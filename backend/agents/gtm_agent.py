"""
gtm_agent.py
(Go-To-Market Agent)

Purpose:
Production-grade GTM Agent.
Generates an evidence-backed startup launch strategy using intelligence
from Market, Customer, Competitor, and MVP agents.
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

logger = logging.getLogger("gtm_agent")

class GTMAgent:
    """
    Analyzes startup intelligence to define a Go-To-Market strategy.
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
            logger.warning("GTMAgent: Task cancelled.")
            self._analysis_task = None
            self.status = "failed"
            raise

    async def _perform_analysis(self):
        """Run the GTM analysis."""
        self.status = "started"
        start_time = time.time()
        correlation_id = self.context.get("correlation_id", "N/A")
        log_prefix = f"[{correlation_id}] GTMAgent:"

        try:
            logger.info(f"{log_prefix} Starting GTM analysis.")

            if self.peers:
                dependencies = []
                for peer_name in ["market", "customer", "competitor", "risk", "swot", "mvp"]:
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
            logger.error(f"{log_prefix} GTM analysis timed out: {exc}")
            return self._return_degraded("GTM analysis timed out.")
        except Exception as exc:
            self.status = "failed"
            logger.exception(f"{log_prefix} GTM analysis failed: {exc}")
            return self._return_degraded(f"Unexpected failure: {str(exc)}")

    def _return_degraded(self, reason: str):
        """Return a safe response when analysis fails."""
        analysis = {
            "target_segment": {"segment": "Unknown", "reason": "Data unavailable", "evidence": []},
            "pricing_strategy": {"model": "Unknown", "price_point": "Unknown", "rationale": "", "evidence": []},
            "acquisition_channels": [],
            "launch_channels": [],
            "growth_hacks": [],
            "launch_plan": [],
            "launch_roadmap": {"validation": [], "launch": [], "growth": []},
            "action_plan": {"first_30_days": [], "first_90_days": []},
            "kpi_recommendations": [],
            "marketing_message": "Analysis could not be completed.",
            "estimated_cac_risk": "High",
            "confidence": "Low",
            "go_to_market_score": 0,
            "failure_reason": reason,
            "status": "degraded" if "Insufficient" in reason else self.status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.context["gtm_analysis"] = analysis
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
        mvp = self._get_previous_analysis("mvp_analysis")

        idea_data = self.context.get("idea") or {}
        idea = idea_data.get("description") or "Unknown startup idea"

        evidence = {
            "startup_idea": idea,
            "market_maturity": market.get("market_maturity"),
            "target_personas": [p.get("persona") for p in customer.get("personas", []) if isinstance(p, dict)],
            "customer_pain_points": [p.get("insight") for p in customer.get("pain_points", []) if isinstance(p, dict)],
            "competitor_pricing": [c.get("pricing") for c in competitor.get("competitors", []) if isinstance(c, dict)],
            "mvp_scope": mvp.get("mvp_scope")
        }
        return json.dumps(evidence, indent=2, default=str)

    def _validate_evidence_dict(self, item: Any, default_key: str) -> dict | None:
        """Validates standard evidence-backed dictionaries."""
        if not isinstance(item, dict):
            return None
            
        main_val = str(item.get(default_key) or "").strip()
        if not main_val:
            return None
            
        raw_evidence = item.get("evidence", [])
        evidence = [str(e).strip() for e in raw_evidence if e] if isinstance(raw_evidence, list) else []
            
        return item | {"evidence": evidence}

    async def analyze(self, log_prefix: str = "GTMAgent:"):
        """Main GTM Agent entry point."""
        logger.info(f"{log_prefix} Execution started.")

        if self.llm_client is None:
            return self._return_degraded("LLM client is not available.")
            
        successful_analyses = sum(1 for key in ["market_analysis", "customer_analysis", "competitor_analysis", "risk_analysis", "swot_analysis", "mvp_analysis"] 
                                if self.context.get(key) and self.context.get(key, {}).get("status") != "failed")
                
        if successful_analyses < 4:
            logger.warning(f"{log_prefix} Insufficient data for GTM analysis. Found {successful_analyses}/6 upstream outputs.")
            return self._return_degraded("Insufficient data for GTM generation")

        evidence_context = self._build_evidence_context()

        prompt = f"""
Analyze the provided intelligence and generate a Go-To-Market (GTM) strategy for the MVP.
All recommendations must cite specific evidence from the payload and MUST be tailored exactly to the specific startup idea. Avoid generic industry-wide marketing advice. If you lack evidence for a field, explain why instead of using "Unknown" or "None".

Return ONLY valid JSON with exactly this structure. Keep all descriptions concise (max 2 sentences). Limit all arrays to a maximum of 3 items. Ensure the JSON is completely formed and properly closed before finishing:
{{
    "target_segment": {{"segment": "string", "reason": "string", "evidence": ["string"]}},
    "pricing_strategy": {{"model": "string", "price_point": "string", "rationale": "string", "evidence": ["string"]}},
    "acquisition_channels": [
        {{"channel": "string", "type": "Paid or Organic", "priority": "High or Medium", "evidence": ["string"]}}
    ],
    "launch_roadmap": {{
        "validation": ["string"],
        "launch": ["string"],
        "growth": ["string"]
    }},
    "action_plan": {{
        "first_30_days": ["string"],
        "first_90_days": ["string"]
    }},
    "kpi_recommendations": ["string"],
    "marketing_message": "string"
}}

Evidence Payload:
{evidence_context}
"""

        max_retries = getattr(settings.agent, "GTM_MAX_RETRIES", 3)
        timeout_seconds = getattr(settings.agent, "GTM_LLM_TIMEOUT", 60)
        parsed_analysis = None
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"{log_prefix} Calling LLM attempt {attempt + 1}/{max_retries}.")
                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt=(
                            "You are an expert startup growth marketer. "
                            "STRICT REQUIREMENT: Penalize broad industry commentary. You must analyze the EXACT startup idea and target customer. "
                            "Do not use generic 'Unknown' or 'None' placeholders. If data is unavailable, provide a brief explanation of why. "
                            "Return ONLY valid JSON."
                        ),
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

        # Structure Target Segment
        target_segment = parsed_analysis.get("target_segment", {})
        if not isinstance(target_segment, dict): target_segment = {}
        
        # Structure Pricing Strategy
        pricing_strategy = parsed_analysis.get("pricing_strategy", {})
        if not isinstance(pricing_strategy, dict): pricing_strategy = {}

        # Structure Channels
        raw_channels = parsed_analysis.get("acquisition_channels", [])
        acquisition_channels = []
        if isinstance(raw_channels, list):
            for c in raw_channels:
                val = self._validate_evidence_dict(c, "channel")
                if val: acquisition_channels.append(val)

        # Deterministic CAC Risk Estimation
        market_analysis = self._get_previous_analysis("market_analysis")
        market_maturity = str(market_analysis.get("market_maturity", "")).lower()
        
        paid_channel_count = sum(1 for c in acquisition_channels if str(c.get("type", "")).lower() == "paid")
        total_channels = len(acquisition_channels)
        paid_ratio = paid_channel_count / total_channels if total_channels > 0 else 0
        
        if market_maturity == "saturated" or paid_ratio > 0.6:
            cac_risk = "High"
        elif paid_ratio > 0.3:
            cac_risk = "Medium"
        else:
            cac_risk = "Low"

        # Deterministic Go-To-Market Score
        gtm_score = 50
        if cac_risk == "Low": gtm_score += 20
        elif cac_risk == "High": gtm_score -= 15
        
        if len(acquisition_channels) >= 2: gtm_score += 15
        if target_segment.get("segment"): gtm_score += 15
        gtm_score = max(0, min(100, gtm_score))
        
        # Calculate dynamic CAC vs LTV visualizations based on inferred pricing models
        customer_analysis = self._get_previous_analysis("customer_analysis")
        willingness_to_pay = customer_analysis.get("willingness_to_pay", {})
        
        expected_price_str = willingness_to_pay.get("expected", "$10/mo")
        # Extract numeric value for LTV calculation
        price_val = 10
        import re
        match = re.search(r'\$?(\d+)', expected_price_str)
        if match:
            price_val = int(match.group(1))
            
        is_monthly = "mo" in expected_price_str.lower()
        
        # Heuristic LTV (Assume 12 month lifespan if monthly, 3 years if annual)
        ltv = price_val * 12 if is_monthly else price_val * 3
        
        # Heuristic CAC based on CAC risk
        if cac_risk == "Low": cac = ltv * 0.15
        elif cac_risk == "Medium": cac = ltv * 0.33
        else: cac = ltv * 0.6
        
        cac = round(cac)
        ltv = round(ltv)
        
        # Set a minimum floor
        if cac < 5: cac = 5
        if ltv < 15: ltv = 15

        # Evidence-Quality Confidence Score
        total_evidence = len(target_segment.get("evidence", [])) + len(pricing_strategy.get("evidence", []))
        total_evidence += sum(len(c.get("evidence", [])) for c in acquisition_channels)
        
        if total_evidence >= 4: confidence = "High"
        elif total_evidence >= 2: confidence = "Medium"
        else: confidence = "Low"

        # Map to legacy arrays to preserve downstream backward compatibility (e.g. StartupScoringService fallback)
        launch_channels = [c.get("channel") for c in acquisition_channels if c.get("channel")]
        growth_hacks = [str(k) for k in parsed_analysis.get("kpi_recommendations", [])][:3]

        raw_roadmap = parsed_analysis.get("launch_roadmap", {})
        launch_roadmap = {
            "validation": [str(x) for x in raw_roadmap.get("validation", [])][:3],
            "launch": [str(x) for x in raw_roadmap.get("launch", [])][:3],
            "growth": [str(x) for x in raw_roadmap.get("growth", [])][:3]
        }
        
        raw_action = parsed_analysis.get("action_plan", {})
        action_plan = {
            "first_30_days": [str(x) for x in raw_action.get("first_30_days", [])][:3],
            "first_90_days": [str(x) for x in raw_action.get("first_90_days", [])][:3]
        }
        
        # Format Funnel Pipeline array for the UI
        funnel_pipeline = [
            {"stage": "Awareness", "channels": launch_channels[:2], "conversion_rate": "2-5%"},
            {"stage": "Acquisition", "tactics": ["Landing Page", "Lead Magnet"], "conversion_rate": "10-20%"},
            {"stage": "Activation", "tactics": ["Onboarding", "Free Trial"], "conversion_rate": "30-50%"},
            {"stage": "Revenue", "metrics": {"cac": f"${cac}", "ltv": f"${ltv}"}}
        ]

        analysis = {
            "target_segment": target_segment,
            "pricing_strategy": pricing_strategy,
            "acquisition_channels": acquisition_channels,
            "launch_roadmap": launch_roadmap,
            "action_plan": action_plan,
            "kpi_recommendations": [str(x) for x in parsed_analysis.get("kpi_recommendations", [])][:5],
            "marketing_message": str(parsed_analysis.get("marketing_message", "")).strip(),
            "estimated_cac_risk": cac_risk,
            "go_to_market_score": gtm_score,
            "confidence": confidence,
            "launch_channels": launch_channels,
            "growth_hacks": growth_hacks,
            "launch_plan": action_plan.get("first_30_days", []) + action_plan.get("first_90_days", []),
            "funnel_pipeline": funnel_pipeline,
            "cac_ltv_metrics": {"cac": cac, "ltv": ltv},
            "failure_reason": None,
            "status": "success",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"{log_prefix} GTM Analysis Complete. CAC Risk: {cac_risk}, GTM Score: {gtm_score}/100")
        
        from contracts.gtm_contract import GTMContract
        from contracts.validator import SafeContractValidator
        
        validated_analysis = SafeContractValidator.validate(GTMContract, analysis, "gtm_agent")
        self.context["gtm_analysis"] = validated_analysis
        return validated_analysis
