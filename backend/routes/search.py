from fastapi import APIRouter, HTTPException, Query
from crew.orchestrator import StartupValidatorOrchestrator
from services.tavily_service import TavilySearchService
from processors.result_processor import ResultProcessor
from llm.openrouter_client import OpenRouterClient
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Instantiate dependencies using Clean Architecture & Dependency Injection
llm_client = OpenRouterClient()
search_service = TavilySearchService()
result_processor = ResultProcessor()

# Initialize the main orchestration engine
orchestrator = StartupValidatorOrchestrator(
    llm_client=llm_client,
    search_service=search_service,
    result_processor=result_processor
)

@router.get("/search")
async def search(query: str = Query(..., min_length=10, max_length=1000, description="The startup idea to validate")):
    """
    Main endpoint for validating a startup idea.
    Triggers the full multi-agent workflow via the A2A Orchestrator.
    """
    try:
        logger.info(f"Received search request for idea: {query}")
        return await orchestrator.validate_idea(query)
    except Exception as e:
        logger.exception("Error processing search request")
        raise HTTPException(status_code=500, detail=str(e))
