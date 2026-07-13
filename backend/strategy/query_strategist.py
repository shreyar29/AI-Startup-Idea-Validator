"""
query_strategist.py

Purpose
-------
This module implements the Query Strategist: the component responsible for
turning a raw startup idea into a categorized set of search queries by
calling the LLM (via OpenRouter) with the SYSTEM_PROMPT defined in
query_prompt.py.

Responsibilities
-----------------
- Accept a startup idea (plain text).
- Send it to the LLM alongside SYSTEM_PROMPT.
- Parse and validate the LLM's JSON response.
- Return a structured, typed result to the caller (web_search_agent.py).

This module NEVER:
- Searches the web or calls Tavily.
- Performs market analysis or validation.
- Generates reports or recommendations.

It assumes the following already exist elsewhere in the project:
- app.strategy.query_prompt.SYSTEM_PROMPT
- app.llm.openrouter_client (an async client with a `.generate_response()` method)
- app.utils.logger.get_logger
- app.utils.error_handler (custom exception types)
"""

from __future__ import annotations

import json
from typing import Any

from strategy.query_prompt import SYSTEM_PROMPT
from strategy.query_rules import validate_startup_idea, SEARCH_CATEGORIES
from llm.openrouter_client import OpenRouterClient
from utils.logger import get_logger
from utils.error_handler import LLMResponseError, QueryStrategistError

logger = get_logger(__name__)

REQUIRED_CONTEXT_FIELDS: tuple[str, ...] = (
    "product",
    "industry",
    "target_audience",
    "technology",
)


