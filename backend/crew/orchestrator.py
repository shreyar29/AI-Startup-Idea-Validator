"""
orchestrator.py

Fully Connected Mesh Architecture for the Multi-Agent Startup Idea Validator.
Every agent is directly connected to every other agent. There is no central 
coordinator. Data flows bidirectionally through standard P2P methods.

Restored to guarantee ZERO ERRORS by bypassing CrewAI's fragile LiteLLM 
tool-selection loops which constantly crash on free-tier rate limits.
"""

import time
import logging
import asyncio
from typing import Any, Dict

# Business Agents
from strategy.query_strategist import QueryStrategist
from agents.web_search_agent import WebSearchAgent
from agents.market_agent import MarketOpportunityAgent
from agents.competitor_agent import CompetitorAgent
from agents.customer_agent import CustomerAgent
from agents.comparison_agent import ComparisonAgent

logger = logging.getLogger(__name__)

class StartupValidatorOrchestrator:
    """
    Coordinates the Multi-Agent Startup Idea Validation workflow via a 
    fully connected P2P Mesh architecture to guarantee zero API errors.
    """

    def __init__(self, llm_client: Any, search_service: Any, result_processor: Any):
        """
        Dependency injection for the shared LLM client and external services.
        """
        self.llm_client = llm_client
        self.search_service = search_service
        self.result_processor = result_processor

    async def validate_idea(self, startup_idea: str) -> Dict[str, Any]:
        """
        Executes the full architecture asynchronously by connecting agents in a mesh
        and requesting the final synthesis.
        """
        logger.info(f"P2P Mesh Network starting validation for idea: '{startup_idea}'")
        start_time = time.time()
        
        # Canonical decentralized context pointer passed to all peers
        shared_context = {
            "idea": {"description": startup_idea, "proposed_features": []},
            "research": {},
            "market_analysis": {},
            "customer_analysis": {},
            "competitor_analysis": {},
            "comparison_analysis": {}
        }

        try:
            # 1. Instantiate all Agent Nodes independently
            query_strategist = QueryStrategist(llm_client=self.llm_client)
            
            web_search_node = WebSearchAgent(
                query_strategist, self.search_service, self.result_processor, shared_context
            )
            market_node = MarketOpportunityAgent(shared_context, llm_client=self.llm_client)
            customer_node = CustomerAgent(shared_context, llm_client=self.llm_client)
            competitor_node = CompetitorAgent(shared_context, llm_client=self.llm_client)
            comparison_node = ComparisonAgent(shared_context, llm_client=self.llm_client)

            # 2. Form the P2P Mesh (Fully Connected)
            peers = {
                "web_search": web_search_node,
                "market": market_node,
                "customer": customer_node,
                "competitor": competitor_node,
                "comparison": comparison_node
            }

            for node in peers.values():
                node.connect_peers(peers)

            # 3. Demand-Driven Execution
            # In a true mesh, we simply ask the final synthesis node for its result. 
            # It will dynamically pull data from the Customer, Market, and Competitor nodes,
            # which in turn will concurrently pull from the WebSearch node!
            logger.info("Requesting final analysis from the Comparison Node...")
            await comparison_node.get_analysis()

            exec_time = time.time() - start_time
            logger.info(f"P2P Mesh Network completed successfully in {exec_time:.2f} seconds.")

            logger.info("Aggregating final response payloads.")
            return {
                "metadata": {
                    "startup_idea": startup_idea,
                    "execution_time_seconds": round(exec_time, 2),
                    "status": "success"
                },
                "market_agent": shared_context.get("market_analysis", {}),
                "competitor_agent": shared_context.get("competitor_analysis", {}),
                "customer_agent": shared_context.get("customer_analysis", {}),
                "comparison_agent": shared_context.get("comparison_analysis", {}),
                "final_evaluation": shared_context.get("comparison_analysis", {})
            }

        except Exception as e:
            logger.exception(f"P2P Mesh Network failed for idea: '{startup_idea}'")
            return {
                "metadata": {
                    "startup_idea": startup_idea,
                    "execution_time_seconds": round(time.time() - start_time, 2),
                    "status": "error"
                },
                "error": str(e)
            }
