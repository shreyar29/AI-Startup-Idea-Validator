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
            self._analysis_task = asyncio.create_task(
                self._perform_analysis()
            )

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

        correlation_id = self.context.get(
            "correlation_id",
            "N/A"
        )

        log_prefix = f"[{correlation_id}] RiskAgent:"

        try:
            logger.info(
                f"{log_prefix} Starting risk analysis."
            )

            result = await self.analyze(log_prefix)

            self.status = "success"

            duration = time.time() - start_time

            logger.info(
                f"{log_prefix} Completed successfully "
                f"in {duration:.2f}s."
            )

            return result

        except asyncio.TimeoutError as exc:
            self.status = "timeout"

            logger.error(
                f"{log_prefix} Risk analysis timed out: {exc}"
            )

            return self._return_degraded(
                "Risk analysis timed out.",
                "Low"
            )

        except Exception as exc:
            self.status = "failed"

            logger.exception(
                f"{log_prefix} Risk analysis failed: {exc}"
            )

            return self._return_degraded(
                f"Unexpected failure: {str(exc)}",
                "Low"
            )

    def _return_degraded(
        self,
        reason: str,
        confidence: str
    ):
        """Return a safe response when analysis fails."""

        analysis = {
            "overall_risk_level": "Unknown",
            "overall_risk_score": 0,
            "risks": [],
            "top_risks": [],
            "recommendations": [],
            "confidence": confidence,
            "failure_reason": reason,
            "status": self.status,
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
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
        """
        Build a compact context from existing agent outputs.

        Risk Agent consumes existing structured results instead
        of performing duplicate web research.
        """

        market = self._get_previous_analysis(
            "market_analysis"
        )

        customer = self._get_previous_analysis(
            "customer_analysis"
        )

        competitor = self._get_previous_analysis(
            "competitor_analysis"
        )

        comparison = self._get_previous_analysis(
            "comparison_analysis"
        )

        idea_data = self.context.get("idea") or {}

        idea = (
            idea_data.get("description")
            or "Unknown startup idea"
        )

        evidence = {
            "startup_idea": idea,
            "market_analysis": market,
            "customer_analysis": customer,
            "competitor_analysis": competitor,
            "comparison_analysis": comparison,
        }

        return json.dumps(
            evidence,
            indent=2,
            default=str
        )

    def _validate_risk(self, risk: Any) -> dict | None:
        """Validate and normalize one risk item."""

        if not isinstance(risk, dict):
            return None

        category = str(
            risk.get("category") or "General"
        ).strip()

        name = str(
            risk.get("risk") or ""
        ).strip()

        if not name:
            return None

        severity = str(
            risk.get("severity") or "Medium"
        ).strip().title()

        likelihood = str(
            risk.get("likelihood") or "Medium"
        ).strip().title()

        impact = str(
            risk.get("impact") or "Medium"
        ).strip().title()

        evidence = str(
            risk.get("evidence") or "Not available"
        ).strip()

        mitigation = str(
            risk.get("mitigation")
            or "Further validation is recommended."
        ).strip()

        valid_levels = {
            "Low",
            "Medium",
            "High",
            "Critical"
        }

        if severity not in valid_levels:
            severity = "Medium"

        if likelihood not in valid_levels:
            likelihood = "Medium"

        if impact not in valid_levels:
            impact = "Medium"

        return {
            "category": category,
            "risk": name,
            "severity": severity,
            "likelihood": likelihood,
            "impact": impact,
            "evidence": evidence,
            "mitigation": mitigation,
        }

    def _calculate_score(
        self,
        risks: list[dict]
    ) -> tuple[int, str]:

        weights = {
            "Low": 1,
            "Medium": 2,
            "High": 3,
            "Critical": 4,
        }

        if not risks:
            return 0, "Low"

        total = 0

        for risk in risks:
            severity = weights.get(
                risk.get("severity"),
                2
            )

            likelihood = weights.get(
                risk.get("likelihood"),
                2
            )

            impact = weights.get(
                risk.get("impact"),
                2
            )

            total += (
                severity
                + likelihood
                + impact
            )

        maximum = len(risks) * 12

        score = round(
            (total / maximum) * 100
        )

        if score >= 75:
            level = "Critical"
        elif score >= 50:
            level = "High"
        elif score >= 25:
            level = "Medium"
        else:
            level = "Low"

        return score, level

    async def analyze(
        self,
        log_prefix: str = "RiskAgent:"
    ):
        """
        Main Risk Agent entry point.

        Uses outputs from existing agents and asks the LLM
        to identify and structure startup risks.
        """

        logger.info(
            f"{log_prefix} Execution started."
        )

        if self.llm_client is None:
            return self._return_degraded(
                "LLM client is not available.",
                "Low"
            )

        evidence_context = (
            self._build_evidence_context()
        )

        prompt = f"""
Analyze the risks of the startup using ONLY the
provided evidence.

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

Do not invent facts that are not supported by
the provided evidence.

For every identified risk provide:

- category
- risk
- severity
- likelihood
- impact
- evidence
- mitigation

Severity, likelihood and impact must be one of:

Low
Medium
High
Critical

Also provide:

- top_risks: array of the most important risk names
- recommendations: practical mitigation recommendations

Return ONLY valid JSON with exactly:

{{
    "risks": [],
    "top_risks": [],
    "recommendations": []
}}

Evidence:

{evidence_context}
"""

        max_retries = getattr(
            settings.agent,
            "RISK_MAX_RETRIES",
            3
        )

        timeout_seconds = getattr(
            settings.agent,
            "RISK_LLM_TIMEOUT",
            60
        )

        parsed_analysis = None
        last_error = None

        for attempt in range(max_retries):

            try:

                logger.info(
                    f"{log_prefix} "
                    f"Calling LLM attempt "
                    f"{attempt + 1}/{max_retries}."
                )

                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt=(
                            "You are an expert startup "
                            "risk analysis specialist. "
                            "Return ONLY valid JSON."
                        ),
                        user_prompt=(
                            prompt
                            if attempt == 0
                            else (
                                f"{prompt}\n\n"
                                "Previous output was invalid. "
                                f"Fix the JSON formatting. "
                                f"Error: {last_error}"
                            )
                        ),
                    ),
                    timeout=timeout_seconds
                )

                parsed_analysis = (
                    safe_parse_llm_json(
                        raw_response
                    )
                )

                break

            except asyncio.TimeoutError:

                last_error = "LLM Timeout"

                logger.warning(
                    f"{log_prefix} LLM timeout."
                )

            except MalformedLLMOutputError as exc:

                last_error = str(exc)

                logger.warning(
                    f"{log_prefix} Invalid JSON: {exc}"
                )

            except Exception as exc:

                last_error = str(exc)

                logger.exception(
                    f"{log_prefix} LLM request failed."
                )

                break

        if not isinstance(
            parsed_analysis,
            dict
        ):

            return self._return_degraded(
                f"LLM extraction failed: "
                f"{last_error}",
                "Low"
            )

        raw_risks = parsed_analysis.get(
            "risks",
            []
        )

        if not isinstance(raw_risks, list):
            raw_risks = []

        validated_risks = []

        for raw_risk in raw_risks:

            validated = self._validate_risk(
                raw_risk
            )

            if validated:
                validated_risks.append(
                    validated
                )

        score, risk_level = (
            self._calculate_score(
                validated_risks
            )
        )

        top_risks = parsed_analysis.get(
            "top_risks",
            []
        )

        if not isinstance(top_risks, list):
            top_risks = []

        recommendations = parsed_analysis.get(
            "recommendations",
            []
        )

        if not isinstance(
            recommendations,
            list
        ):
            recommendations = []

        top_risks = [
            str(item).strip()
            for item in top_risks
            if item
        ]

        recommendations = [
            str(item).strip()
            for item in recommendations
            if item
        ]

        analysis = {
            "overall_risk_level": risk_level,
            "overall_risk_score": score,
            "risks": validated_risks,
            "top_risks": top_risks[:5],
            "recommendations": recommendations[:10],
            "confidence": (
                "High"
                if validated_risks
                else "Low"
            ),
            "failure_reason": None,
            "status": "success",
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self.context["risk_analysis"] = analysis

        logger.info(
            f"{log_prefix} Risk analysis complete. "
            f"Level={risk_level}, Score={score}"
        )

        logger.info(
            json.dumps(
                analysis,
                indent=2
            )
        )

        return analysis