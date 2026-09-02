import asyncio
import json
import logging
import time
import random
from datetime import datetime, timezone
from typing import Any

from core.config import settings
from utils.error_handler import safe_parse_llm_json
from contracts.competitor_contract import CompetitorContract
from contracts.validator import SafeContractValidator

logger = logging.getLogger("competitor_agent")

class CompetitorAgent:
    """
    Analyzes competitors using LLM intelligence.
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
            logger.warning("CompetitorAgent: Task cancelled.")
            self._analysis_task = None
            self.status = "failed"
            raise

    def _return_degraded(self, reason: str, confidence: str = "Low", log_prefix: str = "CompetitorAgent:"):
        analysis = {
            "competitors": [],
            "competitor_gaps": [],
            "gap_analysis": [],
            "no_competitor_data_found": True,
            "competition_score": 0,
            "confidence_level": confidence,
            "status": self.status,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        validated = SafeContractValidator.validate(CompetitorContract, analysis, "competitor_agent")
        self.context["competitor_analysis"] = validated
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
        log_prefix = f"[{correlation_id}] CompetitorAgent:"

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

    async def analyze(self, log_prefix: str = "CompetitorAgent:"):
        if self.llm_client is None:
            return self._return_degraded("LLM client is not available.")
            
        evidence_context = self._build_evidence_context()
        if not evidence_context.strip():
            return self._return_degraded("No valid competitor research evidence found.")

        prompt = f"""
Analyze the competitors for the startup using ONLY the provided evidence.

Return a valid JSON object matching this EXACT structure:
{{
    "competitors": [
        {{
            "name": "Competitor Name",
            "pricing": "$10/mo",
            "business_model": "SaaS",
            "strengths": ["Strength 1"],
            "weaknesses": ["Weakness 1"],
            "features": ["Feature 1", "Feature 2"],
            "threat_score": 85,
            "position_x": 80,
            "position_y": 60,
            "product_summary": "Brief summary",
            "moat_score": {{"technology": 80, "brand": 70, "distribution": 60, "execution": 90}}
        }}
    ],
    "competitor_gaps": [
        "Gap 1",
        "Gap 2"
    ],
    "competition_score": 50,
    "confidence_level": "High"
}}

IMPORTANT RULES:
1. Identify up to 4 primary competitors from the evidence.
2. "threat_score" must be an integer (0-100). 100 means high threat.
3. "position_x" is Price/Complexity (0-100).
4. "position_y" is Market Value/Depth (0-100).
5. "moat_score" is only required for the top competitor, out of 100 per category.
6. "competition_score" is an integer (0-100) reflecting the overall competitive whitespace (100 = high whitespace/blue ocean, 0 = saturated red ocean).
7. "competitor_gaps" should have 2-4 points on how the startup can differentiate.

Evidence:
{evidence_context}
"""

        max_retries = getattr(settings.agent, "COMPETITOR_MAX_RETRIES", 3)
        timeout_seconds = getattr(settings.agent, "COMPETITOR_LLM_TIMEOUT", 60)
        parsed_analysis = None
        last_error = None

        for attempt in range(max_retries):
            try:
                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt="You are an expert competitive intelligence analyst. Provide factual, evidence-based competitor analysis.",
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

        parsed_analysis["status"] = self.status
        parsed_analysis["generated_at"] = datetime.now(timezone.utc).isoformat()
        
        parsed_analysis["competition_score"] = max(0, min(100, int(parsed_analysis.get("competition_score", 50))))
        parsed_analysis["gap_analysis"] = parsed_analysis.get("competitor_gaps", [])

        validated = SafeContractValidator.validate(CompetitorContract, parsed_analysis, "competitor_agent")
        
        # Inject non-schema fields so they persist for the UI/orchestrator
        validated["competition_score"] = parsed_analysis.get("competition_score")
        validated["confidence_level"] = parsed_analysis.get("confidence_level", "Medium")
        
        self.context["competitor_analysis"] = validated
        return validated