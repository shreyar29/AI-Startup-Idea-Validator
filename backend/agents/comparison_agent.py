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

    def connect_peers(self, peers: dict):
        self.peers = peers

    async def get_analysis(self):
        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(self._perform_analysis())
        return await self._analysis_task

    async def _perform_analysis(self):
        logger.info("ComparisonAgent: Awaiting payloads from Market, Customer, and Competitor peers.")
        # Pull data dynamically from peers if available sequentially to prevent HTTP 429 Rate Limits
        if "market" in self.peers:
            await self.peers["market"].get_analysis()
        if "customer" in self.peers:
            await self.peers["customer"].get_analysis()
        if "competitor" in self.peers:
            await self.peers["competitor"].get_analysis()
            
        logger.info("ComparisonAgent: Successfully received all upstream analytical payloads.")
        result = await self.compare()
        return result

    def _validate_and_coerce_list(self, val: Any) -> list:
        if not val: return []
        if isinstance(val, list): return [str(v) for v in val if v]
        if isinstance(val, str): return [val]
        return []

    async def compare(self) -> dict[str, Any]:
        """
        Main Comparison Agent entry point.
        """
        logger.info("ComparisonAgent: Execution started.")

        market = self.context.get("market_analysis", {})
        customer = self.context.get("customer_analysis", {})
        competitor = self.context.get("competitor_analysis", {})
        idea = self.context.get("idea", {})

        if not (market or customer or competitor):
            logger.error("ComparisonAgent: Shared Context is completely empty.")
            return self._return_fallback("No upstream analysis data found.")

        # Serialize the context slightly to avoid token limit explosions, but keep critical data
        context_payload = {
            "startup_idea": idea.get("description", ""),
            "proposed_features": idea.get("proposed_features", []),
            "market_insights": {
                "size": market.get("market_size"),
                "growth": market.get("growth_rate"),
                "trends": market.get("market_trends"),
                "opportunities": market.get("opportunities")
            },
            "customer_insights": {
                "segments": customer.get("target_customer_segments"),
                "pain_points": customer.get("pain_points"),
                "sentiment": customer.get("sentiment"),
                "feature_demand": customer.get("feature_demand")
            },
            "competitor_insights": [
                {
                    "name": c.get("name"),
                    "features": c.get("features"),
                    "pricing": c.get("pricing"),
                    "strengths": c.get("strengths")
                } for c in competitor.get("competitors", [])
            ]
        }

        prompt = (
            f"You are the Lead Startup Validator. Synthesize the following analyses into a final comprehensive report.\n"
            f"Input Data:\n{json.dumps(context_payload, indent=2)}\n\n"
            f"Output strictly as a JSON object with exactly these keys:\n"
            f"- 'feature_matrix' (list of objects: {{'feature': string, 'startup': true, 'competitors': [{{'name': string, 'available': boolean}}] }})\n"
            f"- 'competitive_advantages' (list of strings, dynamically deduced)\n"
            f"- 'market_gaps' (list of strings, dynamically deduced)\n"
            f"- 'validation_score' (integer 0-100, holistic score based on the data)\n"
            f"- 'innovation_score' (integer 0-100, holistic score based on gaps/features)\n"
            f"- 'confidence' (string: 'High', 'Medium', or 'Low' based on data density)\n"
            f"- 'recommendations' (list of actionable string recommendations)\n"
            f"- 'summary' (string paragraph synthesizing the final verdict)\n\n"
            f"IMPORTANT: You MUST return ONLY valid JSON. No markdown blocks, no explanatory text. Ensure all brackets are closed.\n"
        )

        logger.info("ComparisonAgent: Requesting LLM synthesis for final validation report.")
        
        parsed_analysis = None
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                raw_response = await self.llm_client.generate_response(
                    system_prompt="You are an expert startup validator. Return ONLY valid JSON.",
                    user_prompt=prompt if attempt == 0 else f"{prompt}\n\nWARNING: Your previous response was invalid JSON. Please fix formatting: {last_error}",
                    response_format={"type": "json_object"}
                )
                parsed_analysis = safe_parse_llm_json(raw_response)
                logger.info(f"ComparisonAgent: LLM synthesis successful on attempt {attempt + 1}.")
                break
            except MalformedLLMOutputError as e:
                logger.warning(f"ComparisonAgent: Malformed JSON output on attempt {attempt + 1}: {e}")
                last_error = str(e)
            except Exception as exc:
                logger.error(f"ComparisonAgent: LLM synthesis API call failed on attempt {attempt + 1}: {exc}.")
                last_error = str(exc)
                break # Break on network/API errors, only retry on JSON parsing failures

        if not parsed_analysis:
            logger.error(f"ComparisonAgent: Failed to generate valid comparison JSON after {max_retries} attempts. Using fallback.")
            return self._return_fallback(f"LLM failure or malformed JSON: {last_error}")

        logger.info("ComparisonAgent: Validating and structuring final report.")

        try:
            val_score = int(parsed_analysis.get("validation_score", 0))
        except (ValueError, TypeError):
            val_score = 0
            
        try:
            inn_score = int(parsed_analysis.get("innovation_score", 0))
        except (ValueError, TypeError):
            inn_score = 0

        # Type checking for feature_matrix
        raw_matrix = parsed_analysis.get("feature_matrix")
        validated_matrix = []
        if isinstance(raw_matrix, list):
            for row in raw_matrix:
                if isinstance(row, dict):
                    comps = row.get("competitors", [])
                    val_comps = []
                    if isinstance(comps, list):
                        for c in comps:
                            if isinstance(c, dict):
                                name = str(c.get("name") or "")
                                if name and name.lower() not in ["unknown", "n/a", "none"]:
                                    val_comps.append({
                                        "name": name,
                                        "available": bool(c.get("available"))
                                    })
                    validated_matrix.append({
                        "feature": str(row.get("feature") or "Unknown Feature"),
                        "startup": True,
                        "competitors": val_comps
                    })

        analysis = {
            "feature_matrix": validated_matrix,
            "competitive_advantages": self._validate_and_coerce_list(parsed_analysis.get("competitive_advantages")),
            "market_gaps": self._validate_and_coerce_list(parsed_analysis.get("market_gaps")),
            "validation_score": val_score,
            "innovation_score": inn_score,
            "confidence": str(parsed_analysis.get("confidence") or "Low"),
            "recommendations": self._validate_and_coerce_list(parsed_analysis.get("recommendations")),
            "summary": str(parsed_analysis.get("summary") or "Validation summary could not be generated."),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"--- COMPARISON AGENT COMPLETE PAYLOAD ---")
        logger.info(json.dumps(analysis, indent=2))
        logger.info("-----------------------------------------")

        logger.info("ComparisonAgent: Successful completion. Output ready for Orchestrator.")
        self.context["comparison_analysis"] = analysis
        return analysis

    def _return_fallback(self, reason: str):
        analysis = {
            "feature_matrix": [],
            "competitive_advantages": [],
            "market_gaps": [],
            "validation_score": 0,
            "innovation_score": 0,
            "confidence": "Low",
            "recommendations": [f"Final comparison failed due to {reason}"],
            "summary": f"Startup validation could not be completed. Reason: {reason}",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        self.context["comparison_analysis"] = analysis
        return analysis
