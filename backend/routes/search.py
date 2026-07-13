from fastapi import APIRouter, HTTPException
from agents.web_search_agent import WebSearchAgent
from strategy.query_strategist import QueryStrategist
from services.tavily_service import TavilySearchService
from processors.result_processor import ResultProcessor
from llm.openrouter_client import OpenRouterClient
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Instantiate dependencies using Clean Architecture & Dependency Injection
llm_client = OpenRouterClient()
query_strategist = QueryStrategist(llm_client=llm_client)
search_service = TavilySearchService()
result_processor = ResultProcessor()

# Initialize the main orchestration agent
agent = WebSearchAgent(
    query_strategist=query_strategist,
    search_service=search_service,
    result_processor=result_processor
)

@router.get("/search")
async def search(query: str):
    """
    Main endpoint for validating a startup idea.
    Triggers the full multi-agent workflow.
    """
    try:
        logger.info(f"Received search request for idea: {query}")
        return await agent.run(query)
    except Exception as e:
        logger.exception("Error processing search request")
        raise HTTPException(status_code=500, detail=str(e))
