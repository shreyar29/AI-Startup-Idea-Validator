"""
web_search_agent.py

Purpose
-------
This module implements the Web Search Agent — the primary agent in the
Multi-Agent Startup Idea Validator. It orchestrates:

    1. Query Strategist  -> understands the startup idea, generates
                             categorized search queries (no web access).
    2. Search Service    -> executes those queries against Tavily.
    3. Result Processor  -> deduplicates, filters, and structures results.

The `search_startup()` function is the current production entry-point
used by app.py. It uses the Tavily API directly to perform a web search
and returns a structured JSON response matching the frontend's expected format.
"""

from __future__ import annotations
from services.tavily_service import search_web


def search_startup(startup_idea: str) -> dict:
    """
    Production entry-point used by app.py.
    Takes a raw startup idea string, performs a Tavily web search,
    and returns a structured response matching the frontend's data contract.
    """
    raw_data = search_web(startup_idea)

    # Tavily returns {"results": [...], "query": "...", ...}
    results = []
    if isinstance(raw_data, dict):
        results = raw_data.get("results", [])
    elif isinstance(raw_data, list):
        results = raw_data

    return {
        "metadata": {
            "status": "success",
            "agent": "WebSearchAgent",
            "total_categories_processed": 1,
            "total_results_found": len(results)
        },
        "identified_context": {
            "product_idea": startup_idea,
        },
        "search_queries": {
            "general_research": [startup_idea]
        },
        "search_results": {
            "general_research": results
        }
    }


# ============================================================
# WebSearchAgent Class (for future full pipeline usage)
# ============================================================

class WebSearchAgent:
    """
    Full orchestration class for future use when QueryStrategist
    and the complete multi-agent pipeline is active.
    """

    def __init__(self, query_strategist, search_service, result_processor) -> None:
        self._query_strategist = query_strategist
        self._search_service = search_service
        self._result_processor = result_processor

    async def run(self, startup_idea: str) -> dict:
        import asyncio
        from datetime import datetime, timezone

        query_data = await self._query_strategist.generate_search_queries(startup_idea)
        
        from utils.text_sanitizer import sanitize_category_queries
        sanitized_queries = sanitize_category_queries(query_data["queries"])

        async def fetch_category(category, queries):
            if not queries:
                return category, []
            res = await self._search_service.search(queries)
            return category, res

        tasks = [fetch_category(cat, q) for cat, q in sanitized_queries.items()]
        category_results = await asyncio.gather(*tasks)
        
        raw_results = {cat: res for cat, res in category_results}

        processed_results = self._result_processor.process(raw_results)

        total_queries = sum(len(q) for q in sanitized_queries.values())

        return {
            "metadata": {
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent": "WebSearchAgent",
                "version": "1.0",
                "total_categories_processed": len(sanitized_queries),
                "total_search_queries_executed": total_queries
            },
            "identified_context": query_data["identified_context"],
            "search_queries": sanitized_queries,
            "search_results": processed_results,
        }
