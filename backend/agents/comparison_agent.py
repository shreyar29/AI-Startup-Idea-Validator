"""
comparison_agent.py
(Comparison Agent)

Purpose:
Milestone 2 — Comparison & Evaluation Agent.
Synthesizes the analyses into a final startup evaluation including Feature Comparison, Validation Score, Innovation Score, and Recommendations using an LLM.
"""

from __future__ import annotations
import asyncio
import json
import time
import re
from datetime import datetime, timezone
from typing import Any
import logging
from core.config import settings

from utils.error_handler import safe_parse_llm_json, MalformedLLMOutputError

logger = logging.getLogger("comparison_agent")


class ComparisonAnalysisError(Exception):
    """Raised when comparison analysis fails."""


class ComparisonAgent:
    """
    Comparison Agent node in the A2A Mesh Network.
    Pulls data from Market, Customer, and Competitor peers to synthesize.
    """

    def __init__(self, shared_context: dict[str, Any], llm_client=None):
        self.context = shared_context
        self.llm_client = llm_client
        self.peers = {}
        self._analysis_task = None
        self.status = "idle" # States: idle, started, success, failed, timeout

    def connect_peers(self, peers: dict):
        self.peers = peers

    async def get_analysis(self):
        if self._analysis_task is not None:
            if self._analysis_task.done():
                try:
                    self._analysis_task.result()
                    if self.status in ["failed", "timeout"]:
                        logger.warning("ComparisonAgent: Previous task completed in degraded state. Resetting task.")
                        self._analysis_task = None
                except Exception as e:
                    logger.warning(f"ComparisonAgent: Previous task failed with '{e}'. Resetting task.")
                    self._analysis_task = None

        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(self._perform_analysis())
            
        try:
            return await self._analysis_task
        except asyncio.CancelledError:
            logger.warning("ComparisonAgent: Task cancelled. Resetting state.")
            self._analysis_task = None
            self.status = "failed"
            raise
        except Exception:
            raise

    async def _perform_analysis(self):
        self.status = "started"
        start_time = time.perf_counter()
        correlation_id = self.context.get("correlation_id", "N/A")
        log_prefix = f"[{correlation_id}] ComparisonAgent:"
        
        try:
            logger.info(f"{log_prefix} Awaiting payloads from Market, Customer, and Competitor peers concurrently.")
            # Pull data concurrently from peers to reduce latency
            tasks = []
            if "market" in self.peers:
                tasks.append(self.peers["market"].get_analysis())
            if "customer" in self.peers:
                tasks.append(self.peers["customer"].get_analysis())
            if "competitor" in self.peers:
                tasks.append(self.peers["competitor"].get_analysis())
                
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
            logger.info(f"{log_prefix} Successfully received all upstream analytical payloads.")
            result = await self.compare(log_prefix, start_time)
            self.status = "success"
            return result
            
        except asyncio.TimeoutError as e:
            self.status = "timeout"
            logger.error(f"{log_prefix} Timed out: {e}")
            return self._return_fallback("Analysis timed out.", log_prefix)
        except Exception as e:
            self.status = "failed"
            logger.exception(f"{log_prefix} Failed unexpectedly: {e}")
            return self._return_fallback(f"Unexpected failure: {str(e)}", log_prefix)

    def _validate_and_coerce_list(self, val: Any) -> list:
        if not val: return []
        if isinstance(val, list): return [str(v) for v in val if v]
        if isinstance(val, str): return [val]
        return []

    def _dedupe_list(self, raw_list: list) -> list:
        val_list = self._validate_and_coerce_list(raw_list)
        return list(dict.fromkeys(val_list))

    async def compare(self, log_prefix: str = "ComparisonAgent:", start_time: float = None) -> dict[str, Any]:
        """
        Main Comparison Agent entry point.
        """
        if start_time is None:
            start_time = time.perf_counter()
            
        logger.info(f"{log_prefix} Execution started.")

        market = self.context.get("market_analysis", {})
        customer = self.context.get("customer_analysis", {})
        competitor = self.context.get("competitor_analysis", {})
        idea = self.context.get("idea", {})

        available = []
        missing = []
        
        if market and market.get("status") != "failed": available.append("market")
        else: missing.append("market")
        
        if customer and customer.get("status") != "failed": available.append("customer")
        else: missing.append("customer")
        
        if competitor and competitor.get("status") != "failed" and not competitor.get("no_competitor_data_found"): available.append("competitor")
        else: missing.append("competitor")
        
        logger.info(f"{log_prefix} Available inputs: {available}. Missing inputs: {missing}")

        if not available:
            logger.warning(f"{log_prefix} Upstream agents are missing. Synthesizing based on initial idea and search data only.")

        proposed_features = idea.get("proposed_features") or []
        if not proposed_features:
            raw_demand = (customer.get("feature_demand") or [])[:5]
            # Normalize: feature_demand can be list of dicts with 'feature' key or list of strings
            proposed_features = [
                f.get("feature", str(f)) if isinstance(f, dict) else str(f)
                for f in raw_demand if f
            ]
            
        context_payload = {
            "startup_idea": idea.get("description", ""),
            "proposed_features": proposed_features,
            "market_insights": {
                "size": market.get("market_size", "Unknown"),
                "growth": market.get("growth_rate", "Unknown"),
                "trends": (market.get("market_trends") or [])[:3],
                "opportunities": (market.get("opportunities") or [])[:2]
            } if "market" in available else "Missing",
            "customer_insights": {
                "segments": (customer.get("target_customer_segments") or [])[:2],
                "pain_points": (customer.get("pain_points") or [])[:3],
                "feature_demand": (customer.get("feature_demand") or [])[:3]
            } if "customer" in available else "Missing",
            "competitor_insights": [
                {
                    "name": c.get("name"),
                    "features": (c.get("features") or [])[:3],
                    "pricing": c.get("pricing", "Unknown")
                } for c in (competitor.get("competitors") or [])[:3]
            ] if "competitor" in available else "Missing"
        }

        compact_payload = json.dumps(context_payload, separators=(',', ':'))
        
        prompt = (
            f"Evaluate the startup idea using the provided data.\n"
            f"RULES:\n"
            f"1. Calculate 'innovation_score' (0-10) based on uniqueness and tech.\n"
            f"2. Calculate 'validation_score' (0-100) based on demand and feasibility.\n"
            f"3. 'recommendation' MUST be one of: 'Strongly Recommended', 'Recommended', 'Needs Improvement', 'Not Recommended'.\n"
            f"4. 'key_risks' and 'next_steps' MUST be arrays of max 5 strings.\n"
            f"5. 'scoring_breakdown' MUST be an object with string values like '25/30' for 'Market Opportunity', 'Competition', 'Customer Demand', 'Innovation', 'Execution Feasibility' summing to validation_score.\n"
            f"6. 'market_fit' MUST be a detailed executive summary explaining WHY. Include Top strengths, Top weaknesses, Top opportunities, Top risks, and Evidence supporting each. Do not just summarize.\n"
            f"7. Output ONLY valid JSON containing EXACTLY these keys: 'market_fit', 'competitive_advantage', 'innovation_score', 'validation_score', 'scoring_breakdown', 'recommendation', 'key_risks', 'next_steps'.\n\n"
            f"Input Data:\n{compact_payload}"
        )

        payload_size_bytes = len(compact_payload)
        est_tokens = payload_size_bytes // 4
        logger.info(f"{log_prefix} Requesting LLM synthesis for final validation report. Payload size: {payload_size_bytes} bytes (~{est_tokens} tokens).")
        
        parsed_analysis = None
        max_retries = settings.agent.COMPARISON_MAX_RETRIES
        base_backoff = 2
        last_error = None
        llm_start = time.perf_counter()
        
        timeout_seconds = settings.agent.COMPARISON_LLM_TIMEOUT
        
        for attempt in range(max_retries):
            try:
                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt="You are an expert Venture Capital Analyst and Product Strategist. Return ONLY valid JSON.",
                        user_prompt=prompt if attempt == 0 else f"{prompt}\n\nWARNING: Your previous response was invalid JSON. Please fix formatting: {last_error}",
                        response_format={"type": "json_object"}
                    ),
                    timeout=timeout_seconds
                )
                parsed_analysis = safe_parse_llm_json(raw_response)
                logger.info(f"{log_prefix} LLM synthesis successful on attempt {attempt + 1}.")
                break
            except asyncio.TimeoutError:
                logger.error(f"{log_prefix} LLM synthesis timed out after {timeout_seconds}s on attempt {attempt + 1}.")
                last_error = "LLM Timeout"
                break # Break on network timeout, only retry on JSON parsing failures
            except MalformedLLMOutputError as e:
                logger.warning(f"{log_prefix} Malformed JSON output on attempt {attempt + 1}: {e}")
                last_error = str(e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(base_backoff ** attempt)
            except Exception as exc:
                logger.error(f"{log_prefix} LLM synthesis API call failed on attempt {attempt + 1}: {exc}.")
                last_error = str(exc)
                break # Break on network/API errors, only retry on JSON parsing failures

        llm_duration = time.perf_counter() - llm_start
        logger.info(f"{log_prefix} LLM extraction latency: {llm_duration:.2f}s (Attempts: {attempt + 1}/{max_retries})")

        if not parsed_analysis:
            logger.error(f"{log_prefix} Failed to generate valid comparison JSON after {max_retries} attempts. Using fallback.")
            return self._return_fallback(f"LLM failure or malformed JSON: {last_error}", log_prefix)

        logger.info(f"{log_prefix} Validating and structuring final report.")

        competitive_advantage = parsed_analysis.get("competitive_advantage")
        comp_adv_list = [str(competitive_advantage)] if competitive_advantage else []

        market_gaps = self._dedupe_list(parsed_analysis.get("key_risks"))
        next_steps = self._dedupe_list(parsed_analysis.get("next_steps"))
        recommendation_str = str(parsed_analysis.get("recommendation", ""))
        
        recommendations = [recommendation_str] if recommendation_str else []
        recommendations.extend(next_steps)

        try:
            val_score = int(parsed_analysis.get("validation_score", 0))
        except (ValueError, TypeError):
            val_score = 0
            
        try:
            inn_score = int(parsed_analysis.get("innovation_score", 0))
        except (ValueError, TypeError):
            inn_score = 0

        summary = str(parsed_analysis.get("market_fit", "Validation summary could not be generated."))
        scoring_breakdown = parsed_analysis.get("scoring_breakdown") or {}

        if len(available) == 3:
            confidence = "High"
        elif len(available) == 2:
            confidence = "Medium"
        else:
            confidence = "Low"

        # --- FEATURE COMPARISON ENGINE ---
        feature_map = {}
        
        raw_startup_features = []
        raw_startup_features.extend(proposed_features)
        
        cust_demand = customer.get("feature_demand") or []
        for f in cust_demand:
            if isinstance(f, dict):
                raw_startup_features.append(f.get("feature", ""))
            else:
                raw_startup_features.append(str(f))
                
        def normalize_feat(name: str) -> str:
            name = str(name).lower()
            name = re.sub(r'[^\w\s]', ' ', name)
            words = [w for w in name.split() if len(w) > 1 and w not in {'the', 'and', 'with', 'using', 'for', 'to', 'of', 'in', 'a', 'an'}]
            return " ".join(words)
            
        for f in raw_startup_features:
            f_str = str(f).strip()
            if not f_str: continue
            norm = normalize_feat(f_str)
            if not norm or len(norm) < 3: continue
            if norm not in feature_map:
                feature_map[norm] = {"original": f_str[:60].capitalize(), "startup": True, "competitor_set": set()}
            else:
                feature_map[norm]["startup"] = True
                
        comps = competitor.get("competitors") or []
        for c in comps:
            c_name = c.get("name", "Unknown")
            c_feats = []
            if isinstance(c.get("features"), list): c_feats.extend(c.get("features"))
            if isinstance(c.get("strengths"), list): c_feats.extend(c.get("strengths"))
            for f in c_feats:
                if isinstance(f, dict): f = f.get("feature", "") or f.get("name", "")
                f_str = str(f).strip()
                if not f_str: continue
                norm = normalize_feat(f_str)
                if not norm or len(norm) < 3: continue
                if norm not in feature_map:
                    feature_map[norm] = {"original": f_str[:60].capitalize(), "startup": False, "competitor_set": set()}
                feature_map[norm]["competitor_set"].add(c_name)
                
        feature_comparison = []
        unique_count = 0
        common_count = 0
        missing_count = 0
        comp_adv_count = 0
        
        for norm, data in feature_map.items():
            startup_has = data["startup"]
            comp_count = len(data["competitor_set"])
            
            if not startup_has and comp_count > 0:
                coverage = "Gap"
                missing_count += 1
                sort_order = 4
            elif comp_count == 0:
                coverage = "Unique"
                unique_count += 1
                sort_order = 1
            elif comp_count <= 2:
                coverage = "Rare"
                comp_adv_count += 1
                sort_order = 2
            elif comp_count <= 5:
                coverage = "Partial"
                comp_adv_count += 1
                sort_order = 2
            else:
                coverage = "Common"
                common_count += 1
                sort_order = 3
                
            feature_comparison.append({
                "feature": data["original"],
                "startup": startup_has,
                "competitors": comp_count,
                "coverage": coverage,
                "_sort_order": sort_order
            })
            
        feature_comparison.sort(key=lambda x: (x["_sort_order"], -x["competitors"]))
        for fc in feature_comparison:
            fc.pop("_sort_order", None)
            
        feature_summary = {
            "unique_features": unique_count,
            "common_features": common_count,
            "missing_features": missing_count,
            "competitive_advantage": comp_adv_count
        }
        # --- END FEATURE ENGINE ---

        self.status = "success"
        analysis = {
            "feature_comparison": feature_comparison,
            "feature_summary": feature_summary,
            "competitive_advantages": comp_adv_list,
            "market_gaps": market_gaps,
            "validation_score": val_score,
            "innovation_score": inn_score,
            "scoring_breakdown": scoring_breakdown,
            "confidence": confidence,
            "recommendations": recommendations,
            "summary": summary,
            "status": self.status,
            "failure_reason": None,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        stats = {
            "features_compared": len(analysis["feature_comparison"]),
            "advantages_identified": len(comp_adv_list),
            "market_gaps_detected": len(market_gaps),
            "recommendations_generated": len(recommendations),
            "validation_score": val_score,
            "innovation_score": inn_score,
            "confidence": confidence
        }
        logger.info(f"{log_prefix} Processing Stats: {stats}")

        logger.debug(f"--- COMPARISON AGENT COMPLETE PAYLOAD ---")
        logger.debug(json.dumps(analysis, indent=2))
        logger.debug("-----------------------------------------")

        duration = time.perf_counter() - start_time
        logger.info(f"{log_prefix} Successful completion in {duration:.2f}s. Output ready for Orchestrator.")
        self.context["comparison_analysis"] = analysis
        return analysis

    def _return_fallback(self, reason: str, log_prefix: str = "ComparisonAgent:"):
        analysis = {
            "feature_comparison": [],
            "competitive_advantages": [],
            "market_gaps": [],
            "validation_score": 0,
            "innovation_score": 0,
            "scoring_breakdown": {},
            "confidence": "Low",
            "recommendations": [f"Final comparison failed due to {reason}"],
            "summary": f"Startup validation could not be completed. Reason: {reason}",
            "status": self.status,
            "failure_reason": reason,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        self.context["comparison_analysis"] = analysis
        return analysis
