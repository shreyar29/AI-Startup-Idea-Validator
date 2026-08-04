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
import os
import time
from datetime import datetime, timezone
from typing import Any
import logging

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
        start_time = time.time()
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

    async def compare(self, log_prefix: str = "ComparisonAgent:", start_time: float = None) -> dict[str, Any]:
        """
        Main Comparison Agent entry point.
        """
        if start_time is None:
            start_time = time.time()
            
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
            logger.error(f"{log_prefix} Shared Context is completely empty.")
            return self._return_fallback("No upstream analysis data found.", log_prefix)

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
            f"5. Output ONLY valid JSON containing EXACTLY these keys: 'market_fit', 'competitive_advantage', 'innovation_score', 'validation_score', 'recommendation', 'key_risks', 'next_steps'.\n\n"
            f"Input Data:\n{compact_payload}"
        )

        payload_size_bytes = len(compact_payload)
        est_tokens = payload_size_bytes // 4
        logger.info(f"{log_prefix} Requesting LLM synthesis for final validation report. Payload size: {payload_size_bytes} bytes (~{est_tokens} tokens).")
        
        parsed_analysis = None
        max_retries = int(os.getenv("COMPARISON_MAX_RETRIES", "3"))
        last_error = None
        llm_start = time.time()
        timeout_seconds = int(os.getenv("COMPARISON_LLM_TIMEOUT", "45"))
        
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
            except Exception as exc:
                logger.error(f"{log_prefix} LLM synthesis API call failed on attempt {attempt + 1}: {exc}.")
                last_error = str(exc)
                break # Break on network/API errors, only retry on JSON parsing failures

        llm_duration = time.time() - llm_start
        logger.info(f"{log_prefix} LLM extraction latency: {llm_duration:.2f}s (Attempts: {attempt + 1}/{max_retries})")

        if not parsed_analysis:
            logger.error(f"{log_prefix} Failed to generate valid comparison JSON after {max_retries} attempts. Using fallback.")
            return self._return_fallback(f"LLM failure or malformed JSON: {last_error}", log_prefix)

        logger.info(f"{log_prefix} Validating and structuring final report.")

        def dedupe_list(raw_list):
            val_list = self._validate_and_coerce_list(raw_list)
            return list(dict.fromkeys(val_list))

        competitive_advantage = parsed_analysis.get("competitive_advantage")
        comp_adv_list = [str(competitive_advantage)] if competitive_advantage else []

        market_gaps = dedupe_list(parsed_analysis.get("key_risks"))
        next_steps = dedupe_list(parsed_analysis.get("next_steps"))
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

        if len(available) == 3:
            confidence = "High"
        elif len(available) == 2:
            confidence = "Medium"
        else:
            confidence = "Low"

        analysis = {
            "feature_comparison": [],
            "competitive_advantages": comp_adv_list,
            "market_gaps": market_gaps,
            "validation_score": val_score,
            "innovation_score": inn_score,
            "confidence": confidence,
            "recommendations": recommendations,
            "summary": summary,
            "status": self.status,
            "failure_reason": None,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        stats = {
            "features_compared": len(validated_matrix),
            "advantages_identified": len(competitive_advantages),
            "market_gaps_detected": len(market_gaps),
            "recommendations_generated": len(recommendations),
            "validation_score": val_score,
            "innovation_score": inn_score,
            "confidence": confidence
        }
        logger.info(f"{log_prefix} Processing Stats: {stats}")

        logger.info(f"--- COMPARISON AGENT COMPLETE PAYLOAD ---")
        logger.info(json.dumps(analysis, indent=2))
        logger.info("-----------------------------------------")

        duration = time.time() - start_time
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
            "confidence": "Low",
            "recommendations": [f"Final comparison failed due to {reason}"],
            "summary": f"Startup validation could not be completed. Reason: {reason}",
            "status": self.status,
            "failure_reason": reason,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        self.context["comparison_analysis"] = analysis
        return analysis
