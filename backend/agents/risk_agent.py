"""
risk_agent.py
(Risk Analysis Agent)

Purpose:
Milestone 3 — Risk Analysis Agent.
Evaluates market, competitive, customer, feasibility, business,
and AI/LLM risks using evidence from existing analysis agents.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any
import random

from core.config import settings
from utils.error_handler import safe_parse_llm_json, MalformedLLMOutputError

logger = logging.getLogger("risk_agent")

class RiskAnalysisError(Exception):
    """Raised when risk analysis fails."""

class RiskAgent:
    """
    Analyzes startup risks using existing agent outputs.
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
            logger.warning("RiskAgent: Task cancelled.")
            self._analysis_task = None
            self.status = "failed"
            raise

    async def _perform_analysis(self):
        """Run the risk analysis."""
        self.status = "started"
        start_time = time.time()
        correlation_id = self.context.get("correlation_id", "N/A")
        log_prefix = f"[{correlation_id}] RiskAgent:"

        try:
            logger.info(f"{log_prefix} Starting risk analysis.")

            # 1. Await required peers to prevent race condition
            if self.peers:
                dependencies = []
                for peer_name in ["market", "customer", "competitor"]:
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
            logger.error(f"{log_prefix} Risk analysis timed out: {exc}")
            return self._return_degraded("Risk analysis timed out.", "Low")
        except Exception as exc:
            self.status = "failed"
            logger.exception(f"{log_prefix} Risk analysis failed: {exc}")
            return self._return_degraded(f"Unexpected failure: {str(exc)}", "Low")

    def _return_degraded(self, reason: str, confidence: str):
        """Return a safe response when analysis fails."""
        analysis = {
            "overall_risk_level": "Unknown",
            "overall_risk_score": 0,
            "risks": [],
            "top_risks": [],
            "recommendations": [],
            "confidence": confidence,
            "failure_reason": reason,
            "status": "degraded" if "Insufficient" in reason else self.status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.context["risk_analysis"] = analysis
        return analysis

    def _get_previous_analysis(self, key: str) -> Any:
        """Safely retrieve another agent's analysis."""
        value = self.context.get(key)
        if isinstance(value, dict):
            return value
        return {}

    def _build_evidence_context(self) -> str:
        """Build a compact context from existing agent outputs."""
        market = self._get_previous_analysis("market_analysis")
        customer = self._get_previous_analysis("customer_analysis")
        competitor = self._get_previous_analysis("competitor_analysis")
        idea_data = self.context.get("idea") or {}
        idea = idea_data.get("description") or "Unknown startup idea"

        # Reduce context payload size by extracting only essential fields
        evidence = {
            "startup_idea": idea,
            "market_maturity": market.get("market_maturity"),
            "market_risks": market.get("risks"),
            "regulations": market.get("regulations"),
            "customer_pain_points": customer.get("pain_points"),
            "competitor_gaps": competitor.get("gap_analysis"),
            "competitor_threats": [c.get("name") for c in competitor.get("competitors", []) if c.get("threat_score", 0) > 70]
        }
        return json.dumps(evidence, indent=2, default=str)

    def _validate_risk(self, risk: Any) -> dict | None:
        """Validate and normalize one risk item with weighted scoring."""
        if not isinstance(risk, dict):
            return None

        category = str(risk.get("category") or "General").strip()
        name = str(risk.get("risk") or "").strip()
        if not name:
            return None

        valid_levels = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        
        severity = str(risk.get("severity") or "Medium").strip().title()
        likelihood = str(risk.get("likelihood") or "Medium").strip().title()
        impact = str(risk.get("impact") or "Medium").strip().title()
        
        if severity not in valid_levels: severity = "Medium"
        if likelihood not in valid_levels: likelihood = "Medium"
        if impact not in valid_levels: impact = "Medium"

        mitigation = str(risk.get("mitigation") or "Further validation is recommended.").strip()
        time_horizon = str(risk.get("time_horizon") or "Medium-term").strip()
        mitigation_effort = str(risk.get("mitigation_effort") or "Medium").strip()
        
        raw_evidence = risk.get("evidence", [])
        if isinstance(raw_evidence, str):
            evidence = [raw_evidence]
        elif isinstance(raw_evidence, list):
            evidence = [str(e) for e in raw_evidence if e]
        else:
            evidence = []

        # Weighted Risk Modeling
        sev_val = valid_levels[severity]
        lik_val = valid_levels[likelihood]
        imp_val = valid_levels[impact]
        
        base_score = sev_val * lik_val * imp_val
        
        category_weights = {
            "financial": 1.2,
            "ai/llm": 1.5,
            "technical feasibility": 1.2,
            "regulatory": 1.4,
            "competition": 1.3
        }
        multiplier = category_weights.get(category.lower(), 1.0)
        adjusted_score = base_score * multiplier
        
        # Residual risk calculation
        mitigation_effectiveness = {
            "Low": 0.8,    # Low effort mitigation leaves 80% risk
            "Medium": 0.5, # Medium effort leaves 50%
            "High": 0.2    # High effort drops risk to 20%
        }.get(mitigation_effort, 0.5)
        
        residual_score = round(adjusted_score * mitigation_effectiveness, 1)
        
        # Quadrant mapping
        if adjusted_score >= 45: quadrant = "Critical (Immediate Action)"
        elif adjusted_score >= 24: quadrant = "High (Strategic Monitoring)"
        elif adjusted_score >= 12: quadrant = "Medium (Standard Mitigation)"
        else: quadrant = "Low (Acceptable Risk)"

        return {
            "category": category,
            "risk": name,
            "severity": severity,
            "likelihood": likelihood,
            "impact": impact,
            "evidence_metadata": evidence,
            "mitigation": mitigation,
            "time_horizon": time_horizon,
            "mitigation_effort": mitigation_effort,
            "risk_score": round(adjusted_score, 1),
            "residual_risk_score": residual_score,
            "risk_quadrant": quadrant
        }

    async def analyze(self, log_prefix: str = "RiskAgent:"):
        """
        Main Risk Agent entry point.
        Uses outputs from existing agents and asks the LLM
        to identify and structure startup risks.
        """
        logger.info(f"{log_prefix} Execution started.")

        if self.llm_client is None:
            return self._return_degraded("LLM client is not available.", "Low")
            
        successful_analyses = sum(1 for key in ["market_analysis", "customer_analysis", "competitor_analysis"] 
                                if self.context.get(key) and self.context.get(key, {}).get("status") != "failed")
                
        if successful_analyses < 2:
            logger.warning(f"{log_prefix} Insufficient data for risk analysis. Found {successful_analyses}/3 upstream outputs.")
            return self._return_degraded("Insufficient data for risk analysis", "Low")

        evidence_context = self._build_evidence_context()

        prompt = f"""
Analyze the risks of the startup using ONLY the provided evidence payload.

Identify risks across these categories when relevant:
1. Market
2. Competition
3. Customer Adoption
4. Technical Feasibility
5. Business
6. Financial
7. Operational
8. Regulatory
9. AI/LLM

Do not invent facts that are not supported by the evidence.

For every identified risk provide:
- category
- risk (The name of the risk)
- severity (Low, Medium, High, Critical)
- likelihood (Low, Medium, High, Critical)
- impact (Low, Medium, High, Critical)
- evidence (Array of strings citing specific facts from the payload)
- mitigation (Practical steps to reduce this risk)
- time_horizon (Short-term, Medium-term, Long-term)
- mitigation_effort (Low, Medium, High)

Also provide:
- top_risks: array of the most important risk names (max 5)
- recommendations: practical mitigation recommendations (max 5)

Return ONLY valid JSON:
{{
    "risks": [],
    "top_risks": [],
    "recommendations": []
}}

Evidence Payload:
{evidence_context}
"""

        max_retries = getattr(settings.agent, "RISK_MAX_RETRIES", 3)
        timeout_seconds = getattr(settings.agent, "RISK_LLM_TIMEOUT", 60)
        parsed_analysis = None
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"{log_prefix} Calling LLM attempt {attempt + 1}/{max_retries}.")
                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt="You are an expert startup risk analysis specialist. Return ONLY valid JSON.",
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
            return self._return_degraded(f"LLM extraction failed: {last_error}", "Low")

        raw_risks = parsed_analysis.get("risks", [])
        if not isinstance(raw_risks, list):
            raw_risks = []

        validated_risks = []
        for raw_risk in raw_risks:
            validated = self._validate_risk(raw_risk)
            if validated:
                validated_risks.append(validated)

        # Deterministic Risk Prioritization
        validated_risks.sort(key=lambda x: x["risk_score"], reverse=True)

        # Calculate Overall Risk Score (0-100 scale, where 100 is max risk)
        if validated_risks:
            total_score = sum(r["risk_score"] for r in validated_risks)
            max_possible = len(validated_risks) * 64 * 1.5 # 4*4*4 * max_multiplier
            overall_risk_score = round((total_score / max_possible) * 100)
        else:
            overall_risk_score = 0
            
        if overall_risk_score >= 75: overall_risk_level = "Critical"
        elif overall_risk_score >= 50: overall_risk_level = "High"
        elif overall_risk_score >= 25: overall_risk_level = "Medium"
        else: overall_risk_level = "Low"

        # Evidence-Quality Confidence Score
        evidence_count = sum(len(r["evidence_metadata"]) for r in validated_risks)
        if evidence_count >= len(validated_risks) * 2 and len(validated_risks) > 0:
            confidence = "High"
        elif evidence_count >= len(validated_risks):
            confidence = "Medium"
        else:
            confidence = "Low"
            
        # Map likelihood and impact to 1-100 scales for Heatmap
        level_map = {"Low": 20, "Medium": 50, "High": 80, "Critical": 95}
        for r in validated_risks:
            r["probability_score"] = level_map.get(r["likelihood"], 50) + random.randint(-5, 5)
            r["impact_score"] = level_map.get(r["impact"], 50) + random.randint(-5, 5)

        top_risks = parsed_analysis.get("top_risks", [])
        recommendations = parsed_analysis.get("recommendations", [])
        if not top_risks and validated_risks:
            top_risks = [r["risk"] for r in validated_risks[:5]]

        analysis = {
            "overall_risk_level": overall_risk_level,
            "overall_risk_score": overall_risk_score,
            "risks": validated_risks,
            "top_risks": [str(r).strip() for r in top_risks if r][:5],
            "recommendations": [str(r).strip() for r in recommendations if r][:10],
            "confidence": confidence,
            "failure_reason": None,
            "status": "success",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"{log_prefix} Risk Analysis Complete. Score: {overall_risk_score}, Risks Identified: {len(validated_risks)}")
        
        from contracts.risk_contract import RiskContract
        from contracts.validator import SafeContractValidator
        
        validated_analysis = SafeContractValidator.validate(RiskContract, analysis, "risk_agent")
        self.context["risk_analysis"] = validated_analysis
        return validated_analysis