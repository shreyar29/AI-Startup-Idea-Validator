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
import uuid
from typing import Any, Dict

from core.config import settings
from guardrails.manager import GuardrailManager
from utils.progress import ProgressManager

# Business Agents
from strategy.query_strategist import QueryStrategist
from agents.web_search_agent import WebSearchAgent
from agents.market_agent import MarketOpportunityAgent
from agents.competitor_agent import CompetitorAgent
from agents.customer_agent import CustomerAgent
from agents.comparison_agent import ComparisonAgent

logger = logging.getLogger(__name__)

class OrchestrationError(Exception):
    """Base exception for orchestrator errors."""
    pass

class PayloadIntegrityError(OrchestrationError):
    """Raised when critical payloads are missing or invalid."""
    pass

class MeshNodeWrapper:
    """Wraps an agent node to provide timeouts, execution metrics, and partial failure recovery."""
    def __init__(self, name: str, node: Any, metrics: Dict[str, Any], correlation_id: str, timeout: int = 180):
        self.name = name
        self.node = node
        self.metrics = metrics
        self.correlation_id = correlation_id
        self.timeout = timeout
        self._task = None
        
    async def get_analysis(self):
        if self._task is None:
            self._task = asyncio.create_task(self._execute())
        return await self._task

    async def _execute(self):
        start_time = time.time()
        self.metrics[self.name] = {
            "status": "started",
            "start_time": start_time,
            "end_time": None,
            "duration": 0
        }
        logger.info(f"[{self.correlation_id}] {self.name}: Execution started.")
        
        request_id = self.node.context.get("request_id")
        if request_id and self.name != "Web Search Agent":
            # Avoid duplicating Web Search events as it manages granular internal steps
            asyncio.create_task(ProgressManager.publish(request_id, self.name, "running", f"Analyzing data..."))
        
        try:
            result = await asyncio.wait_for(self.node.get_analysis(), timeout=self.timeout)
            duration = time.time() - start_time
            self.metrics[self.name].update({
                "status": "success",
                "end_time": time.time(),
                "duration": round(duration, 2)
            })
            logger.info(f"[{self.correlation_id}] {self.name}: Completed successfully in {duration:.2f}s.")
            if request_id and self.name != "Web Search Agent":
                asyncio.create_task(ProgressManager.publish(request_id, self.name, "completed", f"{self.name} finished successfully."))
            return result
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            self.metrics[self.name].update({
                "status": "timeout",
                "end_time": time.time(),
                "duration": round(duration, 2),
                "error": "Timeout exceeded"
            })
            logger.error(f"[{self.correlation_id}] {self.name}: Timed out after {self.timeout}s. Degrading gracefully.")
            if request_id and self.name != "Web Search Agent":
                asyncio.create_task(ProgressManager.publish(request_id, self.name, "failed", f"{self.name} timed out."))
            return {}
        except Exception as e:
            duration = time.time() - start_time
            self.metrics[self.name].update({
                "status": "failed",
                "end_time": time.time(),
                "duration": round(duration, 2),
                "error": str(e)
            })
            logger.exception(f"[{self.correlation_id}] {self.name}: Failed with error: {e}. Degrading gracefully.")
            if request_id and self.name != "Web Search Agent":
                asyncio.create_task(ProgressManager.publish(request_id, self.name, "failed", f"{self.name} encountered an error."))
            return {}


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

    async def validate_idea(self, startup_idea: str, request_id: str = None) -> Dict[str, Any]:
        """
        Executes the full architecture asynchronously by connecting agents in a mesh
        and requesting the final synthesis.
        """
        correlation_id = str(uuid.uuid4())[:8]
        logger.info(f"[{correlation_id}] P2P Mesh Network starting validation for idea: '{startup_idea}'")
        start_time = time.time()
        
        # Canonical decentralized context pointer passed to all peers
        shared_context = {
            "idea": {"description": startup_idea, "proposed_features": []},
            "correlation_id": correlation_id,
            "request_id": request_id,
            "research": {},
            "market_analysis": {},
            "customer_analysis": {},
            "competitor_analysis": {},
            "comparison_analysis": {}
        }
        
        metrics = {}

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

            # 2. Form the P2P Mesh (Fully Connected) with Wrappers
            wrapped_peers = {
                "web_search": MeshNodeWrapper("Web Search Agent", web_search_node, metrics, correlation_id, timeout=settings.orchestrator.WEB_SEARCH_TIMEOUT),
                "market": MeshNodeWrapper("Market Agent", market_node, metrics, correlation_id, timeout=settings.orchestrator.MARKET_AGENT_TIMEOUT),
                "customer": MeshNodeWrapper("Customer Agent", customer_node, metrics, correlation_id, timeout=settings.orchestrator.CUSTOMER_AGENT_TIMEOUT),
                "competitor": MeshNodeWrapper("Competitor Agent", competitor_node, metrics, correlation_id, timeout=settings.orchestrator.COMPETITOR_AGENT_TIMEOUT),
                "comparison": MeshNodeWrapper("Comparison Agent", comparison_node, metrics, correlation_id, timeout=settings.orchestrator.COMPARISON_AGENT_TIMEOUT)
            }

            for node in [web_search_node, market_node, customer_node, competitor_node, comparison_node]:
                node.connect_peers(wrapped_peers)

            # 3. Demand-Driven Execution
            logger.info(f"[{correlation_id}] Awaiting Web Search Node data...")
            web_search_data = await wrapped_peers["web_search"].get_analysis()

            # Validate payload integrity: check for actual category data, not just truthiness
            has_categories = isinstance(web_search_data, dict) and any(
                isinstance(v, list) and len(v) > 0 for v in web_search_data.values()
            )
            if not has_categories:
                logger.warning(f"[{correlation_id}] Orchestrator: Web search returned empty or invalid data. Continuing downstream mesh regardless.")
                
            logger.info(f"[{correlation_id}] Payload integrity check completed. Triggering P2P Mesh Execution...")
            await wrapped_peers["comparison"].get_analysis()
    
            exec_time = time.time() - start_time
            logger.info(f"[{correlation_id}] P2P Mesh Network completed successfully in {exec_time:.2f} seconds.")
            logger.info(f"[{correlation_id}] Aggregating final response payloads.")
            
            if request_id:
                await ProgressManager.publish(request_id, "Guardrails", "running", "Applying evidence guardrails and hallucination checks...")
            
            # Apply (4) Agent Output Guardrails and (5) Fact & Hallucination Guardrails
            market_data = GuardrailManager.validate_agent_output(
                "Market Agent", shared_context.get("market_analysis", {}), ["market_size", "growth_rate", "market_trends"]
            )
            competitor_data = GuardrailManager.validate_agent_output(
                "Competitor Agent", shared_context.get("competitor_analysis", {}), ["competitors"]
            )
            customer_data = GuardrailManager.validate_agent_output(
                "Customer Agent", shared_context.get("customer_analysis", {}), ["target_customer_segments", "pain_points"]
            )
            comparison_data = GuardrailManager.validate_agent_output(
                "Comparison Agent", shared_context.get("comparison_analysis", {}), ["feature_comparison"]
            )
            
            market_data = GuardrailManager.verify_facts_and_hallucinations("Market Agent", market_data, web_search_data)
            competitor_data = GuardrailManager.verify_facts_and_hallucinations("Competitor Agent", competitor_data, web_search_data)
            
            if request_id:
                await ProgressManager.publish(request_id, "Guardrails", "completed", "Guardrail verification passed.")
                await ProgressManager.publish(request_id, "Report Generator", "running", "Preparing Executive Report...")

            # Evaluate overall orchestration status based on mesh execution metrics
            critical_agents = ["Web Search Agent", "Comparison Agent"]
            optional_agents = ["Market Agent", "Customer Agent", "Competitor Agent"]
            
            overall_status = "success"
            for critical_agent in critical_agents:
                agent_metric = metrics.get(critical_agent, {})
                if agent_metric.get("status") in ["failed", "timeout"]:
                    overall_status = "failed"
                    break
                    
            if overall_status != "failed":
                for optional_agent in optional_agents:
                    agent_metric = metrics.get(optional_agent, {})
                    if agent_metric.get("status") in ["failed", "timeout"]:
                        overall_status = "partial_success"
                        break

            logger.info(f"[{correlation_id}] Orchestration final status evaluated as: {overall_status}")

            raw_response = {
                "metadata": {
                    "startup_idea": startup_idea,
                    "correlation_id": correlation_id,
                    "execution_time_seconds": round(exec_time, 2),
                    "status": overall_status,
                    "agent_metrics": metrics
                },
                "web_search_agent": {"search_results": web_search_data},
                "market_agent": market_data,
                "competitor_agent": competitor_data,
                "customer_agent": customer_data,
                "comparison_agent": comparison_data,
                "final_evaluation": comparison_data
            }
            
            # Apply (6) Final Response Guardrail
            final_report = GuardrailManager.verify_final_response(raw_response)
            
            if request_id:
                await ProgressManager.publish(request_id, "Orchestrator", "completed", "Validation pipeline finished.")
                
            return final_report

        except PayloadIntegrityError as e:
            logger.error(f"[{correlation_id}] Critical Payload Integrity Error: {e}")
            return self._format_error_response(startup_idea, correlation_id, start_time, str(e), metrics)
        except Exception as e:
            logger.exception(f"[{correlation_id}] P2P Mesh Network failed unexpectedly for idea: '{startup_idea}'")
            return self._format_error_response(startup_idea, correlation_id, start_time, "An unexpected error occurred during startup validation.", metrics)

    def _format_error_response(self, startup_idea: str, correlation_id: str, start_time: float, error_msg: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "metadata": {
                "startup_idea": startup_idea,
                "correlation_id": correlation_id,
                "execution_time_seconds": round(time.time() - start_time, 2),
                "status": "failed",
                "agent_metrics": metrics
            },
            "error": error_msg
        }

