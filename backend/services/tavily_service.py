from dotenv import load_dotenv
import os

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError(
                "TAVILY_API_KEY is not set. Please add it to your .env file."
            )
        from tavily import TavilyClient
        _client = TavilyClient(api_key=api_key)
    return _client


def search_web(query):
    return _get_client().search(query)


class TavilySearchService:
    def __init__(self, max_concurrent_searches=10):
        import asyncio
        self.semaphore = asyncio.Semaphore(max_concurrent_searches)

    async def _safe_search(self, client, query: str):
        import logging
        import os
        api_key = os.getenv("TAVILY_API_KEY")
        
        async with self.semaphore:
            try:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": api_key, "query": query},
                )
                response.raise_for_status()
                data = response.json()
                if "results" in data:
                    return data["results"]
                return data
            except Exception as e:
                logging.getLogger(__name__).error(f"Search failed for query '{query}': {e}")
            return []

    async def search(self, queries: list[str]) -> list[dict]:
        import asyncio
        import httpx
        if not queries:
            return []
            
        async with httpx.AsyncClient(timeout=15.0) as client:
            tasks = [self._safe_search(client, q) for q in queries]
            results_list = await asyncio.gather(*tasks)
            
            flat_results = []
            for res in results_list:
                if res:
                    flat_results.extend(res)
            return flat_results
