import asyncio
import json
import logging
from typing import Any

from strategy.query_strategist import QueryStrategist
from services.tavily_service import TavilySearchService
from processors.result_processor import ResultProcessor
from agents.web_search_agent import WebSearchAgent
from utils.error_handler import SearchServiceError

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

# Mock Dependencies to demonstrate orchestration without actual network/LLM calls
class MockQueryStrategist(QueryStrategist):
    def __init__(self): pass
    async def run(self, input_data: dict) -> dict[str, Any]:
        return {
            "identified_context": {"product": "AI Resume Builder", "industry": "HR Tech", "target_audience": "Job seekers", "technology": "AI"},
            "queries": {"competitors": ["AI resume builder competitors", "top AI tools"]}
        }

class MockTavilyService(TavilySearchService):
    def __init__(self): self._fail_once = True
    async def search(self, category: str, queries: list[str]) -> list[dict[str, Any]]:
        # Simulate a transient failure on the first call to test retry logic
        if self._fail_once:
            self._fail_once = False
            raise SearchServiceError("Simulated transient Tavily timeout")
        return [{"url": "https://example.com", "content": "Sample content for " + queries[0], "title": "Example", "score": 0.9}]

class MockResultProcessor(ResultProcessor):
    def __init__(self): pass
    def process(self, raw_results: dict[str, list[dict[str, Any]]], idea: str = "") -> dict[str, list[dict[str, Any]]]:
        # Return mock processed format
        return {
            cat: [{"url": r["url"], "content": r["content"], "title": r["title"], "relevance_score": 10.0, "domain": "example.com"} for r in res]
            for cat, res in raw_results.items()
        }

async def _test():
    agent = WebSearchAgent(
        query_strategist=MockQueryStrategist(), 
        search_service=MockTavilyService(), 
        result_processor=MockResultProcessor(),
        shared_context={"request_id": "test_req_123", "idea": {"description": "AI Resume Builder"}}
    )
    
    try:
        result = await agent.run("AI Resume Builder")
        print("\n=== Final Web Search Agent Output ===")
        print(json.dumps(result, indent=2))
    except Exception as e:
        logger.error("Test failed: %s", e)

if __name__ == "__main__":
    asyncio.run(_test())
