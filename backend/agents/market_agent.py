"""
market_agent.py
(Market Agent)

Purpose:
Milestone 2 — Market Opportunity Agent.
Synthesizes raw search results into structured market insights (market size, growth rate, trends, opportunities, challenges) using an LLM.
"""

import asyncio
import logging
import json
import time
import os
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict

from utils.error_handler import safe_parse_llm_json, MalformedLLMOutputError

logger = logging.getLogger("market_agent")

class MarketAnalysisError(Exception):
    """Raised when market analysis fails."""

class MarketOpportunityAgent:
    """
    Analyzes the market for a startup idea using research data.
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
        """
        if self._analysis_task is not None:
            if self._analysis_task.done():
                try:
                    self._analysis_task.result()
                    if self.status in ["failed", "timeout"]:
                        logger.warning("MarketOpportunityAgent: Previous task completed in degraded state. Resetting task.")
                        self._analysis_task = None
                except Exception as e:
                    logger.warning(f"MarketOpportunityAgent: Previous task failed with '{e}'. Resetting task.")
                    self._analysis_task = None

        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(self._perform_analysis())
            
        try:
            return await self._analysis_task
        except asyncio.CancelledError:
            logger.warning("MarketOpportunityAgent: Task cancelled. Resetting state.")
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
        log_prefix = f"[{correlation_id}] MarketAgent:"
        
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
            return self._return_degraded("Analysis timed out.", "Low", log_prefix)
        except Exception as e:
            self.status = "failed"
            duration = time.time() - start_time
            logger.exception(f"{log_prefix} Failed unexpectedly after {duration:.2f}s: {e}")
            return self._return_degraded(f"Unexpected failure: {str(e)}", "Low", log_prefix)

    def _validate_and_coerce_list(self, val: Any) -> list:
        """Helper to ensure a value is strictly a list of strings."""
        if not val:
            return []
        if isinstance(val, list):
            return [str(v) for v in val if v]
        if isinstance(val, str):
            return [val]
        return []

    def _return_degraded(self, reason: str, confidence: str, log_prefix: str = "MarketAgent:"):
        analysis = {
            "market_size": "Data unavailable",
            "growth_rate": "Data unavailable",
            "market_maturity": "Data unavailable",
            "market_segmentation": [],
            "growth_drivers": [],
            "market_trends": [],
            "opportunities": [],
            "challenges": [],
            "industry_insights": [],
            "market_summary": f"Analysis could not be completed: {reason}",
            "confidence_score": confidence,
            "status": self.status,
            "failure_reason": reason,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        self.context["market_analysis"] = analysis
        return analysis

    async def analyze(self, log_prefix: str = "MarketAgent:"):
        """
        Main entry point. Uses LLM to parse raw market snippets.
        Populates and returns shared_context["market_analysis"].
        """
        logger.info(f"{log_prefix} Execution started.")
        
        research = self.context.get("research") or {}
        if "search_results" in research and isinstance(research["search_results"], dict):
            research = research["search_results"]
            
        idea_data = self.context.get("idea") or {}
        idea = idea_data.get("description", "Unknown startup idea")

        max_snippets = int(os.getenv("MARKET_MAX_SNIPPETS", "4"))
        max_snippet_length = int(os.getenv("MARKET_MAX_SNIPPET_LENGTH", "500"))
        auth_domains = [
            "gartner.", "statista.", "mckinsey.", "grandviewresearch.", ".gov", ".edu", "forrester.", "idc.", "bloomberg.",
            "grandviewresearch.com", "mordorintelligence.com", "imarcgroup.com", "fortunebusinessinsights.com",
            "marketresearchfuture.com", "snsinsider.com", "globenewswire.com", "businesswire.com"
        ]
        priority_categories = ["market", "growth", "forecast", "industry", "trend"]

        snippets = []
        seen_hashes = set()

        for cat, results in research.items():
            if not isinstance(results, list):
                continue
                
            cat_lower = cat.lower()
            if not any(p in cat_lower for p in priority_categories):
                continue
                
            for r in results:
                content = str(r.get("content") or "").strip()
                url = str(r.get("url") or "").strip()
                relevance = r.get("relevance_score", 0)
                
                if not content or not url:
                    continue
                    
                snippet_hash = hashlib.sha256(content[:250].lower().encode('utf-8')).hexdigest()
                if snippet_hash not in seen_hashes:
                    seen_hashes.add(snippet_hash)
                    
                    # Boost authority
                    is_authoritative = any(d in url.lower() for d in auth_domains)
                    score = relevance + (5 if is_authoritative else 0)
                    
                    snippets.append({
                        "category": cat,
                        "url": url,
                        "content": content,
                        "score": score,
                        "length": len(content)
                    })

        if not snippets:
            logger.warning(f"{log_prefix} No market-related research data found. Degrading gracefully.")
            return self._return_degraded("No valid market research snippets found.", "Low", log_prefix)
            
        logger.info(f"{log_prefix} Consolidated {len(snippets)} unique snippets for analysis.")
        
        snippets.sort(key=lambda x: (x["score"], x["length"]), reverse=True)
        top_snippets = snippets[:max_snippets]
        
        def generate_prompt(snippet_list):
            evidence_text = ""
            for i, s in enumerate(snippet_list, 1):
                evidence_text += f"Source {i}\nCategory: {s['category']}\nURL: {s['url']}\nContent: {s['content'][:max_snippet_length]}\n\n"

            p = (
                f"Extract facts for startup idea: '{idea}'.\n"
                f"RULES:\n"
                f"1. Extract ONLY: market_size, growth_rate, market_maturity, and market_trends.\n"
                f"2. Use ONLY explicit facts from evidence. Do NOT explain or reason.\n"
                f"3. If unavailable, return 'Unknown'.\n\n"
                f"Output strictly as a JSON object containing exactly these keys:\n"
                f"- 'market_size' (string)\n"
                f"- 'growth_rate' (string)\n"
                f"- 'market_maturity' (string)\n"
                f"- 'market_trends' (list of strings)\n\n"
                f"Evidence:\n{evidence_text}"
            )
            return p, len(evidence_text)

        prompt, payload_size_bytes = generate_prompt(top_snippets)
        logger.info(f"{log_prefix} Prepared LLM extraction. Snippets selected: {len(top_snippets)}, Content length: {payload_size_bytes} chars.")

        parsed_analysis = None
        max_retries = int(os.getenv("MARKET_MAX_RETRIES", "1"))
        last_error = None
        timeout_seconds = int(os.getenv("MARKET_LLM_TIMEOUT", "20"))
        llm_start = time.time()
        
        for attempt in range(max_retries + 1):
            try:
                req_start = time.time()
                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt="You are an expert Market Research Consultant. Return ONLY valid JSON.",
                        user_prompt=prompt
                    ),
                    timeout=timeout_seconds
                )
                
                if not raw_response or not isinstance(raw_response, str) or not raw_response.strip():
                    raise ValueError("Invalid LLM response: expected a non-empty string.")
                    
                logger.debug(f"{log_prefix} Raw LLM response (first 300 chars): {raw_response[:300]}")
                
                parse_start = time.time()
                parsed_analysis = safe_parse_llm_json(raw_response)
                parse_duration = time.time() - parse_start
                req_duration = time.time() - req_start
                
                logger.info(
                    f"{log_prefix} Extraction successful on attempt {attempt + 1}. "
                    f"Sent Chars: {payload_size_bytes}, "
                    f"Req Time: {req_duration:.2f}s, Parse Time: {parse_duration:.2f}s."
                )
                break
            except asyncio.TimeoutError:
                logger.warning(f"{log_prefix} LLM timeout on attempt {attempt + 1} after {timeout_seconds}s.")
                last_error = "LLM Timeout"
                
                # Timeout recovery: halve the context and retry immediately if this was the first attempt
                if attempt == 0 and len(top_snippets) > 2:
                    logger.info(f"{log_prefix} Retrying with top 2 snippets to reduce context and latency.")
                    top_snippets = top_snippets[:2]
                    prompt, payload_size_bytes = generate_prompt(top_snippets)
                    
            except MalformedLLMOutputError as e:
                logger.warning(f"{log_prefix} Malformed JSON output on attempt {attempt + 1}: {e}")
                last_error = str(e)
            except ValueError as e:
                logger.warning(f"{log_prefix} Validation error on attempt {attempt + 1}: {e}")
                last_error = str(e)
            except Exception as exc:
                logger.error(f"{log_prefix} API call failed on attempt {attempt + 1}: {exc}")
                last_error = str(exc)
                break 

        total_duration = time.time() - llm_start
        logger.info(f"{log_prefix} Total LLM execution time: {total_duration:.2f}s")

        if not parsed_analysis or not isinstance(parsed_analysis, dict):
            logger.error(f"{log_prefix} All retries failed or invalid format. Last error: {last_error}. Degrading gracefully.")
            return self._return_degraded(f"LLM extraction failed: {last_error}", "Low", log_prefix)

        logger.info(f"{log_prefix} Validating and structuring response generation.")

        # Clean duplicates from lists
        def dedupe_list(raw_list):
            val_list = self._validate_and_coerce_list(raw_list)
            return list(dict.fromkeys(val_list)) # preserves order, removes duplicates

        def get_field(data, key, default="Unknown"):
            val = data.get(key)
            if not val or val == "Data unavailable":
                return default
            return str(val)

        market_size = get_field(parsed_analysis, "market_size")
        growth_rate = get_field(parsed_analysis, "growth_rate")
        market_maturity = get_field(parsed_analysis, "market_maturity")
        market_trends = dedupe_list(parsed_analysis.get("market_trends"))

        trends_str = ", ".join(market_trends[:3]) if market_trends else "none identified"
        market_summary = f"The market appears to be growing with a CAGR of {growth_rate}. The identified maturity level is {market_maturity}. Key trends include {trends_str}."

        opportunities = []
        challenges = []
        market_segmentation = []
        growth_drivers = []
        industry_insights = []

        # Calculate confidence score logically to save LLM tokens
        unknowns = sum(1 for v in [market_size, growth_rate, market_maturity] if v == "Unknown")
        if not market_trends:
            unknowns += 1
            
        if unknowns == 0:
            confidence = "High"
        elif unknowns <= 2:
            confidence = "Medium"
        else:
            confidence = "Low"

        # Ensure all required keys exist and enforce rigid typing to prevent downstream crashes
        analysis = {
            "market_size": market_size,
            "growth_rate": growth_rate,
            "market_maturity": market_maturity,
            "market_segmentation": market_segmentation,
            "growth_drivers": growth_drivers,
            "market_trends": market_trends,
            "opportunities": opportunities,
            "challenges": challenges,
            "industry_insights": industry_insights,
            "market_summary": market_summary,
            "confidence_score": confidence,
            "status": self.status,
            "failure_reason": None,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        stats = {
            "trends_extracted": len(market_trends),
            "opportunities_extracted": len(opportunities),
            "challenges_extracted": len(challenges),
            "confidence": confidence
        }
        logger.info(f"{log_prefix} Processing Stats: {stats}")

        logger.info(f"--- MARKET AGENT COMPLETE PAYLOAD ---")
        logger.info(json.dumps(analysis, indent=2))
        logger.info("-------------------------------------")

        logger.info(f"{log_prefix} Successful completion. Output ready for downstream agents.")
        self.context["market_analysis"] = analysis
        return analysis