class QueryStrategist:
    """
    Converts a startup idea into categorized search queries by delegating
    understanding and query generation to the LLM, guided by SYSTEM_PROMPT.

    This class holds no search or analysis logic — it is a thin, focused
    orchestrator around a single LLM call plus response validation.
    """

    def __init__(self, llm_client: OpenRouterClient) -> None:
        """
        Args:
            llm_client: An already-configured OpenRouter client instance.
                        Injected rather than constructed here, so this class
                        stays easy to test and decoupled from client setup.
        """
        self._llm_client = llm_client

    async def generate_search_queries(self, startup_idea: str) -> dict[str, Any]:
        """
        Generate categorized search queries for a given startup idea.

        Args:
            startup_idea: Raw natural-language description of the startup
                idea, as provided by the user.

        Returns:
            A dictionary matching the contract defined in SYSTEM_PROMPT:
            {
                "identified_context": {...},
                "queries": {...}
            }

        Raises:
            QueryStrategistError: If the idea is empty/invalid, or if the
                LLM response cannot be parsed/validated into the expected
                structure.
        """
        logger.info("Startup idea received by Query Strategist. Validating input.")
        cleaned_idea = self._validate_input(startup_idea)
        logger.info("Input validation successful.")

        max_retries = 2
        raw_response = ""

        for attempt in range(max_retries + 1):
            if attempt == 0:
                logger.info("Sending request to OpenRouter to generate search queries.")
                current_system = SYSTEM_PROMPT
                current_user = cleaned_idea
            else:
                logger.warning("Retry attempt %d/%d for malformed JSON.", attempt, max_retries)
                current_system = "You are a JSON fixer. Return ONLY valid JSON."
                current_user = (
                    "Your previous response was invalid JSON. Return ONLY corrected "
                    "valid JSON without changing the meaning. Do not include markdown fences or explanations.\n\n"
                    f"Invalid JSON:\n{raw_response}"
                )

            raw_response = await self._call_llm(current_system, current_user)
            
            try:
                if attempt == 0:
                    logger.info("Response received from OpenRouter. Parsing JSON.")
                else:
                    logger.info("Repaired response received. Parsing JSON.")
                    
                parsed_response = self._parse_llm_response(raw_response)
                logger.info("Validating response structure.")
                self._validate_response_structure(parsed_response)

                logger.info("Queries generated successfully. Returning response.")
                return parsed_response

            except LLMResponseError as exc:
                logger.warning("Failed to parse or validate JSON on attempt %d: %s", attempt, exc)
                if attempt == max_retries:
                    logger.error("All retry attempts failed. Raising exception.")
                    raise

    def _validate_input(self, startup_idea: str) -> str:
        """
        Ensure the incoming startup idea is usable before sending it to the
        LLM. Uses centralized validation rules.
        """
        try:
            validate_startup_idea(startup_idea)
            return startup_idea.strip()
        except ValueError as exc:
            logger.error("Startup idea validation failed: %s", exc)
            raise QueryStrategistError(str(exc)) from exc

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send the prompt to the LLM and return the raw text response.
        Passes structured JSON response_format if supported.
        """
        try:
            response_text = await self._llm_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format={"type": "json_object"}
            )
        except Exception as exc:
            logger.exception("LLM call failed during query generation.")
            raise LLMResponseError(
                "Failed to get a response from the LLM."
            ) from exc

        if not response_text or not response_text.strip():
            logger.error("LLM returned an empty response.")
            raise LLMResponseError("LLM returned an empty response.")

        return response_text

    def _parse_llm_response(self, raw_response: str) -> dict[str, Any]:
        """
        Parse the LLM's raw text output into a Python dict safely.
        Strips markdown code fences and extranous surrounding text.
        """
        cleaned = raw_response.strip()

        # Remove markdown fences robustly
        if "```" in cleaned:
            import re
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL | re.IGNORECASE)
            if match:
                cleaned = match.group(1).strip()
            else:
                cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Ensure we only parse from the first { to the last }
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
            cleaned = cleaned[start_idx:end_idx+1]

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.exception("Failed to parse LLM response as JSON: %s", cleaned)
            raise LLMResponseError(
                "LLM response was not valid JSON."
            ) from exc

        if not isinstance(parsed, dict):
            logger.error("LLM response JSON is not an object at the top level.")
            raise LLMResponseError(
                "LLM response JSON must be an object at the top level."
            )

        return parsed

    def _validate_response_structure(self, parsed: dict[str, Any]) -> None:
        """
        Validate that the parsed LLM response matches the contract defined
        in SYSTEM_PROMPT.
        """
        if "identified_context" not in parsed or "queries" not in parsed:
            logger.error("Response missing 'identified_context' or 'queries'.")
            raise LLMResponseError(
                "LLM response is missing required top-level keys "
                "'identified_context' and/or 'queries'."
            )

        context = parsed["identified_context"]
        missing_context_fields = [
            field for field in REQUIRED_CONTEXT_FIELDS if field not in context
        ]
        if missing_context_fields:
            logger.error("Response missing context fields: %s", missing_context_fields)
            raise LLMResponseError(
                f"LLM response is missing context fields: "
                f"{missing_context_fields}"
            )

        queries = parsed["queries"]
        missing_categories = [
            category
            for category in SEARCH_CATEGORIES
            if category not in queries
        ]
        if missing_categories:
            logger.error("Response missing query categories: %s", missing_categories)
            raise LLMResponseError(
                f"LLM response is missing required query categories: "
                f"{missing_categories}"
            )

        for category, query_list in queries.items():
            if not isinstance(query_list, list) or not all(
                isinstance(q, str) for q in query_list
            ):
                logger.error("Query category '%s' is not a valid list of strings.", category)
                raise LLMResponseError(
                    f"Query category '{category}' must be a list of strings."
                )

if __name__ == "__main__":
    import asyncio
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    async def _test() -> None:
        try:
            client = OpenRouterClient()
            strategist = QueryStrategist(llm_client=client)
            
            sample_idea = "AI Resume Builder that automatically formats resumes and matches keywords to job descriptions."
            
            result = await strategist.generate_search_queries(sample_idea)
            
            print("\nGenerated Output:")
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            logging.error("Test failed: %s", e)

    asyncio.run(_test())
