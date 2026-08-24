import logging
import asyncio
from typing import Dict, Any, List
import time
from duckduckgo_search import DDGS
from tavily import AsyncTavilyClient
import json
import hashlib

logger = logging.getLogger("search_provider")

class SearchCache:
    """Simple in-memory LRU cache for search results to reduce API calls and latency."""
    def __init__(self, max_size=100, ttl_seconds=3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl_seconds

    def _generate_key(self, query: str, category: str) -> str:
        return hashlib.sha256(f"{query}:{category}".encode('utf-8')).hexdigest()

    def get(self, query: str, category: str) -> List[Dict[str, Any]]:
        key = self._generate_key(query, category)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                logger.debug(f"Search Cache HIT for '{query}' in '{category}'")
                return entry["data"]
            else:
                del self.cache[key]
        return None

    def set(self, query: str, category: str, data: List[Dict[str, Any]]):
        if len(self.cache) >= self.max_size:
            # Pop oldest item
            oldest = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest]
            
        key = self._generate_key(query, category)
        self.cache[key] = {
            "timestamp": time.time(),
            "data": data
        }


class SearchCircuitBreaker:
    """
    Provides robust search execution with fallback chains:
    Tavily -> Brave (Optional/Placeholder) -> DuckDuckGo
    """
    def __init__(self, tavily_api_key: str = None):
        self.tavily_api_key = tavily_api_key
        self.tavily_client = AsyncTavilyClient(api_key=tavily_api_key) if tavily_api_key else None
        self.cache = SearchCache()

    async def execute_search(self, query: str, category: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Executes search with caching and fallbacks."""
        cached = self.cache.get(query, category)
        if cached is not None:
            return cached

        results = []
        
        # 1. Try Tavily (Primary)
        if self.tavily_client:
            try:
                logger.info(f"Attempting Tavily search for: '{query}'")
                tavily_res = await asyncio.wait_for(
                    self.tavily_client.search(query=query, search_depth="advanced", max_results=max_results),
                    timeout=8.0
                )
                if tavily_res and "results" in tavily_res:
                    results = [{"url": r["url"], "content": r["content"], "title": r.get("title", ""), "relevance_score": r.get("score", 0.5) * 10} for r in tavily_res["results"]]
                    if results:
                        self.cache.set(query, category, results)
                        return results
            except asyncio.TimeoutError:
                logger.warning(f"Tavily search timed out for '{query}'. Falling back...")
            except Exception as e:
                logger.warning(f"Tavily search failed for '{query}': {e}. Falling back...")

        # 2. Brave (Placeholder for actual Brave Search API implementation if needed)
        # We can implement httpx calls here if a Brave key is provided.
        
        # 3. DuckDuckGo (Ultimate Fallback)
        try:
            logger.info(f"Attempting DuckDuckGo search for: '{query}'")
            ddg = DDGS()
            # DDGS is blocking, run in executor
            loop = asyncio.get_event_loop()
            ddg_results = await loop.run_in_executor(None, lambda: list(ddg.text(query, max_results=max_results)))
            
            if ddg_results:
                results = [{"url": r["href"], "content": r["body"], "title": r["title"], "relevance_score": 5.0} for r in ddg_results]
                if results:
                    self.cache.set(query, category, results)
                    return results
        except Exception as e:
            logger.error(f"DuckDuckGo fallback completely failed for '{query}': {e}")
            
        return []
