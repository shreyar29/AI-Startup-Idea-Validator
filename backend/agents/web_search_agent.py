"""

web_search_agent.py

Purpose
-------
This module implements the Web Search Agent — the Milestone 1 agent in the
Multi-Agent Startup Idea Validator. It is the single orchestration point
that ties together three independently-responsible modules:

    1. Query Strategist  -> understands the startup idea, generates
                             categorized search queries (no web access).
    2. Search Service     -> executes those queries against Tavily
                             (no query generation, no cleaning).
    3. Result Processor    -> deduplicates, filters, and structures the
                             raw search results (no searching, no query
                             generation).

The Web Search Agent itself contains NO search logic, NO query-generation
logic, and NO result-cleaning logic. Its only job is to call each module in
the correct order, pass data between them, handle failures at the
orchestration level, and return one final structured JSON object that
becomes the input contract for the future Market Analysis Agent.
"""

from __future__ import annotations
import asyncio
import json
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from strategy.query_strategist import QueryStrategist
from services.tavily_service import TavilySearchService
from processors.result_processor import ResultProcessor
from utils.logger import get_logger
from guardrails.manager import GuardrailManager
from core.config import settings
from utils.error_handler import (
    QueryStrategistError,
    LLMResponseError,
    SearchServiceError,
    ResultProcessingError,
    WebSearchAgentError,
)

logger = get_logger(__name__)

_TRUSTED_DOMAINS = settings.guardrails.trusted_domains_list


