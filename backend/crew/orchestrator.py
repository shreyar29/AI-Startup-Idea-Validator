"""
orchestrator.py

Fully Connected Mesh Architecture for the Multi-Agent Startup Idea Validator.

Agents:
    1. Web Search Agent
    2. Market Opportunity Agent
    3. Customer Agent
    4. Competitor Agent
    5. Comparison Agent
    6. Risk Agent

All agents share a common context and are connected through a P2P mesh.
The orchestrator uses demand-driven execution with timeouts, metrics,
progress reporting, guardrails, and graceful failure handling.
"""

import asyncio
import logging
import time
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
from agents.risk_agent import RiskAgent


logger = logging.getLogger(__name__)


class OrchestrationError(Exception):
    """Base exception for orchestrator errors."""
    pass


class PayloadIntegrityError(OrchestrationError):
    """Raised when critical payloads are missing or invalid."""
    pass


class MeshNodeWrapper:
    """
    Wraps an agent node with:
        - timeout protection
        - execution metrics
        - progress reporting
        - graceful error handling
        - task caching

    A node executes only once. Multiple peers requesting the same
    node share the same asyncio Task.
    """

    def __init__(
        self,
        name: str,
        node: Any,
        metrics: Dict[str, Any],
        correlation_id: str,
        timeout: int = 180,
    ):
        self.name = name
        self.node = node
        self.metrics = metrics
        self.correlation_id = correlation_id
        self.timeout = timeout
        self._task = None

    async def get_analysis(self):
        """Return the cached analysis task or create it."""
        if self._task is None:
            self._task = asyncio.create_task(self._execute())

        return await self._task

    async def _execute(self):
        """Execute the wrapped agent with timeout and error handling."""
        start_time = time.time()

        self.metrics[self.name] = {
            "status": "started",
            "start_time": start_time,
            "end_time": None,
            "duration": 0,
        }

        logger.info(
            f"[{self.correlation_id}] "
            f"{self.name}: Execution started."
        )

        request_id = getattr(self.node, "context", {}).get("request_id")

        if request_id and self.name != "Web Search Agent":
            asyncio.create_task(
                ProgressManager.publish(
                    request_id,
                    self.name,
                    "running",
                    "Analyzing data...",
                )
            )

        try:
            result = await asyncio.wait_for(
                self.node.get_analysis(),
                timeout=self.timeout,
            )

            duration = time.time() - start_time

            self.metrics[self.name].update(
                {
                    "status": "success",
                    "end_time": time.time(),
                    "duration": round(duration, 2),
                }
            )

            logger.info(
                f"[{self.correlation_id}] "
                f"{self.name}: Completed successfully "
                f"in {duration:.2f}s."
            )

            if request_id and self.name != "Web Search Agent":
                asyncio.create_task(
                    ProgressManager.publish(
                        request_id,
                        self.name,
                        "completed",
                        f"{self.name} finished successfully.",
                    )
                )

            return result

        except asyncio.TimeoutError:
            duration = time.time() - start_time

            self.metrics[self.name].update(
                {
                    "status": "timeout",
                    "end_time": time.time(),
                    "duration": round(duration, 2),
                    "error": "Timeout exceeded",
                }
            )

            logger.error(
                f"[{self.correlation_id}] "
                f"{self.name}: Timed out after "
                f"{self.timeout}s. Degrading gracefully."
            )

            if request_id and self.name != "Web Search Agent":
                asyncio.create_task(
                    ProgressManager.publish(
                        request_id,
                        self.name,
                        "failed",
                        f"{self.name} timed out.",
                    )
                )

            return {}

        except asyncio.CancelledError:
            duration = time.time() - start_time

            self.metrics[self.name].update(
                {
                    "status": "cancelled",
                    "end_time": time.time(),
                    "duration": round(duration, 2),
                    "error": "Task cancelled",
                }
            )

            logger.warning(
                f"[{self.correlation_id}] "
                f"{self.name}: Task cancelled."
            )

            raise

        except Exception as exc:
            duration = time.time() - start_time

            self.metrics[self.name].update(
                {
                    "status": "failed",
                    "end_time": time.time(),
                    "duration": round(duration, 2),
                    "error": str(exc),
                }
            )

            logger.exception(
                f"[{self.correlation_id}] "
                f"{self.name}: Failed with error: {exc}. "
                f"Degrading gracefully."
            )

            if request_id and self.name != "Web Search Agent":
                asyncio.create_task(
                    ProgressManager.publish(
                        request_id,
                        self.name,
                        "failed",
                        f"{self.name} encountered an error.",
                    )
                )

            return {}


