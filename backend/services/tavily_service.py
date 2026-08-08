from typing import Dict, Any, Optional
import asyncio
import logging

from ddgs import DDGS
from utils.error_handler import SearchServiceError

logger = logging.getLogger(__name__)

_MAX_RESULTS_PER_QUERY = 10
_SYNTHETIC_SCORE_DECAY = 0.05
class TavilySearchService:
    def __init__(self, max_concurrent_searches=10):
        self.semaphore = asyncio.Semaphore(max_concurrent_searches)

    async def _safe_search(self, category: str, query: str):
        async with self.semaphore:
            try:
                # Due to Tavily 432 limit errors, we fallback to DDGS for free web search
                def _do_search():
                    with DDGS() as ddgs:
                        return list(ddgs.text(query, max_results=_MAX_RESULTS_PER_QUERY))
                        
                results = await asyncio.to_thread(_do_search)
                
                tavily_formatted_results = []
                for idx, res in enumerate(results):
                    tavily_formatted_results.append({
                        "title": res.get("title", ""),
                        "url": res.get("href", ""),
                        "content": res.get("body", ""),
                        "score": 1.0 - (idx * _SYNTHETIC_SCORE_DECAY)
                    })
                return tavily_formatted_results
            except Exception as e:
                logger.debug(f"Search failed for query '{query[:30]}...': {e}")
                raise SearchServiceError(f"DDGS search failed: {e}") from e

    async def search(self, category: str, queries: list[str]) -> list[dict]:
        if not queries:
            return []
            
        logger.info(f"TavilySearchService (DDG Fallback): Executing {len(queries)} live web searches for '{category}'.")
        
        tasks = [self._safe_search(category, q) for q in queries]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        flat_results = []
        errors = []
        for res in results_list:
            if isinstance(res, Exception):
                logger.warning(f"TavilySearchService: A query failed in category '{category}'")
                errors.append(res)
            elif res:
                logger.debug(f"TavilySearchService: Retrieved {len(res)} valid results for a query.")
                flat_results.extend(res)
            else:
                logger.warning(f"TavilySearchService: A query yielded no results.")
                
        if errors and not flat_results:
            raise SearchServiceError(f"All searches failed for category '{category}'")
                
        logger.info(f"TavilySearchService: Live search batch complete. Total raw results: {len(flat_results)}.")
        return flat_results
