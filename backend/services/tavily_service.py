import os
import httpx
from typing import Dict, Any, Optional
import asyncio
import logging

from ddgs import DDGS
from utils.error_handler import SearchServiceError
from core.config import settings

logger = logging.getLogger(__name__)

_MAX_RESULTS_PER_QUERY = 10
_SYNTHETIC_SCORE_DECAY = 0.05

class SearchProviderFallbackChain:
    def __init__(self, max_concurrent_searches=10):
        self.semaphore = asyncio.Semaphore(max_concurrent_searches)
        
    async def _search_tavily(self, query: str) -> list[dict]:
        api_key = settings.search.TAVILY_API_KEY
        if not api_key:
            raise ValueError("Tavily API key not found.")
        
        async with httpx.AsyncClient() as client:
            payload = {
                "api_key": api_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": _MAX_RESULTS_PER_QUERY
            }
            resp = await client.post("https://api.tavily.com/search", json=payload, timeout=15.0)
            if resp.status_code != 200:
                raise Exception(f"Tavily returned {resp.status_code}: {resp.text}")
            data = resp.json()
            results = []
            for idx, r in enumerate(data.get("results", [])):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 1.0 - (idx * _SYNTHETIC_SCORE_DECAY))
                })
            return results

    async def _search_brave(self, query: str) -> list[dict]:
        api_key = getattr(settings.search, "BRAVE_API_KEY", None)
        if not api_key:
            raise ValueError("Brave API key not found.")
            
        async with httpx.AsyncClient() as client:
            headers = {"Accept": "application/json", "Accept-Encoding": "gzip", "X-Subscription-Token": api_key}
            params = {"q": query, "count": _MAX_RESULTS_PER_QUERY}
            resp = await client.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params=params, timeout=15.0)
            if resp.status_code != 200:
                raise Exception(f"Brave returned {resp.status_code}: {resp.text}")
            data = resp.json()
            results = []
            for idx, r in enumerate(data.get("web", {}).get("results", [])):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("description", ""),
                    "score": 1.0 - (idx * _SYNTHETIC_SCORE_DECAY)
                })
            return results

    async def _search_ddgs(self, query: str) -> list[dict]:
        def _do_search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=_MAX_RESULTS_PER_QUERY))
                
        results = await asyncio.to_thread(_do_search)
        
        formatted_results = []
        for idx, res in enumerate(results):
            formatted_results.append({
                "title": res.get("title", ""),
                "url": res.get("href", ""),
                "content": res.get("body", ""),
                "score": 1.0 - (idx * _SYNTHETIC_SCORE_DECAY)
            })
        return formatted_results

    async def _safe_search(self, category: str, query: str):
        async with self.semaphore:
            diagnostics = {"tavily": "not_tried", "brave": "not_tried", "ddgs": "not_tried"}
            
            # Try Tavily
            try:
                res = await self._search_tavily(query)
                if res and len(res) >= 3:
                    logger.info(f"TavilySearchService: '{query[:20]}...' succeeded via Tavily.")
                    diagnostics["tavily"] = "success"
                    return res, diagnostics
                else:
                    diagnostics["tavily"] = "empty_or_insufficient"
            except Exception as e:
                diagnostics["tavily"] = f"error: {str(e)}"
                
            # Try Brave
            try:
                res = await self._search_brave(query)
                if res and len(res) >= 3:
                    logger.info(f"TavilySearchService: '{query[:20]}...' succeeded via Brave.")
                    diagnostics["brave"] = "success"
                    return res, diagnostics
                else:
                    diagnostics["brave"] = "empty_or_insufficient"
            except Exception as e:
                diagnostics["brave"] = f"error: {str(e)}"
                
            # Try DDGS
            try:
                res = await self._search_ddgs(query)
                if res:
                    logger.info(f"TavilySearchService: '{query[:20]}...' succeeded via DDGS.")
                    diagnostics["ddgs"] = "success"
                    return res, diagnostics
                else:
                    diagnostics["ddgs"] = "empty_or_insufficient"
            except Exception as e:
                diagnostics["ddgs"] = f"error: {str(e)}"
                logger.debug(f"Search completely failed for query '{query[:30]}...': {e}")
                
            return [], diagnostics

    async def search(self, category: str, queries: list[str]) -> list[dict]:
        if not queries:
            return []
            
        logger.info(f"SearchService: Executing {len(queries)} queries for '{category}'.")
        
        tasks = [self._safe_search(category, q) for q in queries]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        flat_results = []
        errors = []
        diagnostic_log = {}
        
        for idx, res in enumerate(results_list):
            q_snippet = queries[idx][:20] + "..."
            if isinstance(res, Exception):
                logger.warning(f"SearchService: Query '{q_snippet}' threw exception: {res}")
                errors.append(res)
                diagnostic_log[q_snippet] = {"error": str(res)}
            else:
                snippets, diags = res
                diagnostic_log[q_snippet] = diags
                if snippets:
                    flat_results.extend(snippets)
                else:
                    logger.warning(f"SearchService: Query '{q_snippet}' yielded no results after all fallbacks.")
                    
        # Log structured diagnostics
        logger.info(f"Search Diagnostics for '{category}': {diagnostic_log}")
                
        if errors and not flat_results:
            raise SearchServiceError(f"All searches failed for category '{category}'")
            
        # Minimum threshold requirement (Issue 1)
        if len(flat_results) < 3:
            logger.warning(f"SearchService: Extremely low results for '{category}'. Check network or query validity.")
            
        logger.info(f"SearchService: Live search batch complete. Total raw results: {len(flat_results)}.")
        return flat_results

# Export the same name so we don't break existing imports
TavilySearchService = SearchProviderFallbackChain
