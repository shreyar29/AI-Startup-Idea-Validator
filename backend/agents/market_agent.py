"""
market_agent.py
(Market Agent)

Purpose:
Milestone 2 — Market Opportunity Agent.
Synthesizes raw search results into structured market insights (market size, growth rate, trends, opportunities, challenges) using an LLM.
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Any

from utils.error_handler import safe_parse_llm_json, MalformedLLMOutputError

logger = logging.getLogger("market_agent")

class MarketAnalysisError(Exception):
    """Raised when market analysis fails."""

class MarketOpportunityAgent:
    """
    Analyzes the market for a startup idea using research data.
    Operates as a decentralized node in the A2A Mesh Network.
    """

    def __init__(self, shared_context: dict, llm_client=None):
        self.context = shared_context
        self.llm_client = llm_client
        self.peers = {}
        self._analysis_task = None

    def connect_peers(self, peers: dict):
        """Connects this agent to all other agents in the mesh."""
        self.peers = peers

    async def get_analysis(self):
        """
        Mesh Network endpoint. Returns the analysis, computing it
        only once and caching the result as an asyncio Task.
        """
        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(self._perform_analysis())
        return await self._analysis_task

    async def _perform_analysis(self):
        """Pulls required data from peers and runs the analysis."""
        logger.info("MarketOpportunityAgent: Awaiting research payload from Web Search Agent.")
        # Pull research dynamically from the Web Search peer
        if "web_search" in self.peers:
            research_data = await self.peers["web_search"].get_analysis()
            self.context["research"] = research_data
            logger.info("MarketOpportunityAgent: Successfully received research payload.")
            
        # Run the CPU/Network bound logic
        result = await self.analyze()
        return result

    def _validate_and_coerce_list(self, val: Any) -> list:
        """Helper to ensure a value is strictly a list of strings."""
        if not val:
            return []
        if isinstance(val, list):
            return [str(v) for v in val if v]
        if isinstance(val, str):
            return [val]
        return []

    async def analyze(self):
        """
        Main entry point. Uses LLM to parse raw market snippets.
        Populates and returns shared_context["market_analysis"].
        """
        logger.info("Market Opportunity Agent: Execution started.")
        
        research = self.context.get("research", {})
        idea = self.context.get("idea", {}).get("description", "Unknown startup idea")

        if not research:
            logger.warning("Market Opportunity Agent: No research data found in Shared Context. Aborting.")
            return self._return_fallback("Missing research data")

        # Combine all raw snippets from WebSearchAgent (market_data, competitors, target_audience)
        snippets = []
        for cat, results in research.items():
            if isinstance(results, list):
                for r in results:
                    content = r.get("content", "").strip()
                    if content:
                        snippets.append(content)
        
        logger.info(f"Market Opportunity Agent: Consolidated {len(snippets)} snippets for analysis.")
        
        raw_text = "\n".join(snippets)[:3000]  # truncate to fit in LLM context

        if not raw_text.strip():
            logger.warning("Market Opportunity Agent: Research data is empty after extraction.")
            return self._return_fallback("Empty research data")

        prompt = (
            f"You are a Market Analyst. Analyze the following startup idea: '{idea}'.\n"
            f"Using the provided web research snippets, synthesize a comprehensive market analysis.\n"
            f"Output strictly as a JSON object with exactly these keys:\n"
            f"- 'market_size' (string, e.g. '$10B')\n"
            f"- 'growth_rate' (string, e.g. '15% CAGR')\n"
            f"- 'market_maturity' (string, e.g. 'Emerging', 'Mature')\n"
            f"- 'market_trends' (list of strings)\n"
            f"- 'opportunities' (list of strings)\n"
            f"- 'challenges' (list of strings)\n"
            f"- 'market_summary' (string paragraph)\n\n"
            f"IMPORTANT: You MUST return ONLY valid JSON. No markdown blocks, no explanatory text. Ensure all brackets are closed.\n"
            f"Research Snippets:\n{raw_text}\n"
        )

        logger.info("Market Opportunity Agent: Requesting LLM extraction for market insights.")
        parsed_analysis = None
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                raw_response = await self.llm_client.generate_response(
                    system_prompt="You are an expert market analyst. Return ONLY valid JSON.",
                    user_prompt=prompt if attempt == 0 else f"{prompt}\n\nWARNING: Your previous response was invalid JSON. Please fix formatting: {last_error}",
                    response_format={"type": "json_object"}
                )
                parsed_analysis = safe_parse_llm_json(raw_response)
                logger.info(f"Market Opportunity Agent: LLM data extraction successful on attempt {attempt + 1}.")
                break
            except MalformedLLMOutputError as e:
                logger.warning(f"Market Opportunity Agent: Malformed JSON output on attempt {attempt + 1}: {e}")
                last_error = str(e)
            except Exception as exc:
                logger.error(f"Market Opportunity Agent: LLM market analysis API call failed on attempt {attempt + 1}: {exc}.")
                last_error = str(exc)
                break # Break on network/API errors, only retry on JSON parsing failures

        if not parsed_analysis:
            logger.error(f"Market Opportunity Agent: Failed to generate valid market JSON after {max_retries} attempts. Using fallback.")
            return self._return_fallback(f"LLM failure or malformed JSON: {last_error}")

        logger.info("Market Opportunity Agent: Validating and structuring response generation.")

        # Ensure all required keys exist and enforce rigid typing to prevent downstream crashes
        analysis = {
            "market_size": str(parsed_analysis.get("market_size") or "Data unavailable"),
            "growth_rate": str(parsed_analysis.get("growth_rate") or "Data unavailable"),
            "market_maturity": str(parsed_analysis.get("market_maturity") or "Data unavailable"),
            "market_trends": self._validate_and_coerce_list(parsed_analysis.get("market_trends")),
            "opportunities": self._validate_and_coerce_list(parsed_analysis.get("opportunities")),
            "challenges": self._validate_and_coerce_list(parsed_analysis.get("challenges")),
            "market_summary": str(parsed_analysis.get("market_summary") or "No summary provided."),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"--- MARKET AGENT COMPLETE PAYLOAD ---")
        logger.info(json.dumps(analysis, indent=2))
        logger.info("-------------------------------------")

        logger.info("Market Opportunity Agent: Successful completion. Output ready for downstream agents.")
        self.context["market_analysis"] = analysis
        return analysis

    def _return_fallback(self, reason: str):
        analysis = {
            "market_size": "Unknown",
            "growth_rate": "Unknown",
            "market_maturity": "Unknown",
            "market_trends": [],
            "opportunities": [f"Opportunity parsing failed due to {reason}"],
            "challenges": [],
            "market_summary": f"Market analysis could not be completed. Reason: {reason}",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        self.context["market_analysis"] = analysis
        return analysis
