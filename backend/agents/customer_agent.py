import asyncio
import json
import logging
import time
import random
from datetime import datetime, timezone
from typing import Any

from core.config import settings
from utils.error_handler import safe_parse_llm_json, MalformedLLMOutputError
from contracts.customer_contract import CustomerContract
from contracts.validator import SafeContractValidator

logger = logging.getLogger("customer_agent")

class CustomerAnalysisError(Exception):
    """Raised when customer analysis fails."""

class CustomerAgent:
    """
    Analyzes customer segmentation for a startup idea using LLM intelligence.
    Operates as a decentralized node in the A2A Mesh Network.
    """

    def __init__(self, shared_context: dict, llm_client=None):
        self.context = shared_context
        self.llm_client = llm_client
        self.peers = {}
        self._analysis_task = None
        self.status = "idle"

    def connect_peers(self, peers: dict):
        self.peers = peers

    async def get_analysis(self):
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
            logger.warning("CustomerAgent: Task cancelled.")
            self._analysis_task = None
            self.status = "failed"
            raise

    def _return_degraded(self, reason: str, confidence: str = "Low", log_prefix: str = "CustomerAgent:"):
        analysis = {
            "target_customer_segments": [],
            "pain_points": [],
            "unmet_needs": [],
            "customer_personas": [],
            "customer_journey": [],
            "sentiment": {"overall_sentiment": "Unknown", "positive_factors": [], "negative_factors": []},
            "feature_demand": [],
            "willingness_to_pay": {"low": "$0", "expected": "$0", "premium": "$0"},
            "customer_validation_metrics": {
                "validation_score": 0,
                "confidence": confidence,
                "total_unique_sources": 0,
                "summary": f"Analysis could not be completed: {reason}"
            },
            "customer_score": 0,
            "confidence_level": confidence,
            "status": self.status,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        validated = SafeContractValidator.validate(CustomerContract, analysis, "customer_agent")
        self.context["customer_analysis"] = validated
        return validated

    def _build_evidence_context(self) -> str:
        research = self.context.get("research", {})
        if "search_results" in research and isinstance(research["search_results"], dict):
            research = research["search_results"]
            
        evidence_text = ""
        for cat, results in research.items():
            if isinstance(results, list):
                for r in results[:10]:
                    evidence_text += f"- [{r.get('url', 'Unknown')}] {r.get('content', '')}\n"
        return evidence_text[:15000]

    async def _perform_analysis(self):
        self.status = "started"
        start_time = time.time()
        correlation_id = self.context.get("correlation_id", "N/A")
        log_prefix = f"[{correlation_id}] CustomerAgent:"

        try:
            logger.info(f"{log_prefix} Awaiting research payload.")
            if "web_search" in self.peers:
                research_data = await self.peers["web_search"].get_analysis()
                self.context["research"] = research_data
                
            result = await self.analyze(log_prefix)
            self.status = "success"
            duration = time.time() - start_time
            logger.info(f"{log_prefix} Completed successfully in {duration:.2f}s.")
            return result

        except asyncio.TimeoutError as exc:
            self.status = "timeout"
            return self._return_degraded("Analysis timed out.")
        except Exception as exc:
            self.status = "failed"
            logger.exception(f"{log_prefix} Failed: {exc}")
            return self._return_degraded(f"Unexpected failure: {exc}")

    async def analyze(self, log_prefix: str = "CustomerAgent:"):
        if self.llm_client is None:
            return self._return_degraded("LLM client is not available.")
            
        evidence_context = self._build_evidence_context()
        if not evidence_context.strip():
            return self._return_degraded("No valid customer research evidence found.")

        prompt = f"""
Analyze the target customers for this startup using ONLY the provided evidence.

Return a valid JSON object matching this EXACT structure:
{{
    "target_customer_segments": [
        {{"insight": "Segment description", "evidence": ["URL 1", "URL 2"]}}
    ],
    "pain_points": [
        {{"insight": "Pain point description", "evidence": ["URL 1"]}}
    ],
    "unmet_needs": [
        {{"insight": "Unmet need description", "evidence": ["URL 1"]}}
    ],
    "feature_demand": [
        {{"insight": "Feature requested", "evidence": ["URL 1"]}}
    ],
    "customer_personas": [
        {{
            "name": "Persona Name",
            "inferred_attributes": {{
                "demographics": "25-35",
                "occupation": "Software Engineer",
                "location": "Urban",
                "income": "High",
                "budget": "Flexible",
                "decision_drivers": ["Quality", "Speed"]
            }},
            "evidence_based_attributes": {{
                "goals": ["Goal 1", "Goal 2"],
                "pain_points": ["Pain point 1"],
                "buying_behaviour": ["Behaviour 1"]
            }}
        }}
    ],
    "willingness_to_pay": {{
        "low": "$10/mo",
        "expected": "$29/mo",
        "premium": "$99/mo"
    }},
    "customer_score": 85,
    "confidence_level": "High",
    "customer_validation_summary": "A clean paragraph summarizing the core customer insights without JSON formatting."
}}

IMPORTANT RULES:
1. ONLY use the provided evidence.
2. Maximize 3 segments, 5 pain points, 5 unmet needs, and 2 personas to keep it concise.
3. Keep descriptions clean and human-readable. Do not return messy HTML or JSON characters in your strings.
4. "customer_score" must be an integer between 0 and 100 based on validation strength.
5. "confidence_level" must be "High", "Medium", or "Low".
6. If willingness to pay is not explicitly in the text, logically infer it based on the persona's budget/demographics and standard market pricing for similar software/services.

Evidence:
{evidence_context}
"""

        max_retries = getattr(settings.agent, "CUSTOMER_MAX_RETRIES", 3)
        timeout_seconds = getattr(settings.agent, "CUSTOMER_LLM_TIMEOUT", 60)
        parsed_analysis = None
        last_error = None

        for attempt in range(max_retries):
            try:
                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt="You are an expert customer researcher. Synthesize factual customer segments and pain points.",
                        user_prompt=(prompt if attempt == 0 else f"{prompt}\n\nFix JSON format error: {last_error}"),
                        response_format={"type": "json_object"}
                    ),
                    timeout=timeout_seconds
                )
                parsed_analysis = safe_parse_llm_json(raw_response)
                break
            except asyncio.TimeoutError:
                last_error = "LLM Timeout"
                await asyncio.sleep((2 ** attempt) + random.uniform(0, 1))
            except Exception as exc:
                last_error = str(exc)
                await asyncio.sleep((2 ** attempt) + random.uniform(0, 1))

        if not isinstance(parsed_analysis, dict):
            return self._return_degraded(f"LLM extraction failed: {last_error}")

        # Final structure formatting
        parsed_analysis["status"] = self.status
        parsed_analysis["generated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Calculate heuristics for UI metrics
        total_sources = len(set(
            url for seg in parsed_analysis.get("target_customer_segments", []) for url in seg.get("evidence", [])
        ))
        parsed_analysis["customer_validation_metrics"] = {
            "validation_score": parsed_analysis.get("customer_score", 50),
            "confidence": parsed_analysis.get("confidence_level", "Medium"),
            "total_unique_sources": max(total_sources, 1),
            "summary": parsed_analysis.pop("customer_validation_summary", "Customer profiles built.")
        }
        
        parsed_analysis["customer_score"] = max(0, min(100, int(parsed_analysis.get("customer_score", 50))))

        validated = SafeContractValidator.validate(CustomerContract, parsed_analysis, "customer_agent")
        
        # Inject the non-schema customer_score / confidence_level fields so they persist for the UI/orchestrator
        validated["customer_score"] = parsed_analysis.get("customer_score")
        validated["confidence_level"] = parsed_analysis.get("confidence_level")
        
        self.context["customer_analysis"] = validated
        return validated