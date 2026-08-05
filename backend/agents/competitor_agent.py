"""
competitor_agent.py
(Competitor Agent)

Purpose:
Milestone 2 — Competitor Discovery & Comparison Agent.
Identifies existing competitors, compares their offerings, and highlights
market gaps for the startup idea being validated using LLM inference over raw search data.
"""

import asyncio
import logging
import json
import time
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List
from core.config import settings
from utils.error_handler import safe_parse_llm_json, MalformedLLMOutputError

logger = logging.getLogger("competitor_agent")

class CompetitorAnalysisError(Exception):
    """Raised when competitor analysis fails."""

class CompetitorAgent:
    """
    Analyzes competitor landscape for a startup idea using research data.
    Operates as a decentralized node in the A2A Mesh Network.
    """

    def __init__(self, shared_context: dict, llm_client=None):
        self.context = shared_context
        self.llm_client = llm_client
        self.peers = {}
        self._analysis_task = None
        self.status = "idle" # States: idle, started, success, failed, timeout

    def connect_peers(self, peers: dict):
        """Connects this agent to all other agents in the mesh."""
        self.peers = peers

    async def get_analysis(self):
        """
        Mesh Network endpoint. Returns the analysis, computing it
        only once and caching the result as an asyncio Task.
        Implements proper lifecycle resets on failure/timeout.
        """
        if self._analysis_task is not None:
            if self._analysis_task.done():
                try:
                    self._analysis_task.result()
                    # Task completed without throwing, but if it was degraded, reset it for future-proofing
                    if self.status in ["failed", "timeout"]:
                        logger.warning("CompetitorAgent: Previous task completed in degraded state. Resetting task.")
                        self._analysis_task = None
                except Exception as e:
                    logger.warning(f"CompetitorAgent: Previous task failed with '{e}'. Resetting task.")
                    self._analysis_task = None

        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(self._perform_analysis())
            
        try:
            return await self._analysis_task
        except asyncio.CancelledError:
            logger.warning("CompetitorAgent: Task cancelled. Resetting state.")
            self._analysis_task = None
            self.status = "failed"
            raise
        except Exception:
            raise

    async def _perform_analysis(self):
        """Pulls required data from peers and runs the analysis."""
        self.status = "started"
        start_time = time.time()
        correlation_id = self.context.get("correlation_id", "N/A")
        log_prefix = f"[{correlation_id}] CompetitorAgent:"
        
        try:
            logger.info(f"{log_prefix} Awaiting research payload from Web Search Agent.")
            if "web_search" in self.peers:
                research_data = await self.peers["web_search"].get_analysis()
                self.context["research"] = research_data
                logger.info(f"{log_prefix} Successfully received research payload.")
                
            result = await self.analyze(log_prefix)
            self.status = "success"
            
            duration = time.time() - start_time
            logger.info(f"{log_prefix} Completed successfully in {duration:.2f}s.")
            return result
            
        except asyncio.TimeoutError as e:
            self.status = "timeout"
            duration = time.time() - start_time
            logger.error(f"{log_prefix} Timed out after {duration:.2f}s: {e}")
            return self._return_degraded("Analysis timed out.", "Low")
        except Exception as e:
            self.status = "failed"
            duration = time.time() - start_time
            logger.exception(f"{log_prefix} Failed unexpectedly after {duration:.2f}s: {e}")
            return self._return_degraded(f"Unexpected failure: {str(e)}", "Low")

    def _validate_and_coerce_list(self, val: Any) -> list:
        """Helper to ensure a value is strictly a list of strings."""
        if not val:
            return []
        if isinstance(val, list):
            return [str(v) for v in val if v]
        if isinstance(val, str):
            return [val]
        return []

    def _return_degraded(self, reason: str, confidence: str):
        analysis = {
            "competitors": [],
            "gap_analysis": [f"Analysis could not be completed: {reason}"],
            "confidence": confidence,
            "no_competitor_data_found": True,
            "failure_reason": reason,
            "status": self.status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.context["competitor_analysis"] = analysis
        return analysis

    async def analyze(self, log_prefix: str = "CompetitorAgent:"):
        """
        Main entry point. Populates and returns shared_context["competitor_analysis"].
        """
        logger.info(f"{log_prefix} Execution started.")
        
        research = self.context.get("research") or {}
        if "search_results" in research and isinstance(research["search_results"], dict):
            research = research["search_results"]
            
        idea_data = self.context.get("idea") or {}
        idea = idea_data.get("description", "Unknown startup idea")

        competitor_snippets = []
        seen_hashes = set()
        
        # Configuration Limits
        max_snippets = settings.agent.COMPETITOR_MAX_SNIPPETS
        max_snippet_length = settings.agent.COMPETITOR_MAX_SNIPPET_LENGTH
        
        priority_categories = ["competitor", "alternatives", "products", "business", "startup"]
        
        # Dynamically consume all categories from web search
        for cat, results in research.items():
            if not any(p in cat.lower() for p in priority_categories):
                continue
            if isinstance(results, list):
                for r in results:
                    content = str(r.get("content") or "").strip()
                    url = str(r.get("url") or "").strip()
                    title = str(r.get("title") or "").strip()
                    relevance = r.get("relevance_score", 0)
                    
                    if not content or not url:
                        continue
                        
                    # Deterministic semantic duplicate detection using content hash prefix
                    snippet_hash = hashlib.sha256(content[:250].lower().encode('utf-8')).hexdigest()
                    if snippet_hash not in seen_hashes:
                        seen_hashes.add(snippet_hash)
                        competitor_snippets.append({
                            "url": url,
                            "title": title,
                            "content": content,
                            "relevance": relevance,
                            "length": len(content)
                        })

        if not competitor_snippets:
            logger.warning(f"{log_prefix} No research data snippets found. Degrading gracefully.")
            return self._return_degraded("No valid research snippets found in context.", "Medium")
            
        logger.info(f"{log_prefix} Consolidated {len(competitor_snippets)} unique snippets.")

        # Optimize snippet selection: sort by relevance and length, take top N
        competitor_snippets.sort(key=lambda x: (x["relevance"], x["length"]), reverse=True)
        top_snippets = competitor_snippets[:max_snippets]
        
        def generate_prompt(snippets_list):
            raw_text_parts = []
            for s in snippets_list:
                raw_text_parts.append(f"Source: {s['url']} | Title: {s['title']}\nContent: {s['content'][:max_snippet_length]}")
            raw_text = "\n\n".join(raw_text_parts)
            
            p = (
                f"Extract competitor facts for startup idea: '{idea}'.\n"
                f"RULES:\n"
                f"1. Extract ONLY competitor name, features, pricing, and source URLs.\n"
                f"2. Use ONLY explicit facts from evidence. Do NOT explain or reason.\n"
                f"3. If unavailable, return 'Unknown'.\n\n"
                f"Output strictly as a JSON object containing exactly these keys:\n"
                f"- 'competitors': an array of objects. Each object MUST have:\n"
                f"  - 'name' (string)\n"
                f"  - 'features' (list of strings)\n"
                f"  - 'pricing' (string)\n"
                f"  - 'source_references' (list of strings)\n\n"
                f"Evidence:\n{raw_text}\n"
            )
            return p, raw_text

        prompt, raw_text = generate_prompt(top_snippets)

        est_tokens = len(raw_text) // 4
        logger.info(f"{log_prefix} Requesting LLM extraction. Snippets: {len(top_snippets)}, Context Size: {len(raw_text)} chars (~{est_tokens} tokens).")
        
        parsed_analysis = None
        max_retries = settings.agent.COMPETITOR_MAX_RETRIES
        base_backoff = 2
        last_error = None
        llm_start = time.time()
        timeout_seconds = settings.agent.COMPETITOR_LLM_TIMEOUT
        
        for attempt in range(max_retries):
            try:
                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt="You are an expert competitive intelligence specialist. Return ONLY valid JSON.",
                        user_prompt=prompt if attempt == 0 else f"{prompt}\n\nWARNING: Your previous response was invalid JSON. Please fix formatting: {last_error}"
                    ),
                    timeout=timeout_seconds
                )
                parsed_analysis = safe_parse_llm_json(raw_response)
                logger.info(f"{log_prefix} LLM data extraction successful on attempt {attempt + 1}.")
                break
            except asyncio.TimeoutError:
                logger.error(f"{log_prefix} LLM timeout on attempt {attempt + 1} after {timeout_seconds}s.")
                last_error = "LLM Timeout"
                if attempt == 0 and len(top_snippets) > 2:
                    logger.info(f"{log_prefix} Retrying with top 2 snippets to reduce context.")
                    top_snippets = top_snippets[:2]
                    prompt, _ = generate_prompt(top_snippets)
                else:
                    break
            except MalformedLLMOutputError as e:
                logger.warning(f"{log_prefix} Malformed JSON output on attempt {attempt + 1}: {e}")
                last_error = str(e)
            except Exception as exc:
                logger.error(f"{log_prefix} LLM analysis API call failed on attempt {attempt + 1}: {exc}.")
                last_error = str(exc)
                break 

        llm_duration = time.time() - llm_start
        logger.info(f"{log_prefix} LLM extraction latency: {llm_duration:.2f}s (Attempts: {attempt + 1}/{max_retries})")

        if not parsed_analysis or not isinstance(parsed_analysis, dict):
            logger.error(f"{log_prefix} All retries failed or invalid format. Last error: {last_error}. Degrading gracefully.")
            return self._return_degraded(f"LLM extraction failed: {last_error}", "Low")

        logger.info(f"{log_prefix} Validating and structuring response generation.")

        raw_competitors = parsed_analysis.get("competitors")
        if not isinstance(raw_competitors, list):
            raw_competitors = []
            
        validated_competitors = []
        competitor_map = {}
        
        comps_discovered = len(raw_competitors)
        comps_rejected = 0
        comps_merged = 0
        
        for comp in raw_competitors:
            if not isinstance(comp, dict):
                comps_rejected += 1
                continue
            name = str(comp.get("name") or "").strip()
            
            # Eliminate generic/unknown outputs
            if not name or name.lower() in ["unknown competitor", "unknown", "n/a", "none"]:
                comps_rejected += 1
                continue
                
            name_lower = name.lower()
            if name_lower in competitor_map:
                # Merge duplicate
                existing = competitor_map[name_lower]
                existing["features"] = list(set(existing["features"] + self._validate_and_coerce_list(comp.get("features"))))
                existing["source_references"] = list(set(existing["source_references"] + self._validate_and_coerce_list(comp.get("source_references"))))
                if existing["pricing"] in ["Pricing unavailable", "Unavailable", "Unknown"] and comp.get("pricing") not in [None, "Pricing unavailable", "Unavailable", "Unknown"]:
                    existing["pricing"] = str(comp.get("pricing"))
                comps_merged += 1
                continue
                
            features = self._validate_and_coerce_list(comp.get("features"))
            source_references = self._validate_and_coerce_list(comp.get("source_references"))
            pricing = str(comp.get("pricing") or "Unknown")
            
            # Generate summary in Python
            summary = f"Provides {', '.join(features[:3])}." if features else "Product details unknown."
            
            # Confidence for this competitor (used for overall confidence calculation later)
            has_sources = len(source_references) > 0
            comp_confidence = "High" if has_sources else "Medium"
            
            # Create new competitor with required schema
            valid_comp = {
                "name": name,
                "product_summary": summary,
                "features": features,
                "pricing": pricing,
                "business_model": "Unavailable",
                "market_positioning": "Unknown",
                "target_customers": "Unavailable",
                "strengths": [],
                "weaknesses": [],
                "source_references": source_references,
                "confidence_score": comp_confidence
            }
            competitor_map[name_lower] = valid_comp
            validated_competitors.append(valid_comp)
        
        logger.info(f"{log_prefix} Processing Stats: Discovered={comps_discovered}, Rejected={comps_rejected}, Merged={comps_merged}, Final Valid={len(validated_competitors)}")

        # Gap analysis generated entirely in Python
        raw_gap_analysis = self._generate_gap_analysis(validated_competitors)

        # Calculate confidence score logically to save LLM tokens
        if not validated_competitors:
            overall_confidence = "Low"
        else:
            all_have_sources = all(c["source_references"] for c in validated_competitors)
            missing_fields = sum(1 for c in validated_competitors if not c["features"] or c["pricing"] in ["Unknown", "Unavailable"])
            
            if all_have_sources and missing_fields == 0:
                overall_confidence = "High"
            elif missing_fields <= 2:
                overall_confidence = "Medium"
            else:
                overall_confidence = "Low"

        self.status = "success"
        analysis = {
            "competitors": validated_competitors,
            "gap_analysis": self._validate_and_coerce_list(raw_gap_analysis),
            "confidence": overall_confidence,
            "no_competitor_data_found": len(validated_competitors) == 0,
            "failure_reason": None,
            "status": self.status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"--- COMPETITOR AGENT COMPLETE PAYLOAD ---")
        logger.info(json.dumps(analysis, indent=2))
        logger.info("-----------------------------------------")

        logger.info("CompetitorAgent: Successful completion. Output ready for downstream agents.")
        self.context["competitor_analysis"] = analysis
        return analysis

    def _generate_gap_analysis(self, competitors: list) -> list:
        if not competitors:
            return ["No competitor data available for gap analysis."]
        
        all_features = {}
        for c in competitors:
            for f in c.get("features", []):
                feat = str(f).lower().strip()
                all_features[feat] = all_features.get(feat, 0) + 1
                
        if not all_features:
            return ["No competitor features found to identify gaps."]
            
        common_features = [f for f, count in all_features.items() if count > len(competitors) // 2]
        rare_features = [f for f, count in all_features.items() if count <= len(competitors) // 2]
        
        gaps = []
        if common_features:
            gaps.append(f"Most competitors focus on: {', '.join(common_features[:3])}.")
        if rare_features:
            gaps.append(f"Few competitors provide: {', '.join(rare_features[:3])}.")
            
        return gaps if gaps else ["No distinct feature gaps identified."]