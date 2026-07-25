"""
market_agent.py

Purpose
-------
This module implements the Market Opportunity Agent.
It consumes the structured JSON output from the Web Search Agent (via the orchestrator)
and uses the LLM to synthesize the raw search results into a structured market analysis.

Responsibilities
-----------------
- Accept validation data (dict containing search_results).
- Format the input data for the LLM.
- Call the LLM (via OpenRouterClient) with MARKET_SYSTEM_PROMPT.
- Parse, validate, and return the structured market insights.
"""

import json
from typing import Any

from strategy.market_prompt import MARKET_SYSTEM_PROMPT
from llm.openrouter_client import OpenRouterClient
from utils.logger import get_logger
from utils.error_handler import LLMResponseError

logger = get_logger(__name__)

REQUIRED_KEYS = {
    "market_size": str,
    "growth_rate": str,
    "market_maturity": str,
    "market_trends": list,
    "opportunities": list,
    "challenges": list,
    "market_summary": str
}

class MarketAnalysisError(Exception):
    """Raised when the Market Opportunity Agent encounters an error analyzing data."""

class MarketOpportunityAgent:
    """
    Synthesizes raw search results into structured market insights.
    Relies on the OpenRouterClient for LLM communication.
    """

    def __init__(self, llm_client: OpenRouterClient) -> None:
        """
        Args:
            llm_client: An already-configured OpenRouter client instance.
        """
        self._llm_client = llm_client

    async def analyze_market(self, validation_data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze the market based on search results.

        Args:
            validation_data: The exact JSON output produced by the primary Web Search Agent.

        Returns:
            A structured dictionary containing market insights:
            {
                "market_size": "...",
                "growth_rate": "...",
                "market_maturity": "...",
                "market_trends": [],
                "opportunities": [],
                "challenges": [],
                "market_summary": "..."
            }
        """
        logger.info("Market Opportunity Agent started analysis.")
        
        if not validation_data:
            logger.error("Validation data is empty.")
            raise MarketAnalysisError("Input data must not be empty.")

        logger.info(f"Validation data keys: {validation_data.keys()}")

        validation_data_json = json.dumps(validation_data, indent=2)
        
        user_prompt = (
            "Here are the web search results for the startup idea:\n\n"
            f"{validation_data_json}\n\n"
            "Analyze these results and return the structured JSON output as strictly instructed."
        )

        max_retries = 2
        raw_response = ""

        for attempt in range(max_retries + 1):
            if attempt == 0:
                logger.info("Sending request to LLM to generate market analysis.")
                current_system = MARKET_SYSTEM_PROMPT
                current_user = user_prompt
            else:
                logger.warning("Retry attempt %d/%d for malformed JSON.", attempt, max_retries)
                current_system = "You are a JSON fixer. Return ONLY valid JSON matching the exact schema."
                current_user = (
                    "Your previous response was invalid JSON or did not match the schema. "
                    "Return ONLY corrected valid JSON without changing the meaning.\n\n"
                    f"Invalid JSON:\n{raw_response}"
                )

            raw_response = await self._call_llm(current_system, current_user)
            
            try:
                parsed_response = self._parse_llm_response(raw_response)
                self._validate_response_structure(parsed_response)
                logger.info("Market analysis generated and validated successfully.")
                return parsed_response 
            except LLMResponseError as exc:
                logger.warning("Failed to parse or validate JSON on attempt %d: %s", attempt, exc)
                if attempt == max_retries:
                    logger.error("All retry attempts failed. Raising exception.")
                    raise MarketAnalysisError(str(exc)) from exc

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send the prompt to the LLM and return the raw text response.
        """
        try:
            response_text = await self._llm_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format={"type": "json_object"}
            )
        except Exception as exc:
            logger.exception("LLM call failed during market analysis.")
            raise LLMResponseError("Failed to get a response from the LLM.") from exc

        if not response_text or not response_text.strip():
            logger.error("LLM returned an empty response.")
            raise LLMResponseError("LLM returned an empty response.")

        return response_text

    def _parse_llm_response(self, raw_response: str) -> dict[str, Any]:
        """
        Parse the LLM's raw text output into a Python dict safely.
        Strips markdown code fences and extraneous surrounding text.
        """
        cleaned = raw_response.strip()

        if "```" in cleaned:
            import re
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL | re.IGNORECASE)
            if match:
                cleaned = match.group(1).strip()
            else:
                cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
            cleaned = cleaned[start_idx:end_idx+1]

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.exception("Failed to parse LLM response as JSON.")
            raise LLMResponseError("LLM response was not valid JSON.") from exc

        if not isinstance(parsed, dict):
            raise LLMResponseError("LLM response JSON must be an object at the top level.")

        return parsed

    def _validate_response_structure(self, parsed: dict[str, Any]) -> None:
        """
        Validate that the parsed LLM response matches the required contract.
        """
        for key, expected_type in REQUIRED_KEYS.items():
            if key not in parsed:
                raise LLMResponseError(f"Missing required key: '{key}'")
            if not isinstance(parsed[key], expected_type):
                raise LLMResponseError(f"Key '{key}' must be of type {expected_type.__name__}")
            
            if expected_type == list:
                if not all(isinstance(item, str) for item in parsed[key]):
                    raise LLMResponseError(f"All items in '{key}' list must be strings.")