class StartupValidatorOrchestrator:
    """
    Coordinates the complete multi-agent startup validation workflow.

    Mesh:
        Web Search
             |
        +----+----+---------+---------+
        |         |         |         |
      Market   Customer  Competitor Comparison
                                      |
                                     Risk

    All nodes are directly connected through the shared peer map.
    """

    def __init__(
        self,
        llm_client: Any,
        search_service: Any,
        result_processor: Any,
    ):
        """
        Dependency injection for shared LLM and search services.
        """
        self.llm_client = llm_client
        self.search_service = search_service
        self.result_processor = result_processor

    async def validate_idea(
        self,
        startup_idea: str,
        request_id: str = None,
    ) -> Dict[str, Any]:
        """
        Execute the complete startup idea validation pipeline.
        """

        correlation_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        logger.info(
            f"[{correlation_id}] "
            f"P2P Mesh Network starting validation "
            f"for idea: '{startup_idea}'"
        )

        # ================================================================
        # SHARED CONTEXT
        # ================================================================

        shared_context = {
            "idea": {
                "description": startup_idea,
                "proposed_features": [],
            },
            "correlation_id": correlation_id,
            "request_id": request_id,

            "research": {},

            "market_analysis": {},
            "customer_analysis": {},
            "competitor_analysis": {},
            "comparison_analysis": {},
            "risk_analysis": {},
        }

        metrics: Dict[str, Any] = {}

        try:
            # ============================================================
            # 1. CREATE ALL AGENTS
            # ============================================================

            query_strategist = QueryStrategist(
                llm_client=self.llm_client
            )

            web_search_node = WebSearchAgent(
                query_strategist,
                self.search_service,
                self.result_processor,
                shared_context,
            )

            market_node = MarketOpportunityAgent(
                shared_context,
                llm_client=self.llm_client,
            )

            customer_node = CustomerAgent(
                shared_context,
                llm_client=self.llm_client,
            )

            competitor_node = CompetitorAgent(
                shared_context,
                llm_client=self.llm_client,
            )

            comparison_node = ComparisonAgent(
                shared_context,
                llm_client=self.llm_client,
            )

            # ============================================================
            # RISK AGENT
            # ============================================================

            risk_node = RiskAgent(
                shared_context,
                llm_client=self.llm_client,
            )

            # ============================================================
            # 2. CREATE FULL P2P MESH
            # ============================================================

            # Use a dedicated risk timeout if it exists in config.
            # Otherwise fall back to comparison timeout so this file
            # does not require a new config variable.
            risk_timeout = getattr(
                settings.orchestrator,
                "RISK_AGENT_TIMEOUT",
                settings.orchestrator.COMPARISON_AGENT_TIMEOUT,
            )

            wrapped_peers = {
                "web_search": MeshNodeWrapper(
                    "Web Search Agent",
                    web_search_node,
                    metrics,
                    correlation_id,
                    timeout=settings.orchestrator.WEB_SEARCH_TIMEOUT,
                ),

                "market": MeshNodeWrapper(
                    "Market Agent",
                    market_node,
                    metrics,
                    correlation_id,
                    timeout=settings.orchestrator.MARKET_AGENT_TIMEOUT,
                ),

                "customer": MeshNodeWrapper(
                    "Customer Agent",
                    customer_node,
                    metrics,
                    correlation_id,
                    timeout=settings.orchestrator.CUSTOMER_AGENT_TIMEOUT,
                ),

                "competitor": MeshNodeWrapper(
                    "Competitor Agent",
                    competitor_node,
                    metrics,
                    correlation_id,
                    timeout=settings.orchestrator.COMPETITOR_AGENT_TIMEOUT,
                ),

                "comparison": MeshNodeWrapper(
                    "Comparison Agent",
                    comparison_node,
                    metrics,
                    correlation_id,
                    timeout=settings.orchestrator.COMPARISON_AGENT_TIMEOUT,
                ),

                # ========================================================
                # RISK AGENT IS NOW PART OF THE MESH
                # ========================================================

                "risk": MeshNodeWrapper(
                    "Risk Agent",
                    risk_node,
                    metrics,
                    correlation_id,
                    timeout=risk_timeout,
                ),
            }

            # ============================================================
            # 3. CONNECT EVERY AGENT TO EVERY PEER
            # ============================================================

            all_nodes = [
                web_search_node,
                market_node,
                customer_node,
                competitor_node,
                comparison_node,
                risk_node,
            ]

            for node in all_nodes:
                node.connect_peers(wrapped_peers)

            logger.info(
                f"[{correlation_id}] "
                f"Fully connected P2P mesh initialized with "
                f"{len(all_nodes)} agents."
            )

            # ============================================================
            # 4. WEB SEARCH
            # ============================================================

            logger.info(
                f"[{correlation_id}] "
                f"Awaiting Web Search Agent..."
            )

            web_search_data = await wrapped_peers[
                "web_search"
            ].get_analysis()

            has_categories = (
                isinstance(web_search_data, dict)
                and any(
                    isinstance(value, list) and len(value) > 0
                    for value in web_search_data.values()
                )
            )

            if not has_categories:
                logger.warning(
                    f"[{correlation_id}] "
                    f"Web Search Agent returned empty or invalid data. "
                    f"Continuing downstream mesh."
                )

            # ============================================================
            # 5. TRIGGER COMPARISON AGENT
            # ============================================================

            logger.info(
                f"[{correlation_id}] "
                f"Triggering Comparison Agent..."
            )

            comparison_result = await wrapped_peers[
                "comparison"
            ].get_analysis()

            # ============================================================
            # 6. TRIGGER RISK AGENT
            # ============================================================

            logger.info(
                f"[{correlation_id}] "
                f"Triggering Risk Agent..."
            )

            risk_data = await wrapped_peers[
                "risk"
            ].get_analysis()

            # ============================================================
            # 7. READ SHARED CONTEXT
            # ============================================================

            market_raw = shared_context.get(
                "market_analysis",
                {},
            )

            competitor_raw = shared_context.get(
                "competitor_analysis",
                {},
            )

            customer_raw = shared_context.get(
                "customer_analysis",
                {},
            )

            comparison_raw = shared_context.get(
                "comparison_analysis",
                {},
            )

            risk_raw = shared_context.get(
                "risk_analysis",
                {},
            )

            # Preserve returned values if an agent returns its analysis
            # without writing it into shared_context.
            if not comparison_raw and comparison_result:
                comparison_raw = comparison_result

            if not risk_raw and risk_data:
                risk_raw = risk_data

            # ============================================================
            # 8. APPLY AGENT OUTPUT GUARDRAILS
            # ============================================================

            if request_id:
                await ProgressManager.publish(
                    request_id,
                    "Guardrails",
                    "running",
                    "Applying evidence guardrails and hallucination checks...",
                )

            market_data = GuardrailManager.validate_agent_output(
                "Market Agent",
                market_raw,
                [
                    "market_size",
                    "growth_rate",
                    "market_trends",
                ],
            )

            competitor_data = GuardrailManager.validate_agent_output(
                "Competitor Agent",
                competitor_raw,
                [
                    "competitors",
                ],
            )

            customer_data = GuardrailManager.validate_agent_output(
                "Customer Agent",
                customer_raw,
                [
                    "target_customer_segments",
                    "pain_points",
                ],
            )

            comparison_data = GuardrailManager.validate_agent_output(
                "Comparison Agent",
                comparison_raw,
                [
                    "feature_comparison",
                ],
            )

            # ============================================================
            # RISK DATA
            # ============================================================

            # RiskAgent owns its own output schema, so we preserve its
            # validated result rather than inventing required fields
            # here.
            risk_data = risk_raw

            # ============================================================
            # 9. FACT / HALLUCINATION VERIFICATION
            # ============================================================

            market_data = (
                GuardrailManager.verify_facts_and_hallucinations(
                    "Market Agent",
                    market_data,
                    web_search_data,
                )
            )

            competitor_data = (
                GuardrailManager.verify_facts_and_hallucinations(
                    "Competitor Agent",
                    competitor_data,
                    web_search_data,
                )
            )

            if request_id:
                await ProgressManager.publish(
                    request_id,
                    "Guardrails",
                    "completed",
                    "Guardrail verification passed.",
                )

                await ProgressManager.publish(
                    request_id,
                    "Report Generator",
                    "running",
                    "Preparing Executive Report...",
                )

            # ============================================================
            # 10. DETERMINE OVERALL STATUS
            # ============================================================

            critical_agents = [
                "Web Search Agent",
                "Comparison Agent",
                "Risk Agent",
            ]

            optional_agents = [
                "Market Agent",
                "Customer Agent",
                "Competitor Agent",
            ]

            overall_status = "success"

            # Critical agents failing means overall validation failed.
            for agent_name in critical_agents:
                agent_metric = metrics.get(
                    agent_name,
                    {},
                )

                if agent_metric.get("status") in [
                    "failed",
                    "timeout",
                ]:
                    overall_status = "failed"
                    break

            # Optional agent failure produces partial success.
            if overall_status != "failed":
                for agent_name in optional_agents:
                    agent_metric = metrics.get(
                        agent_name,
                        {},
                    )

                    if agent_metric.get("status") in [
                        "failed",
                        "timeout",
                    ]:
                        overall_status = "partial_success"
                        break

            logger.info(
                f"[{correlation_id}] "
                f"Final orchestration status: "
                f"{overall_status}"
            )

            # ============================================================
            # 11. BUILD FINAL RESPONSE
            # ============================================================

            execution_time = time.time() - start_time

            raw_response = {
                "metadata": {
                    "startup_idea": startup_idea,
                    "correlation_id": correlation_id,
                    "execution_time_seconds": round(
                        execution_time,
                        2,
                    ),
                    "status": overall_status,
                    "agent_metrics": metrics,
                },

                "web_search_agent": {
                    "search_results": web_search_data,
                },

                "market_agent": market_data,

                "competitor_agent": competitor_data,

                "customer_agent": customer_data,

                "comparison_agent": comparison_data,

                # ========================================================
                # RISK AGENT OUTPUT
                # ========================================================

                "risk_agent": risk_data,

                # Keep a clearly named risk_analysis field as well so
                # downstream consumers can access it directly.
                "risk_analysis": risk_data,

                "final_evaluation": {
                    "comparison": comparison_data,
                    "risk": risk_data,
                },
            }

            # ============================================================
            # 12. FINAL RESPONSE GUARDRAIL
            # ============================================================

            final_report = (
                GuardrailManager.verify_final_response(
                    raw_response
                )
            )

            if request_id:
                await ProgressManager.publish(
                    request_id,
                    "Orchestrator",
                    "completed",
                    "Validation pipeline finished.",
                )

            logger.info(
                f"[{correlation_id}] "
                f"P2P Mesh Network completed successfully "
                f"in {execution_time:.2f}s."
            )

            return final_report

        # ================================================================
        # ERROR HANDLING
        # ================================================================

        except PayloadIntegrityError as exc:
            logger.error(
                f"[{correlation_id}] "
                f"Critical Payload Integrity Error: {exc}"
            )

            return self._format_error_response(
                startup_idea,
                correlation_id,
                start_time,
                str(exc),
                metrics,
            )

        except Exception as exc:
            logger.exception(
                f"[{correlation_id}] "
                f"P2P Mesh Network failed unexpectedly "
                f"for idea: '{startup_idea}'"
            )

            return self._format_error_response(
                startup_idea,
                correlation_id,
                start_time,
                "An unexpected error occurred during startup validation.",
                metrics,
            )

    def _format_error_response(
        self,
        startup_idea: str,
        correlation_id: str,
        start_time: float,
        error_msg: str,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Return a consistent error payload."""

        return {
            "metadata": {
                "startup_idea": startup_idea,
                "correlation_id": correlation_id,
                "execution_time_seconds": round(
                    time.time() - start_time,
                    2,
                ),
                "status": "failed",
                "agent_metrics": metrics,
            },
            "error": error_msg,
        }