class WebSearchAgent:
    """
    Orchestrates the Query Strategist, Search Service, and Result Processor
    to turn a raw startup idea into a structured, research-backed JSON output.
    """

    def __init__(
        self,
        query_strategist: QueryStrategist,
        search_service: TavilySearchService,
        result_processor: ResultProcessor,
        shared_context: dict[str, Any] = None,
    ) -> None:
        self._query_strategist = query_strategist
        self._search_service = search_service
        self._result_processor = result_processor
        self.context = shared_context or {}
        self.peers = {}
        self._analysis_task = None

    def connect_peers(self, peers: dict):
        self.peers = peers

    def _publish_progress(self, request_id: str, agent: str, status: str, message: str) -> None:
        if not request_id:
            return
        from utils.progress import ProgressManager
        
        task = asyncio.create_task(ProgressManager.publish(request_id, agent, status, message))
        
        def _on_done(t: asyncio.Task):
            try:
                t.result()
            except Exception as e:
                logger.error("Failed to publish progress event in Web Search Agent: %s", e)
                
        task.add_done_callback(_on_done)

    async def get_analysis(self):
        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(self._perform_analysis())
        return await self._analysis_task
        
    async def _perform_analysis(self):
        startup_idea = self.context.get("idea", {}).get("description")
        if not startup_idea:
            raise ValueError("Startup idea missing from context.")
        
        result = await self.run(startup_idea)
        search_results = result.get("search_results", {})
        
        logger.info("--- WEB SEARCH AGENT COMPLETE RESEARCH PAYLOAD ---")
        logger.info("Categories Researched: %s", list(search_results.keys()))
        logger.debug("Full Payload:\n%s", json.dumps(search_results, indent=2))
        logger.info("--------------------------------------------------")
        
        return search_results

    async def run(self, startup_idea: str) -> dict[str, Any]:
        """
        Execute the full Web Search Agent pipeline for a given startup idea.
        """
        logger.info("Web Search Agent pipeline started. Idea: %s", startup_idea)
        
        request_id = self.context.get("request_id")

        try:
            # Stage 1: Generate Queries
            self._publish_progress(request_id, "Query Strategist", "running", "Generating intelligent search queries...")
                
            query_data = await self._generate_queries(startup_idea)
            
            self._publish_progress(request_id, "Query Strategist", "completed", "Generated specialized search queries.")
            
            # Stage 2: Sanitize Queries (decoupling from LLM artifacts)
            logger.info("Sanitizing generated search queries.")
            
            sanitized_queries = GuardrailManager.validate_queries(query_data["queries"])
            logger.info("Query sanitization completed.")

            self._publish_progress(request_id, "Web Search Agent", "running", "Executing live market intelligence search...")
                
            # Stage 3: Execute Searches
            raw_results = await self._execute_searches(sanitized_queries)

            # Stage 4: Process Results
            # (3) Search Guardrail
            filtered_raw_results = GuardrailManager.filter_search_results(raw_results)
            processed_results = self._process_results(filtered_raw_results, startup_idea)

            # --- Filter & Rank Results ---
            refined_results, category_metadata = self._filter_and_rank_results(processed_results)
            
            # Synchronize results back into shared context for downstream agents
            self.context["research"] = refined_results

            # Stage 5: Assemble Final Output
            final_output = self._assemble_output(
                query_data=query_data,
                sanitized_queries=sanitized_queries,
                processed_results=refined_results,
                category_metadata=category_metadata,
            )

            logger.info("Web Search Agent pipeline completed successfully.")
            
            self._publish_progress(request_id, "Web Search Agent", "completed", "Market intelligence gathered.")
                
            return final_output

        except WebSearchAgentError as exc:
            logger.error("Web Search Agent pipeline failed: %s", exc)
            self._publish_progress(request_id, "Web Search Agent", "failed", "Market intelligence gathering failed.")
            return self._return_degraded(startup_idea, str(exc))
        except Exception as exc:
            logger.exception("Unexpected error in Web Search Agent pipeline.")
            self._publish_progress(request_id, "Web Search Agent", "failed", "Unexpected error during market intelligence.")
            return self._return_degraded(startup_idea, str(exc))

    def _return_degraded(self, startup_idea: str, reason: str) -> dict[str, Any]:
        return {
            "metadata": {
                "status": "failed",
                "agent": "WebSearchAgent",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": reason
            },
            "identified_context": {"product": startup_idea[:100]},
            "search_queries": {},
            "search_results": {}
        }

    async def _generate_queries(self, startup_idea: str) -> dict[str, Any]:
        logger.info("Stage 1/3: Query generation started.")
        try:
            result = await self._query_strategist.run({"startup_idea": startup_idea})

            logger.debug("\n========== QUERY STRATEGIST OUTPUT ==========\n%s\n=============================================\n", json.dumps(result, indent=2))

            logger.info("Stage 1/3: Query generation completed successfully.")
            return result

        except (QueryStrategistError, LLMResponseError) as exc:
            logger.exception("Query generation stage failed.")
            request_id = self.context.get("request_id")
            self._publish_progress(request_id, "Query Strategist", "failed", "Failed to generate search queries.")
            raise WebSearchAgentError(
                "Web Search Agent failed during query generation."
            ) from exc

    async def _execute_searches(
        self,
        categorized_queries: dict[str, list[str]],
    ) -> dict[str, list[dict[str, Any]]]:
        logger.info("Stage 2/3: Tavily search started for each category.")

        raw_results: dict[str, list[dict[str, Any]]] = {}
        semaphore = asyncio.Semaphore(3)

        async def _bounded_search(category: str, queries: list[str]):
            if not queries:
                logger.info("Skipping category '%s' — no queries to execute.", category)
                return category, []

            async with semaphore:
                logger.info("Searching category '%s' (%d queries).", category, len(queries))
                res = await self._search_with_retries(category, queries)
                return category, res

        tasks = [_bounded_search(cat, qs) for cat, qs in categorized_queries.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, Exception):
                logger.exception("A bounded search task failed with an exception.")
                raise WebSearchAgentError("A bounded search task failed") from res
            cat, res_list = res
            raw_results[cat] = res_list

        logger.info("Stage 2/3: Tavily search completed for all categories.")
        return raw_results

    async def _search_with_retries(
        self, category: str, queries: list[str], max_retries: int = 2
    ) -> list[dict[str, Any]]:
        """Executes a search against Tavily with exponential backoff retries."""
        for attempt in range(max_retries + 1):
            try:
                return await self._search_service.search(category, queries)
            except SearchServiceError as exc:
                if attempt < max_retries:
                    backoff = 2 ** attempt
                    logger.warning(
                        "Tavily search attempt %d failed for category '%s'. Retrying in %d seconds...", 
                        attempt + 1, category, backoff
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.exception("All Tavily retry attempts failed for category '%s'.", category)
                    raise WebSearchAgentError(f"Web Search Agent failed while searching category '{category}'.") from exc

    def _process_results(
        self,
        raw_results: dict[str, list[dict[str, Any]]],
        startup_idea: str = ""
    ) -> dict[str, list[dict[str, Any]]]:
        logger.info("Stage 3/3: Result processing started.")
        try:
            processed = self._result_processor.process(raw_results, startup_idea)
            logger.info("Stage 3/3: Result processing completed successfully.")
            return processed
        except ResultProcessingError as exc:
            logger.exception("Result processing stage failed.")
            raise WebSearchAgentError("Web Search Agent failed during result processing.") from exc

    def _assemble_output(
        self,
        query_data: dict[str, Any],
        sanitized_queries: dict[str, list[str]],
        processed_results: dict[str, list[dict[str, Any]]],
        category_metadata: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        Combine the context, cleaned queries, results, and execution metadata
        into the single JSON contract exposed to downstream agents.
        """
        total_queries = sum(len(queries) for queries in sanitized_queries.values())
        
        stats = getattr(self._result_processor, "last_stats", {})
        
        metadata = {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "WebSearchAgent",
            "version": "1.0",
            "total_categories_processed": len(sanitized_queries),
            "total_search_queries_executed": total_queries
        }
        
        if stats:
            metadata.update(stats)
            
        if category_metadata:
            metadata["category_metadata"] = category_metadata
            
        return {
            "metadata": metadata,
            "identified_context": query_data["identified_context"],
            "search_queries": sanitized_queries,
            "search_results": processed_results,
        }

    def _filter_and_rank_results(
        self, processed_results: dict[str, list[dict[str, Any]]]
    ) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
        
        refined_results = {}
        category_metadata = {}
        
        for category, results in processed_results.items():
            results_found = len(results)
            
            valid_results = []
            for r in results:
                url = str(r.get("url") or "")
                content = str(r.get("content") or "")
                
                # Filter out missing URL or empty content
                if not url.strip() or not content.strip():
                    continue
                    
                # Filter out extremely short content
                if len(content.strip()) < 40:
                    continue
                    
                # Do not filter out by relevance, just use it for sorting
                try:
                    relevance_score = float(r.get("relevance_score", r.get("score", 0.0)))
                except (ValueError, TypeError):
                    relevance_score = 0.0
                
                valid_results.append((relevance_score, r))
                
            # Sort by relevance descending
            valid_results.sort(key=lambda x: x[0], reverse=True)
            
            # Deduplicate domains and keep top 5
            final_cat_results = []
            seen_domains = set()
            trusted_count = 0
            
            for score, r in valid_results:
                url = r.get("url", "")
                try:
                    domain = urlparse(url).netloc.lower()
                    if domain.startswith("www."):
                        domain = domain[4:]
                except Exception:
                    domain = url
                    
                if domain in seen_domains:
                    continue
                    
                seen_domains.add(domain)
                final_cat_results.append(r)
                
                if any(td in domain for td in _TRUSTED_DOMAINS):
                    trusted_count += 1
                
                if len(final_cat_results) >= 5:
                    break
                    
            # 1. Never Return Empty Results if original had data
            fallback_used = False
            if len(final_cat_results) == 0 and results_found > 0:
                fallback_used = True
                final_cat_results = results  # Fallback to original results
                # Compute trusted sources for metadata accurately
                for r in final_cat_results:
                    if any(td in str(r.get("url", "")).lower() for td in _TRUSTED_DOMAINS):
                        trusted_count += 1
                        
            logger.info(f"Category '{category}' | Original: {results_found} | After filtering: {len(final_cat_results)} | Fallback used: {fallback_used}")
                    
            refined_results[category] = final_cat_results
            category_metadata[category] = {
                "results_found": results_found,
                "results_kept": len(final_cat_results),
                "trusted_sources": trusted_count,
                "fallback_used": fallback_used
            }
            
        return refined_results, category_metadata

# ============================================================
# STANDALONE TEST BLOCK WITH MOCKS
# ============================================================
if __name__ == "__main__":
    import json
    import logging

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # Mock Dependencies to demonstrate orchestration without actual network/LLM calls
    class MockQueryStrategist(QueryStrategist):
        def __init__(self): pass
        async def generate_search_queries(self, idea: str) -> dict[str, Any]:
            return {
                "identified_context": {"product": "AI Resume Builder", "industry": "HR Tech", "target_audience": "Job seekers", "technology": "AI"},
                "queries": {"competitors": ["AI resume   builder??? competitors", "top AI tools"]}
            }

    class MockTavilyService(TavilySearchService):
        def __init__(self): self._fail_once = True
        async def search(self, category: str, queries: list[str]) -> list[dict[str, Any]]:
            # Simulate a transient failure on the first call to test retry logic
            if self._fail_once:
                self._fail_once = False
                raise SearchServiceError("Simulated transient Tavily timeout")
            return [{"url": "https://example.com", "content": "Sample content for " + queries[0]}]

    class MockResultProcessor(ResultProcessor):
        def __init__(self): pass
        def process(self, raw_results: dict[str, list[dict[str, Any]]], idea: str = "") -> dict[str, list[dict[str, Any]]]:
            return {cat: [{"cleaned_url": r["url"]} for r in res] for cat, res in raw_results.items()}

    async def _test():
        agent = WebSearchAgent(MockQueryStrategist(), MockTavilyService(), MockResultProcessor())
        try:
            result = await agent.run("AI Resume Builder")
            print("\n=== Final Web Search Agent Output ===")
            print(json.dumps(result, indent=2))
        except Exception as e:
            logger.error("Test failed: %s", e)

    asyncio.run(_test())