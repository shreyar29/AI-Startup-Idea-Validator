import asyncio
import logging
from strategy.query_strategist import QueryStrategist
from agents.web_search_agent import WebSearchAgent
from agents.market_agent import MarketOpportunityAgent
from agents.competitor_agent import CompetitorAgent
from agents.customer_agent import CustomerAgent
from agents.comparison_agent import ComparisonAgent
from services.tavily_service import TavilySearchService
from processors.result_processor import ResultProcessor
from llm.openrouter_client import OpenRouterClient
from crew.orchestrator import StartupValidatorOrchestrator

logging.basicConfig(level=logging.INFO)

async def test_run():
    print("Starting test...")
    orchestrator = StartupValidatorOrchestrator(
        llm_client=OpenRouterClient(),
        search_service=TavilySearchService(),
        result_processor=ResultProcessor()
    )
    result = await orchestrator.validate_idea("AI-powered platform that detects skin diseases using smartphone images")
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(test_run())
