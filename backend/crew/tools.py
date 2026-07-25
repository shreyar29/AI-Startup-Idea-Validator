import asyncio
import threading
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from agents.web_search_agent import WebSearchAgent
from strategy.query_strategist import QueryStrategist
from services.tavily_service import TavilySearchService
from processors.result_processor import ResultProcessor
from llm.openrouter_client import OpenRouterClient
from agents.market_agent import MarketOpportunityAgent
from utils.logger import get_logger

logger = get_logger(__name__)

class ToolSchema(BaseModel):
    startup_idea: str = Field(..., description="The startup idea to validate")

def run_async_in_thread(coro):
    """
    Safely runs an async coroutine in a new thread to avoid conflicts 
    with existing asyncio event loops (e.g., FastAPI's main loop).
    """
    result = None
    exception = None

    def runner():
        nonlocal result, exception
        try:
            result = asyncio.run(coro)
        except Exception as e:
            exception = e

    thread = threading.Thread(target=runner)
    thread.start()
    thread.join()

    if exception:
        raise exception
    return result

class WebSearchTool(BaseTool):
    name: str = "web_search_agent_tool"
    description: str = "Invokes the primary Web Search Agent to generate search queries and retrieve structured data for a given startup idea."
    args_schema: type[BaseModel] = ToolSchema
    
    # Instance-specific state injected by the orchestrator to track results safely per-request
    shared_state: dict = Field(default_factory=dict)

    def _run(self, startup_idea: str) -> str:
        logger.info(f"Executing WebSearchTool for idea: {startup_idea}")
        
        # Instantiate core web search components as-is
        llm_client = OpenRouterClient()
        query_strategist = QueryStrategist(llm_client=llm_client)
        search_service = TavilySearchService()
        result_processor = ResultProcessor()
        
        web_search_agent = WebSearchAgent(
            query_strategist=query_strategist,
            search_service=search_service,
            result_processor=result_processor
        )
        
        try:
            # Run the primary async agent method synchronously
            result = run_async_in_thread(web_search_agent.run(startup_idea))
            self.shared_state['web_search_result'] = result
            logger.info("WebSearchTool completed successfully.")
            return "Web search completed successfully. The exact JSON result has been stored internally."
        except Exception as e:
            logger.exception("Error in WebSearchTool execution.")
            return f"Error executing web search: {str(e)}"
            

class MarketAnalysisTool(BaseTool):
    name: str = "market_analysis_tool"
    description: str = "Analyzes the structured search results to generate market insights. Call this ONLY AFTER the web_search_agent_tool has completed."
    args_schema: type[BaseModel] = ToolSchema
    
    # Instance-specific state injected by the orchestrator
    shared_state: dict = Field(default_factory=dict)

    def _run(self, startup_idea: str) -> str:
        logger.info(f"Executing MarketAnalysisTool for idea: {startup_idea}")
        
        validation_data = self.shared_state.get('web_search_result')
        if not validation_data:
            return "Error: No search results found. Please run the web_search_agent_tool first."
            
        llm_client = OpenRouterClient()
        market_agent = MarketOpportunityAgent(llm_client=llm_client)
        
        try:
            # Run the primary async agent method synchronously
            result = run_async_in_thread(market_agent.analyze_market(validation_data))
            self.shared_state['market_analysis_result'] = result
            logger.info("MarketAnalysisTool completed successfully.")
            return "Market analysis completed successfully. The exact JSON result has been stored internally."
        except Exception as e:
            logger.exception("Error in MarketAnalysisTool execution.")
            return f"Error executing market analysis: {str(e)}"
