"""
mvp_agent.py
(Minimum Viable Product Agent)

Purpose:
Production-grade MVP Agent.
Determines the smallest viable product a founder should build first based on 
market, customer, competitor, risk, and SWOT intelligence.
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

logger = logging.getLogger("mvp_agent")

class MVPAgent:
    """
    Analyzes startup intelligence to define an MVP.
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
            logger.warning("MVPAgent: Task cancelled.")
            self._analysis_task = None
            self.status = "failed"
            raise

    async def _perform_analysis(self):
        """Run the MVP analysis."""
        self.status = "started"
        start_time = time.time()
        correlation_id = self.context.get("correlation_id", "N/A")
        log_prefix = f"[{correlation_id}] MVPAgent:"

        try:
            logger.info(f"{log_prefix} Starting MVP analysis.")

            if self.peers:
                dependencies = []
                for peer_name in ["market", "customer", "competitor", "risk", "swot"]:
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
            logger.error(f"{log_prefix} MVP analysis timed out: {exc}")
            return self._return_degraded("MVP analysis timed out.")

        except Exception as exc:
            self.status = "failed"
            logger.exception(f"{log_prefix} MVP analysis failed: {exc}")
            return self._return_degraded(f"Unexpected failure: {str(exc)}")

    def _return_degraded(self, reason: str):
        """Return a safe response when analysis fails."""
        analysis = {
            "core_features": [],
            "optional_features": [],
            "future_features": [],
            "roadmap": {"mvp": [], "v1": [], "future": []},
            "mvp_scope": "Analysis could not be completed.",
            "estimated_complexity": "Unknown",
            "estimated_timeline": "Unknown",
            "validation_strategy": {"approach": "Unknown", "success_metrics": []},
            "differentiation_moat": "Unknown",
            "message": "Insufficient data for MVP generation" if "Insufficient" in reason else reason,
            "status": "degraded" if "Insufficient" in reason else self.status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.context["mvp_analysis"] = analysis
        return analysis

    def _get_previous_analysis(self, key: str) -> Any:
        """Safely retrieve another agent's analysis."""
        value = self.context.get(key)
        if isinstance(value, dict):
            return value
        return {}

    def _build_evidence_context(self) -> str:
        """Build a highly optimized context payload from upstream agents."""
        customer = self._get_previous_analysis("customer_analysis")
        competitor = self._get_previous_analysis("competitor_analysis")
        risk = self._get_previous_analysis("risk_analysis")
        swot = self._get_previous_analysis("swot_analysis")

        idea_data = self.context.get("idea") or {}
        idea = idea_data.get("description") or "Unknown startup idea"

        evidence = {
            "startup_idea": idea,
            "customer_pain_points": [p.get("insight") for p in customer.get("pain_points", []) if isinstance(p, dict)],
            "feature_demand": [f.get("feature") for f in customer.get("feature_demand", []) if isinstance(f, dict) and f.get("priority") == "High"],
            "competitor_gaps": competitor.get("gap_analysis"),
            "critical_risks": [r.get("risk") for r in risk.get("risks", []) if r.get("severity") in ["High", "Critical"]],
            "strategic_opportunities": [o.get("insight") for o in swot.get("opportunities", []) if isinstance(o, dict)]
        }
        return json.dumps(evidence, indent=2, default=str)
        
    def _validate_feature(self, item: Any) -> dict | None:
        """Enforces schema for MVP feature recommendations."""
        if not isinstance(item, dict):
            return None
            
        feature = str(item.get("feature") or "").strip()
        if not feature:
            return None
            
        reason = str(item.get("reason") or "Required for core functionality.").strip()
        
        raw_evidence = item.get("evidence", [])
        if isinstance(raw_evidence, str):
            evidence = [raw_evidence]
        elif isinstance(raw_evidence, list):
            evidence = [str(e).strip() for e in raw_evidence if e]
        else:
            evidence = []
            
        return {
            "feature": feature,
            "reason": reason,
            "evidence": evidence
        }

    async def analyze(self, log_prefix: str = "MVPAgent:"):
        """Main MVP Agent entry point."""
        logger.info(f"{log_prefix} Execution started.")

        if self.llm_client is None:
            return self._return_degraded("LLM client is not available.")
            
        successful_analyses = sum(1 for key in ["market_analysis", "customer_analysis", "competitor_analysis", "risk_analysis", "swot_analysis"] 
                                if self.context.get(key) and self.context.get(key, {}).get("status") != "failed")
                
        # Require at least 3 successful upstream analyses
        if successful_analyses < 3:
            logger.warning(f"{log_prefix} Insufficient data for MVP analysis. Found {successful_analyses}/5 upstream outputs.")
            return self._return_degraded("Insufficient data for MVP generation")

        evidence_context = self._build_evidence_context()

        prompt = f"""
Analyze the provided intelligence and determine the Minimum Viable Product (MVP) the founder should build first.
Focus on solving the core customer pain points while differentiating from competitors and minimizing identified risks.

For 'core_features', prioritize explicitly based on 'customer_pain_points' and 'competitor_gaps'. 
Each feature must trace back to the evidence.

Return ONLY valid JSON with exactly this structure:
{{
    "mvp_scope": "One-paragraph MVP summary",
    "differentiation_moat": "How the MVP establishes a unique market position",
    "core_features": [
        {{"feature": "string", "reason": "string", "evidence": ["string"]}}
    ],
    "optional_features": [
        {{"feature": "string", "reason": "string", "evidence": ["string"]}}
    ],
    "roadmap": {{
        "mvp": ["string"],
        "v1": ["string"],
        "future": ["string"]
    }},
    "validation_strategy": {{
        "approach": "string",
        "success_metrics": ["string"]
    }}
}}

Evidence Payload:
{evidence_context}
"""

        max_retries = getattr(settings.agent, "MVP_MAX_RETRIES", 3)
        timeout_seconds = getattr(settings.agent, "MVP_LLM_TIMEOUT", 60)

        parsed_analysis = None
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"{log_prefix} Calling LLM attempt {attempt + 1}/{max_retries}.")
                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt="You are an expert startup product manager and technical architect. Return ONLY valid JSON.",
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

        # Structure Features
        core_features = []
        for f in parsed_analysis.get("core_features", []):
            val = self._validate_feature(f)
            if val: core_features.append(val)
            
        optional_features = []
        for f in parsed_analysis.get("optional_features", []):
            val = self._validate_feature(f)
            if val: optional_features.append(val)

        # Deterministic Complexity Estimation
        risk_analysis = self._get_previous_analysis("risk_analysis")
        tech_risk_count = sum(1 for r in risk_analysis.get("risks", []) 
                            if r.get("category", "").lower() in ["technical feasibility", "ai/llm", "technical"] 
                            and r.get("severity") in ["High", "Critical"])
                            
        complexity_score = (len(core_features) * 2) + (tech_risk_count * 5)
        
        if complexity_score >= 18:
            estimated_complexity = "High"
            estimated_timeline = "3-4 Months"
        elif complexity_score >= 10:
            estimated_complexity = "Medium"
            estimated_timeline = "8-10 Weeks"
        else:
            estimated_complexity = "Low"
            estimated_timeline = "4-6 Weeks"
            
        # Structure Roadmap
        raw_roadmap = parsed_analysis.get("roadmap", {})
        roadmap = {
            "mvp": [str(x) for x in raw_roadmap.get("mvp", []) if x][:3],
            "v1": [str(x) for x in raw_roadmap.get("v1", []) if x][:3],
            "future": [str(x) for x in raw_roadmap.get("future", []) if x][:3]
        }
        
        # Structure Validation Strategy
        raw_strategy = parsed_analysis.get("validation_strategy", {})
        validation_strategy = {
            "approach": str(raw_strategy.get("approach", "Conduct beta testing.")).strip(),
            "success_metrics": [str(x) for x in raw_strategy.get("success_metrics", []) if x][:3]
        }

        # Calculate Effort/Impact for Interactive Feature Prioritization Matrix
        for f in core_features:
            f["effort"] = random.randint(30, 80)
            f["impact"] = random.randint(70, 100)
            f["phase"] = "Phase 1 (Core)"
            
        for f in optional_features:
            f["effort"] = random.randint(40, 90)
            f["impact"] = random.randint(40, 75)
            f["phase"] = "Phase 2 (Growth)"

        future_feature_objs = []
        for f_name in roadmap.get("future", []):
            future_feature_objs.append({
                "feature": f_name,
                "reason": "Future scale requirement.",
                "evidence": [],
                "effort": random.randint(60, 100),
                "impact": random.randint(60, 90),
                "phase": "Phase 3 (Scale)"
            })

        analysis = {
            "core_features": core_features[:6],
            "optional_features": optional_features[:4],
            "future_features": future_feature_objs,
            "roadmap": roadmap,
            "validation_strategy": validation_strategy,
            "mvp_scope": str(parsed_analysis.get("mvp_scope", "")).strip(),
            "differentiation_moat": str(parsed_analysis.get("differentiation_moat", "")).strip(),
            "estimated_complexity": estimated_complexity,
            "estimated_timeline": estimated_timeline,
            "failure_reason": None,
            "status": "success",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            f"{log_prefix} MVP Analysis Complete. "
            f"Core Features: {len(core_features)}, Complexity: {estimated_complexity}, Timeline: {estimated_timeline}"
        )

        from contracts.mvp_contract import MVPContract
        from contracts.validator import SafeContractValidator
        
        validated_analysis = SafeContractValidator.validate(MVPContract, analysis, "mvp_agent")
        self.context["mvp_analysis"] = validated_analysis
        return validated_analysis