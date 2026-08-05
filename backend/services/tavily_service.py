from typing import Dict, Any, Optional
import asyncio
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class TavilySearchService:
    def __init__(self, max_concurrent_searches=10):
        self.semaphore = asyncio.Semaphore(max_concurrent_searches)

    async def _safe_search(self, category: str, query: str):
        async with self.semaphore:
            try:
                # Due to Tavily 432 limit errors, we fallback to DDGS for free web search
                from ddgs import DDGS
                
                def _do_search():
                    with DDGS() as ddgs:
                        return list(ddgs.text(query, max_results=10))
                        
                results = await asyncio.to_thread(_do_search)
                
                tavily_formatted_results = []
                for idx, res in enumerate(results):
                    tavily_formatted_results.append({
                        "title": res.get("title", ""),
                        "url": res.get("href", ""),
                        "content": res.get("body", ""),
                        "score": 1.0 - (idx * 0.05)
                    })
                return tavily_formatted_results
            except Exception as e:
                logger.error(f"Search failed for query '{query}': {e}")
                return []

    async def search(self, category: str, queries: list[str]) -> list[dict]:
        if not queries:
            return []
            
        logger.info(f"TavilySearchService (DDG Fallback): Executing {len(queries)} live web searches for '{category}'.")
        
        tasks = [self._safe_search(category, q) for q in queries]
        results_list = await asyncio.gather(*tasks)
        
        flat_results = []
        for i, res in enumerate(results_list):
            query_name = queries[i]
            if res:
                logger.info(f"TavilySearchService: Query '{query_name}' retrieved {len(res)} valid results.")
                flat_results.extend(res)
            else:
                logger.warning(f"TavilySearchService: Query '{query_name}' yielded no results or failed.")
                
        logger.info(f"TavilySearchService: Live search batch complete. Total raw results: {len(flat_results)}.")
        return flat_results
