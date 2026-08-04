from dotenv import load_dotenv
import os
import asyncio
import logging
import httpx

load_dotenv()

logger = logging.getLogger(__name__)


class TavilySearchService:
    def __init__(self, max_concurrent_searches=10):
        self.semaphore = asyncio.Semaphore(max_concurrent_searches)

    async def _safe_search(self, client, category: str, query: str):
        api_key = os.getenv("TAVILY_API_KEY")
        
        # Base configuration for high quality results
        exclude_domains = [
            "wikipedia.org", "wiktionary.org", "dictionary.com", 
            "merriam-webster.com", "thesaurus.com", "cambridge.org", 
            "urbandictionary.com", "macmillandictionary.com", "collinsdictionary.com",
            "quora.com", "reddit.com"
        ]
        
        search_depth = "advanced"
        
        # Category specific optimizations (could include include_domains here if desired)
        if category in ["market_size", "competitors", "trends"]:
            search_depth = "advanced"
        
        payload = {
            "api_key": api_key, 
            "query": query,
            "search_depth": search_depth,
            "exclude_domains": exclude_domains,
            "include_answer": False,
            "include_raw_content": False,
            "max_results": 10
        }
        
        async with self.semaphore:
            try:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                if "results" in data:
                    return data["results"]
                return data
            except Exception as e:
                logger.error(f"Search failed for query '{query}': {e}")
            return []

    async def search(self, category: str, queries: list[str]) -> list[dict]:
        
        if not queries:
            return []
            
        logger.info(f"TavilySearchService: Executing {len(queries)} live web searches for '{category}'.")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            tasks = [self._safe_search(client, category, q) for q in queries]
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
