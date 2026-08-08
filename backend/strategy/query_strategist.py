"""
query_strategist.py

Purpose
-------
Converts a startup idea into categorized search queries by delegating
understanding and query generation to the LLM.
"""

from __future__ import annotations

import asyncio
import random
from typing import Any
from datetime import datetime, timezone

from strategy.query_prompt import SYSTEM_PROMPT, REPAIR_SYSTEM_PROMPT, REPAIR_USER_PROMPT_TEMPLATE
from strategy.query_rules import validate_startup_idea, SEARCH_CATEGORIES
from llm.gemini_client import GeminiClient
from utils.logger import get_logger
from utils.error_handler import LLMResponseError, QueryStrategistError, safe_parse_llm_json, MalformedLLMOutputError
from core.config import settings

logger = get_logger(__name__)

REQUIRED_CONTEXT_FIELDS = (
    "product",
    "industry",
    "target_audience",
    "technology",
)

EXPECTED_TOP_LEVEL_KEYS = {"identified_context", "queries", "_parse_metrics"}


class QueryStrategist:
    """
    Converts a startup idea into categorized search queries.
    """

    def __init__(self, llm_client: GeminiClient) -> None:
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

        max_retries = settings.agent.QUERY_STRATEGIST_MAX_RETRIES
        raw_response = ""
        last_error = "Unknown error"

        for attempt in range(max_retries + 1):
            if attempt == 0:
                current_system = SYSTEM_PROMPT
                current_user = f"<startup_idea>\n{cleaned_idea}\n</startup_idea>"
            else:
                logger.warning("Retry attempt %d for Query Strategist", attempt)
                current_system = REPAIR_SYSTEM_PROMPT
                current_user = REPAIR_USER_PROMPT_TEMPLATE.format(raw_response=raw_response)

            try:
                raw_response = await self._call_llm(current_system, current_user)
                
                safe_log_response = raw_response if len(raw_response) <= 5000 else raw_response[:2500] + "\n...[TRUNCATED]...\n" + raw_response[-2500:]
                logger.debug("\n========== RAW GEMINI RESPONSE ==========\n%s\n=========================================", safe_log_response)

                parsed_response = safe_parse_llm_json(
                    raw_response,
                    required_keys=["identified_context", "queries"],
                    retry_attempt=attempt
                )
                
                # Extract _parse_metrics injected by safe_parse_llm_json. It is internal telemetry
                # that does not belong in the final domain schema, but its values are saved to metadata.
                parse_metrics = parsed_response.pop("_parse_metrics", {})
                repaired_fields = self._validate_response_structure(parsed_response, cleaned_idea)
                
                schema_valid = len(repaired_fields) == 0
                
                if repaired_fields:
                    logger.info("Repaired fields during validation: %s", repaired_fields)
                
                parsed_response["metadata"] = {
                    "agent": "QueryStrategist",
                    "status": "success",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "raw_parse_success": parse_metrics.get("raw_parse_success", True),
                    "json_repair_used": parse_metrics.get("json_repair_used", False),
                    "schema_valid": schema_valid,
                    "validation_repairs": repaired_fields,
                    "retry_attempt": attempt
                }
                logger.info("Query Strategist completed successfully after %d retries.", attempt)
                return parsed_response 
            except MalformedLLMOutputError as exc:
                logger.warning("Query Strategist attempt %d experienced validation failure: %s", attempt, exc)
                last_error = str(exc)
                if attempt < max_retries:
                    sleep_time = 1.0 * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning("Backing off for %.1fs before next validation repair attempt.", sleep_time)
                    await asyncio.sleep(sleep_time)
            except LLMResponseError as exc:
                logger.error("Query Strategist encountered permanent API failure: %s", exc)
                last_error = str(exc)
                break
            except Exception as exc:
                logger.error("Query Strategist encountered permanent failure: %s", exc)
                last_error = str(exc)
                break

        logger.error("Query Strategist activating fallback mode. Reason: %s", last_error)
        return {
            "metadata": {
                "agent": "QueryStrategist",
                "status": "degraded",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": last_error,
                "degraded_mode_reason": "Exhausted retries or encountered permanent error."
            },
            "identified_context": {
                "product": cleaned_idea[:100],
                "industry": "Unknown",
                "target_audience": "Unknown",
                "technology": "Unknown"
            },
            "queries": {
                category: self._generate_fallback_query(cleaned_idea, category) 
                for category in SEARCH_CATEGORIES
            }
        }

    def _generate_fallback_query(self, idea: str, category: str) -> list[str]:
        """
        Helper to generate a safe, predictable query if the LLM fails completely
        or produces an irrecoverable schema violation for a specific category.
        """
        return [f"{idea[:50].strip()} {category.replace('_', ' ')}"]

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
                response_format={"type": "json_object"},
                temperature=0.0
            )
            return response_text
        except Exception as exc:
            logger.exception("LLM call failed.")
            raise LLMResponseError("LLM call failed") from exc

    def _validate_response_structure(self, parsed: dict[str, Any], startup_idea: str) -> list[str]:
        repaired_fields = []
        
        for key in list(parsed.keys()):
            if key not in EXPECTED_TOP_LEVEL_KEYS:
                logger.info("Pruning extraneous top-level key: %s", key)
                del parsed[key]
                repaired_fields.append(f"pruned_key.{key}")

        if "identified_context" not in parsed or not isinstance(parsed["identified_context"], dict):
            logger.warning("Missing required key 'identified_context' before validation injects defaults.")
            parsed["identified_context"] = {}
            repaired_fields.append("identified_context")
        if "queries" not in parsed or not isinstance(parsed["queries"], dict):
            logger.warning("Missing required key 'queries' before validation injects defaults.")
            parsed["queries"] = {}
            repaired_fields.append("queries")
            
        context = parsed["identified_context"]
        for field in REQUIRED_CONTEXT_FIELDS:
            val = context.get(field)
            if not isinstance(val, str) or not val.strip() or val.strip().lower() in ["n/a", "none", "null"]:
                if field not in context:
                    logger.warning("Missing schema key: context.%s before validation injects defaults.", field)
                else:
                    logger.warning("Invalid or empty schema key: context.%s before validation injects defaults.", field)
                context[field] = "Unknown"
                repaired_fields.append(f"context.{field}")
            else:
                context[field] = val.strip()
                
        queries = parsed["queries"]
        seen_queries = set()
        for category in SEARCH_CATEGORIES:
            cat_queries = queries.get(category)
            
            if isinstance(cat_queries, str):
                logger.info("Auto-repairing string query into array for: queries.%s", category)
                cat_queries = [cat_queries]
                queries[category] = cat_queries
            
            if not isinstance(cat_queries, list) or not cat_queries:
                logger.warning("Missing or empty array for: queries.%s before validation injects defaults.", category)
                queries[category] = self._generate_fallback_query(startup_idea, category)
                repaired_fields.append(f"queries.{category}")
                seen_queries.add(queries[category][0].lower())
                continue
            
            first_query = cat_queries[0]
            if not isinstance(first_query, str) or not first_query.strip():
                logger.warning("Invalid query string in: queries.%s before validation injects defaults.", category)
                queries[category] = self._generate_fallback_query(startup_idea, category)
                repaired_fields.append(f"queries.{category}_type_repair")
                seen_queries.add(queries[category][0].lower())
                continue
                
            clean_query = first_query.strip()
            
            query_lower = clean_query.lower()
            if query_lower in seen_queries:
                logger.warning("Duplicate query detected in %s. Modifying intent.", category)
                clean_query = f"{clean_query} {category.replace('_', ' ')}"
                repaired_fields.append(f"queries.{category}_dedupe")
                seen_queries.add(clean_query.lower())
            else:
                seen_queries.add(query_lower)
                
            queries[category] = [clean_query]
            if len(cat_queries) > 1:
                repaired_fields.append(f"queries.{category}_truncated")
                
        return repaired_fields
