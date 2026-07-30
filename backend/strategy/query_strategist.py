"""
query_strategist.py

Purpose
-------
Converts a startup idea into categorized search queries by delegating
understanding and query generation to the LLM.
"""

from __future__ import annotations

import json
from typing import Any
from datetime import datetime, timezone

from strategy.query_prompt import SYSTEM_PROMPT
from strategy.query_rules import validate_startup_idea, SEARCH_CATEGORIES
from llm.openrouter_client import OpenRouterClient
from utils.logger import get_logger
from utils.error_handler import LLMResponseError, QueryStrategistError, safe_parse_llm_json

logger = get_logger(__name__)

REQUIRED_CONTEXT_FIELDS = (
    "product",
    "industry",
    "target_audience",
    "technology",
)


class QueryStrategist:
    """
    Converts a startup idea into categorized search queries.
    """

    def __init__(self, llm_client: OpenRouterClient) -> None:
        self._llm_client = llm_client

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the query strategist agent.
        
        Args:
            input_data: Dictionary containing "startup_idea".
            
        Returns:
            Dictionary containing metadata, identified_context, and queries.
        """
        startup_idea = input_data.get("startup_idea")
        if not startup_idea:
            raise QueryStrategistError("Missing 'startup_idea' in input_data")

        logger.info("Query Strategist starting for idea.")
        cleaned_idea = self._validate_input(startup_idea)

        max_retries = 2
        raw_response = ""

        for attempt in range(max_retries + 1):
            if attempt == 0:
                current_system = SYSTEM_PROMPT
                current_user = cleaned_idea
            else:
                logger.warning("Retry attempt %d for Query Strategist", attempt)
                current_system = "You are a JSON fixer. Return ONLY valid JSON."
                current_user = (
                    "Your previous response was invalid JSON. Return ONLY corrected "
                    "valid JSON without changing the meaning.\n\n"
                    f"Invalid JSON:\n{raw_response}"
                )

            try:
                raw_response = await self._call_llm(current_system, current_user)
                parsed_response = safe_parse_llm_json(raw_response)
                self._validate_response_structure(parsed_response)
                
                parsed_response["metadata"] = {
                    "agent": "QueryStrategist",
                    "status": "success",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                logger.info("Query Strategist completed successfully.")
                return parsed_response 
            except Exception as exc:
                logger.warning("Query Strategist attempt %d failed: %s", attempt, exc)
                if attempt == max_retries:
                    logger.error("All retries failed for Query Strategist. Using mock fallback.")
                    return {
                        "metadata": {
                            "agent": "QueryStrategist",
                            "status": "fallback",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        },
                        "identified_context": "Fallback Context",
                        "queries": {
                            "competitors": [f"{cleaned_idea} competitors"],
                            "market_data": [f"{cleaned_idea} market size"],
                            "target_audience": [f"who uses {cleaned_idea}"]
                        }
                    }

    def _validate_input(self, startup_idea: str) -> str:
        try:
            validate_startup_idea(startup_idea)
            return startup_idea.strip()
        except ValueError as exc:
            logger.error("Validation failed: %s", exc)
            raise QueryStrategistError(str(exc)) from exc

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response_text = await self._llm_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format={"type": "json_object"}
            )
            return response_text
        except Exception as exc:
            logger.exception("LLM call failed.")
            raise LLMResponseError("LLM call failed") from exc

    def _validate_response_structure(self, parsed: dict[str, Any]) -> None:
        if "identified_context" not in parsed or "queries" not in parsed:
            raise LLMResponseError("Missing 'identified_context' or 'queries'")
        
        context = parsed["identified_context"]
        for field in REQUIRED_CONTEXT_FIELDS:
            if field not in context:
                raise LLMResponseError(f"Missing context field: {field}")
                
        queries = parsed["queries"]
        for category in SEARCH_CATEGORIES:
            if category not in queries:
                raise LLMResponseError(f"Missing query category: {category}")
