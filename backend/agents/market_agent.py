import asyncio
import json
import logging
import time
import random
from datetime import datetime, timezone
from typing import Any

from core.config import settings
from utils.error_handler import safe_parse_llm_json, MalformedLLMOutputError
from contracts.market_contract import MarketContract
from contracts.validator import SafeContractValidator

logger = logging.getLogger("market_agent")

class MarketAnalysisError(Exception):
    """Raised when market analysis fails."""

class MarketOpportunityAgent:
    """
    Analyzes the market for a startup idea using LLM intelligence.
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
            logger.warning("MarketOpportunityAgent: Task cancelled.")
            self._analysis_task = None
            self.status = "failed"
            raise

    def _return_degraded(self, reason: str, confidence: str = "Low", log_prefix: str = "MarketAgent:"):
        analysis = {
            "market_size": "Insufficient verified evidence.",
            "growth_rate": "Insufficient verified evidence.",
            "market_maturity": "Insufficient verified evidence.",
            "tam": "Data unavailable",
            "sam": "Data unavailable",
            "som": "Data unavailable",
            "methodology": "Data unavailable",
            "market_segmentation": [],
            "growth_drivers": [],
            "market_trends": [],
            "opportunities": [],
            "challenges": [],
            "industry_insights": [],
            "regulations": [],
            "market_summary": f"Analysis could not be completed: {reason}",
            "confidence_score": confidence,
            "opportunity_score": 0,
            "status": self.status,
            "failure_reason": reason,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "evidence": []
        }
        validated = SafeContractValidator.validate(MarketContract, analysis, "market_agent")
        self.context["market_analysis"] = validated
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
        log_prefix = f"[{correlation_id}] MarketAgent:"

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

    async def analyze(self, log_prefix: str = "MarketAgent:"):
        if self.llm_client is None:
            return self._return_degraded("LLM client is not available.")
            
        evidence_context = self._build_evidence_context()
        if not evidence_context.strip():
            return self._return_degraded("No valid market research evidence found.")

        prompt = f"""
Analyze the market opportunity for the startup using ONLY the provided evidence.

Return a valid JSON object matching this structure EXACTLY:
{{
    "market_size": "Current overall market valuation, eg '$50B' (or 'Data unavailable')",
    "growth_rate": "CAGR or percentage growth, eg '15%' (or 'Data unavailable')",
    "market_maturity": "Emerging, Growing, or Mature (or 'Data unavailable')",
    "tam": "Total Addressable Market estimate (or 'Data unavailable')",
    "sam": "Serviceable Available Market estimate (or 'Data unavailable')",
    "som": "Serviceable Obtainable Market estimate (or 'Data unavailable')",
    "methodology": "Brief explanation of how the TAM/SAM/SOM were derived",
    "market_segmentation": ["Segment 1", "Segment 2"],
    "growth_drivers": ["Driver 1", "Driver 2"],
    "market_trends": ["Trend 1", "Trend 2"],
    "opportunities": ["Opportunity 1", "Opportunity 2"],
    "challenges": ["Challenge 1", "Challenge 2"],
    "industry_insights": ["Insight 1", "Insight 2"],
    "regulations": ["Regulation 1", "Regulation 2"],
    "market_summary": "A cohesive paragraph summarizing the entire market landscape without generic filler. DO NOT include raw unescaped JSON, brackets, or arrays in this text.",
    "opportunity_score": 85,
    "confidence_score": "High"
}}

IMPORTANT RULES:
1. ONLY use the provided evidence. Do NOT hallucinate data.
2. If explicit metrics are unavailable, DO NOT guess. Use "Data unavailable".
3. Provide arrays of strings for trends, drivers, etc. Max 5 items per array.
4. "opportunity_score" must be an integer between 0 and 100 based on market strength.
5. "confidence_score" must be "High", "Medium", or "Low" based on evidence quality.
6. Make sure "market_summary" is clean text with NO unescaped JSON characters.

Evidence:
{evidence_context}
"""

        max_retries = getattr(settings.agent, "MARKET_MAX_RETRIES", 3)
        timeout_seconds = getattr(settings.agent, "MARKET_LLM_TIMEOUT", 60)
        parsed_analysis = None
        last_error = None

        for attempt in range(max_retries):
            try:
                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt="You are an expert market research analyst. Provide factual, evidence-based market intelligence.",
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
        
        # Ensure opportunity_score is capped appropriately
        parsed_analysis["opportunity_score"] = max(0, min(100, int(parsed_analysis.get("opportunity_score", 50))))

        validated = SafeContractValidator.validate(MarketContract, parsed_analysis, "market_agent")
        self.context["market_analysis"] = validated
        return validated
