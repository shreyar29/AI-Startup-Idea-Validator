"""
swot_agent.py
(SWOT Analysis Agent)

Purpose:
Milestone 3 — Production-grade SWOT Agent.
Evaluates Strengths, Weaknesses, Opportunities, and Threats using evidence 
from Market, Customer, Competitor, and Risk intelligence agents.
"""

import asyncio
import json
import logging
import time
import random
from datetime import datetime, timezone
from typing import Any

from core.config import settings
from utils.error_handler import safe_parse_llm_json, MalformedLLMOutputError

logger = logging.getLogger("swot_agent")

class SWOTAnalysisError(Exception):
    """Raised when SWOT analysis fails."""

class SWOTAgent:
    """
    Analyzes startup SWOT using existing agent outputs.
    Operates as a decentralized node in the A2A Mesh Network.
    """

    def __init__(self, shared_context: dict, llm_client=None):
        self.context = shared_context
        self.llm_client = llm_client
        self.peers = {}
        self._analysis_task = None
        self.status = "idle"

    def connect_peers(self, peers: dict):
        """Connect this agent to other agents in the mesh."""
        self.peers = peers

    async def get_analysis(self):
        """
        Mesh endpoint.
        Runs the analysis once and caches the asyncio task.
        """
        if self._analysis_task is not None:
            if self._analysis_task.done():
                try:
                    self._analysis_task.result()
                    if self.status in ["failed", "timeout"]:
                        self._analysis_task = None
                except Exception:
                    self._analysis_task = None

        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(self._perform_analysis())

        try:
            return await self._analysis_task
        except asyncio.CancelledError:
            logger.warning("SWOTAgent: Task cancelled.")
            self._analysis_task = None
            self.status = "failed"
            raise

    async def _perform_analysis(self):
        """Run the SWOT analysis."""
        self.status = "started"
        start_time = time.time()
        correlation_id = self.context.get("correlation_id", "N/A")
        log_prefix = f"[{correlation_id}] SWOTAgent:"

        try:
            logger.info(f"{log_prefix} Starting SWOT analysis.")

            # Await required peers to prevent race condition
            if self.peers:
                dependencies = []
                for peer_name in ["market", "customer", "competitor", "risk"]:
                    if peer_name in self.peers:
                        dependencies.append(self.peers[peer_name].get_analysis())
                
                if dependencies:
                    await asyncio.gather(*dependencies, return_exceptions=True)

            result = await self.analyze(log_prefix)
            self.status = "success"
            duration = time.time() - start_time
            logger.info(f"{log_prefix} Completed successfully in {duration:.2f}s.")

            return result

        except asyncio.TimeoutError as exc:
            self.status = "timeout"
            logger.error(f"{log_prefix} SWOT analysis timed out: {exc}")
            return self._return_degraded("SWOT analysis timed out.")
        except Exception as exc:
            self.status = "failed"
            logger.exception(f"{log_prefix} SWOT analysis failed: {exc}")
            return self._return_degraded(f"Unexpected failure: {str(exc)}")

    def _return_degraded(self, reason: str):
        """Return a safe response when analysis fails."""
        analysis = {
            "executive_summary": "Analysis could not be completed.",
            "strategic_recommendation": "Address system failures before proceeding.",
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": [],
            "tows_matrix": {"so": [], "wo": [], "st": [], "wt": []},
            "confidence": "Low",
            "failure_reason": reason,
            "status": "degraded" if "Insufficient" in reason else self.status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.context["swot_analysis"] = analysis
        return analysis

    def _get_previous_analysis(self, key: str) -> Any:
        """Safely retrieve another agent's analysis."""
        value = self.context.get(key)
        if isinstance(value, dict):
            return value
        return {}

    def _build_evidence_context(self) -> str:
        """Build a highly optimized context payload from upstream agents."""
        market = self._get_previous_analysis("market_analysis")
        customer = self._get_previous_analysis("customer_analysis")
        competitor = self._get_previous_analysis("competitor_analysis")
        risk = self._get_previous_analysis("risk_analysis")

        idea_data = self.context.get("idea") or {}
        idea = idea_data.get("description") or "Unknown startup idea"

        # Explicitly map upstream insights to their SWOT domain to guide the LLM
        evidence = {
            "startup_idea": idea,
            "market_growth": market.get("growth_rate"),
            "market_opportunities": market.get("opportunities"),
            "customer_pain_points": [p.get("insight") for p in customer.get("pain_points", []) if isinstance(p, dict)],
            "unmet_needs": [n.get("insight") for n in customer.get("unmet_needs", []) if isinstance(n, dict)],
            "competitor_weaknesses": competitor.get("gap_analysis"),
            "competitor_threats": [c.get("name") for c in competitor.get("competitors", []) if c.get("threat_score", 0) > 70],
            "critical_risks": [r.get("risk") for r in risk.get("risks", []) if r.get("severity") in ["High", "Critical"]]
        }
        return json.dumps(evidence, indent=2, default=str)

    def _validate_swot_item(self, item: Any) -> dict | None:
        """Validates and enforces structure for a single SWOT item."""
        if not isinstance(item, dict):
            return None
            
        insight = str(item.get("insight") or "").strip()
        if not insight:
            return None
            
        impact = str(item.get("impact") or "Medium").strip().title()
        if impact not in ["Low", "Medium", "High", "Critical"]:
            impact = "Medium"
            
        raw_evidence = item.get("evidence", [])
        if isinstance(raw_evidence, str):
            evidence = [raw_evidence]
        elif isinstance(raw_evidence, list):
            evidence = [str(e).strip() for e in raw_evidence if e]
        else:
            evidence = []
            
        return {
            "insight": insight,
            "impact": impact,
            "evidence": evidence
        }

    def _validate_tows_item(self, item: Any) -> dict | None:
        """Validates a TOWS matrix action item."""
        if not isinstance(item, dict):
            return None
        action = str(item.get("action") or "").strip()
        if not action:
            return None
        impact = str(item.get("impact") or "Medium").strip().title()
        if impact not in ["Low", "Medium", "High", "Critical"]:
            impact = "Medium"
        return {"action": action, "impact": impact}

    async def analyze(self, log_prefix: str = "SWOTAgent:"):
        """Main SWOT Agent entry point."""
        logger.info(f"{log_prefix} Execution started.")

        if self.llm_client is None:
            return self._return_degraded("LLM client is not available.")
            
        successful_analyses = sum(1 for key in ["market_analysis", "customer_analysis", "competitor_analysis", "risk_analysis"] 
                                if self.context.get(key) and self.context.get(key, {}).get("status") != "failed")
                
        if successful_analyses < 2:
            logger.warning(f"{log_prefix} Insufficient data for SWOT analysis. Found {successful_analyses}/4 upstream outputs.")
            return self._return_degraded("Insufficient data for SWOT analysis")

        evidence_context = self._build_evidence_context()

        prompt = f"""
Analyze the Strengths, Weaknesses, Opportunities, and Threats (SWOT) of the startup using ONLY the provided evidence.

1. Generate Opportunities explicitly from: market growth, customer pain points, and competitor gaps.
2. Generate Threats explicitly from: critical risks, competitor threats, and market maturity.
3. For EVERY item across the four quadrants, provide the exact 'insight', determine its 'impact' (Low, Medium, High, Critical), and cite specific 'evidence' strings from the payload.
4. Generate a TOWS matrix. Provide exactly 2 actionable strategies for each intersection:
   - "so" (Strengths-Opportunities): Use strengths to maximize opportunities.
   - "wo" (Weaknesses-Opportunities): Improve weaknesses by taking advantage of opportunities.
   - "st" (Strengths-Threats): Use strengths to minimize threats.
   - "wt" (Weaknesses-Threats): Defensive strategies to minimize weaknesses and avoid threats.
5. Generate a concise 'executive_summary' synthesizing the overall market position.
6. Generate a 'strategic_recommendation' advising the founders on their immediate next steps.

Do not invent facts that are not supported by the evidence.

Return ONLY valid JSON with exactly this structure:
{{
    "executive_summary": "string",
    "strategic_recommendation": "string",
    "strengths": [
        {{"insight": "string", "impact": "High", "evidence": ["string"]}}
    ],
    "weaknesses": [
        {{"insight": "string", "impact": "Medium", "evidence": ["string"]}}
    ],
    "opportunities": [
        {{"insight": "string", "impact": "High", "evidence": ["string"]}}
    ],
    "threats": [
        {{"insight": "string", "impact": "Critical", "evidence": ["string"]}}
    ],
    "tows_matrix": {{
        "so": [{{"action": "string", "impact": "High"}}],
        "wo": [{{"action": "string", "impact": "Medium"}}],
        "st": [{{"action": "string", "impact": "High"}}],
        "wt": [{{"action": "string", "impact": "High"}}]
    }}
}}

Evidence:
{evidence_context}
"""

        max_retries = getattr(settings.agent, "SWOT_MAX_RETRIES", 3)
        timeout_seconds = getattr(settings.agent, "SWOT_LLM_TIMEOUT", 60)
        parsed_analysis = None
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"{log_prefix} Calling LLM attempt {attempt + 1}/{max_retries}.")
                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt="You are an expert startup business strategist. Return ONLY valid JSON.",
                        user_prompt=(prompt if attempt == 0 else f"{prompt}\n\nFix JSON formatting. Error: {last_error}"),
                        response_format={"type": "json_object"}
                    ),
                    timeout=timeout_seconds
                )
                parsed_analysis = safe_parse_llm_json(raw_response)
                break
            except asyncio.TimeoutError:
                last_error = "LLM Timeout"
                logger.warning(f"{log_prefix} LLM timeout.")
                await asyncio.sleep((2 ** attempt) + random.uniform(0, 1))
            except MalformedLLMOutputError as exc:
                last_error = str(exc)
                logger.warning(f"{log_prefix} Invalid JSON: {exc}")
                await asyncio.sleep((2 ** attempt) + random.uniform(0, 1))
            except Exception as exc:
                last_error = str(exc)
                logger.exception(f"{log_prefix} LLM request failed.")
                await asyncio.sleep((2 ** attempt) + random.uniform(0, 1))

        if not isinstance(parsed_analysis, dict):
            return self._return_degraded(f"LLM extraction failed: {last_error}")

        # Validate and structure quadrants
        quadrants = ["strengths", "weaknesses", "opportunities", "threats"]
        validated_swot = {}
        total_evidence_count = 0
        total_items = 0
        
        impact_weights = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}

        for quad in quadrants:
            items = []
            raw_items = parsed_analysis.get(quad, [])
            if isinstance(raw_items, list):
                for raw_item in raw_items:
                    validated = self._validate_swot_item(raw_item)
                    if validated:
                        items.append(validated)
                        total_items += 1
                        total_evidence_count += len(validated["evidence"])
            
            # Sort items by impact severity
            items.sort(key=lambda x: impact_weights.get(x["impact"], 0), reverse=True)
            validated_swot[quad] = items

        # Validate TOWS matrix
        tows_matrix = {"so": [], "wo": [], "st": [], "wt": []}
        raw_tows = parsed_analysis.get("tows_matrix", {})
        if isinstance(raw_tows, dict):
            for t_quad in ["so", "wo", "st", "wt"]:
                t_items = []
                for t_item in raw_tows.get(t_quad, []):
                    valid_t = self._validate_tows_item(t_item)
                    if valid_t:
                        t_items.append(valid_t)
                t_items.sort(key=lambda x: impact_weights.get(x["impact"], 0), reverse=True)
                tows_matrix[t_quad] = t_items

        # Evidence-Quality Confidence Scoring
        if total_items > 0:
            evidence_ratio = total_evidence_count / total_items
            if evidence_ratio >= 1.5:
                confidence = "High"
            elif evidence_ratio >= 0.8:
                confidence = "Medium"
            else:
                confidence = "Low"
        else:
            confidence = "Low"

        executive_summary = str(parsed_analysis.get("executive_summary") or "Strategic overview unavailable.").strip()
        strategic_recommendation = str(parsed_analysis.get("strategic_recommendation") or "Review individual SWOT quadrants for next steps.").strip()

        analysis = {
            "executive_summary": executive_summary,
            "strategic_recommendation": strategic_recommendation,
            "strengths": validated_swot["strengths"],
            "weaknesses": validated_swot["weaknesses"],
            "opportunities": validated_swot["opportunities"],
            "threats": validated_swot["threats"],
            "tows_matrix": tows_matrix,
            "confidence": confidence,
            "failure_reason": None,
            "status": "success",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        self.context["swot_analysis"] = analysis

        logger.info(
            f"{log_prefix} SWOT Analysis Complete. "
            f"S:{len(validated_swot['strengths'])} W:{len(validated_swot['weaknesses'])} "
            f"O:{len(validated_swot['opportunities'])} T:{len(validated_swot['threats'])} "
            f"| Confidence: {confidence}"
        )

        return analysis