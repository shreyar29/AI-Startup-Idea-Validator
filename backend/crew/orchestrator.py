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
from telemetry.metrics_service import MetricsService

from core.agent_config import AGENT_REGISTRY
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
from agents.swot_agent import SWOTAgent
from agents.mvp_agent import MVPAgent
from agents.gtm_agent import GTMAgent
from agents.startup_score_agent import StartupScoreAgent

# Pydantic Agent Contracts
from agents.agent_contracts import (
    MarketAnalysis, CustomerAnalysis, CompetitorAnalysis,
    RiskAnalysis, SWOTAnalysis, MVPAnalysis, GTMAnalysis
)

logger = logging.getLogger(__name__)


class OrchestrationError(Exception):
    """Base exception for orchestrator errors."""
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

    def _safe_publish(self, request_id: str, component: str, status: str, message: str):
        if not request_id:
            return
        task = asyncio.create_task(ProgressManager.publish(request_id, component, status, message))
        task.add_done_callback(lambda t: t.exception())

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

        context = getattr(self.node, "context", {})
        request_id = context.get("request_id") if isinstance(context, dict) else getattr(context, "request_id", None)

        if request_id and self.name != "Web Search Agent":
            self._safe_publish(request_id, self.name, "running", "Analyzing data...")

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
            MetricsService.record_agent_execution(self.name, duration, "success")

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
            MetricsService.record_agent_execution(self.name, duration, "timeout", "Timeout exceeded")

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
            error_summary = f"Task failed with {type(exc).__name__}"

            self.metrics[self.name].update(
                {
                    "status": "failed",
                    "end_time": time.time(),
                    "duration": round(duration, 2),
                    "error": error_summary,
                }
            )
            MetricsService.record_agent_execution(self.name, duration, "failed", error_summary)

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
    """

    def __init__(
        self,
        llm_client: Any,
        search_service: Any,
        result_processor: Any,
    ):
        self.llm_client = llm_client
        self.search_service = search_service
        self.result_processor = result_processor

    def _safe_publish(self, request_id: str, component: str, status: str, message: str):
        if not request_id:
            return
        task = asyncio.create_task(ProgressManager.publish(request_id, component, status, message))
        task.add_done_callback(lambda t: t.exception())

    # Ephemeral memory context storage removed in favor of Database persistence in chat_routes.py

    async def validate_idea(
        self,
        startup_idea: str,
        request_id: str = None,
    ) -> Dict[str, Any]:
        # Input Safety Hardening
        startup_idea = startup_idea.strip()[:2000]
        if not startup_idea:
            raise ValueError("Startup idea cannot be empty or solely whitespace.")

        correlation_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        logger.info(
            f"[{correlation_id}] "
            f"P2P Mesh Network starting validation "
            f"for idea of length: {len(startup_idea)}"
        )

        shared_context = self._build_shared_context(startup_idea, correlation_id, request_id)
        metrics: Dict[str, Any] = {}

        try:
            wrapped_peers, all_nodes = self._initialize_mesh(shared_context, metrics, correlation_id)
            
            # Connect all nodes
            for node in all_nodes:
                node.connect_peers(wrapped_peers)

            logger.info(f"[{correlation_id}] Fully connected P2P mesh initialized with {len(all_nodes)} agents.")

            agent_outputs = await self._execute_mesh(wrapped_peers, correlation_id)
            
            # Update shared context with outputs
            self._update_shared_context(shared_context, agent_outputs)

            final_data = self._apply_guardrails(request_id, shared_context, agent_outputs, correlation_id)
            
            overall_status = self._determine_status(metrics, correlation_id)
            
            final_report = self._build_final_response(
                startup_idea, correlation_id, start_time, overall_status, metrics, agent_outputs, final_data, request_id
            )

            return final_report

        except Exception as exc:
            logger.exception(
                f"[{correlation_id}] "
                f"P2P Mesh Network failed unexpectedly "
                f"for idea of length: {len(startup_idea)}"
            )
            return self._format_error_response(
                startup_idea, correlation_id, start_time,
                "An unexpected error occurred during startup validation.", metrics
            )

    def _build_shared_context(self, startup_idea: str, correlation_id: str, request_id: str) -> dict:
        return {
            "idea": {"description": startup_idea, "proposed_features": []},
            "correlation_id": correlation_id,
            "request_id": request_id,
            "research": {},
            "market_analysis": {}, "customer_analysis": {}, "competitor_analysis": {},
            "comparison_analysis": {}, "risk_analysis": {}, "swot_analysis": {},
            "mvp_analysis": {}, "gtm_analysis": {}, "startup_score_analysis": {},
        }

    def _initialize_mesh(self, shared_context: dict, metrics: dict, correlation_id: str):
        query_strategist = QueryStrategist(llm_client=self.llm_client)
        raw_nodes = {
            "web_search": WebSearchAgent(query_strategist, self.search_service, self.result_processor, shared_context=shared_context),
            "market": MarketOpportunityAgent(shared_context),
            "customer": CustomerAgent(shared_context),
            "competitor": CompetitorAgent(shared_context),
            "comparison": ComparisonAgent(shared_context, llm_client=self.llm_client),
            "risk": RiskAgent(shared_context, llm_client=self.llm_client),
            "swot": SWOTAgent(shared_context, llm_client=self.llm_client),
            "mvp": MVPAgent(shared_context, llm_client=self.llm_client),
            "gtm": GTMAgent(shared_context, llm_client=self.llm_client),
            "startup_score": StartupScoreAgent(shared_context, llm_client=self.llm_client),
        }
        
        wrapped_peers = {}
        for key, node_instance in raw_nodes.items():
            config = AGENT_REGISTRY.get(key)
            if config:
                wrapped_peers[key] = MeshNodeWrapper(config.name, node_instance, metrics, correlation_id, timeout=config.timeout)
                
        return wrapped_peers, list(raw_nodes.values())

    async def _execute_mesh(self, wrapped_peers: dict, correlation_id: str) -> dict:
        # Calculate execution tiers based on dependencies for concurrent execution
        tiers = []
        resolved = set()
        pending = set(AGENT_REGISTRY.keys())
        
        while pending:
            current_tier = []
            for key in pending:
                if all(dep in resolved for dep in AGENT_REGISTRY[key].dependencies):
                    current_tier.append(key)
            if not current_tier:
                break
            for key in current_tier:
                resolved.add(key)
                pending.remove(key)
            current_tier.sort(key=lambda k: AGENT_REGISTRY[k].execution_order)
            tiers.append(current_tier)

        agent_outputs = {}
        for tier in tiers:
            logger.info(f"[{correlation_id}] Triggering concurrent tier: {tier}")
            tasks = [wrapped_peers[key].get_analysis() for key in tier]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for key, result in zip(tier, results):
                if isinstance(result, Exception):
                    logger.error(f"[{correlation_id}] Agent {key} raised an exception in mesh: {type(result).__name__}")
                    agent_outputs[key] = {}
                else:
                    agent_outputs[key] = result
                    
                if key == "web_search":
                    has_categories = isinstance(result, dict) and any(isinstance(v, list) and len(v) > 0 for v in result.values())
                    if not has_categories:
                        logger.warning(f"[{correlation_id}] Web Search Agent returned empty or invalid data. Continuing downstream mesh.")
        return agent_outputs

    def _update_shared_context(self, shared_context: dict, agent_outputs: dict):
        mapping = {
            "comparison": "comparison_analysis",
            "market": "market_analysis",
            "customer": "customer_analysis",
            "competitor": "competitor_analysis",
            "risk": "risk_analysis",
            "swot": "swot_analysis",
            "mvp": "mvp_analysis",
            "gtm": "gtm_analysis",
            "startup_score": "startup_score_analysis",
        }
        
        model_mapping = {
            "market": MarketAnalysis,
            "customer": CustomerAnalysis,
            "competitor": CompetitorAnalysis,
            "risk": RiskAnalysis,
            "swot": SWOTAnalysis,
            "mvp": MVPAnalysis,
            "gtm": GTMAnalysis,
        }

        for key, context_key in mapping.items():
            raw_output = agent_outputs.get(key)
            if not shared_context.get(context_key) and raw_output:
                # Validate output schema via Pydantic if a model exists
                if key in model_mapping and isinstance(raw_output, dict):
                    try:
                        model_mapping[key](**raw_output)
                        # Avoid model_dump() memory duplication; store by reference
                        shared_context[context_key] = raw_output
                    except Exception as e:
                        logger.error(f"Schema validation failed for {key}: {type(e).__name__}. Falling back to raw dictionary.")
                        shared_context[context_key] = raw_output
                else:
                    shared_context[context_key] = raw_output

    def _apply_guardrails(self, request_id: str, shared_context: dict, agent_outputs: dict, correlation_id: str) -> dict:
        if request_id:
            self._safe_publish(request_id, "Guardrails", "running", "Applying evidence guardrails and hallucination checks...")
            
        web_search_data = agent_outputs.get("web_search", {})
        
        data = {}
        fields_map = {
            "market": ("Market Agent", "market_analysis", ["market_size", "growth_rate", "market_trends"]),
            "competitor": ("Competitor Agent", "competitor_analysis", ["competitors"]),
            "customer": ("Customer Agent", "customer_analysis", ["target_customer_segments", "pain_points"]),
            "comparison": ("Comparison Agent", "comparison_analysis", ["feature_comparison", "executive_summary"]),
            "risk": ("Risk Agent", "risk_analysis", ["risks", "top_risks", "recommendations"]),
            "swot": ("SWOT Agent", "swot_analysis", ["strengths", "weaknesses", "opportunities", "threats"]),
            "mvp": ("MVP Agent", "mvp_analysis", ["core_features", "optional_features", "future_features", "mvp_scope"]),
            "gtm": ("GTM Agent", "gtm_analysis", ["target_segment", "acquisition_channels", "pricing_strategy", "launch_plan"]),
            "startup_score": ("Startup Score Agent", "startup_score_analysis", ["overall_score", "verdict", "confidence_level"])
        }
        
        # 1. Validate formats
        for key, (name, ctx_key, req_fields) in fields_map.items():
            data[key] = GuardrailManager.validate_agent_output(name, shared_context.get(ctx_key, {}), req_fields)
            
        # 2. Fact checking
        verify_keys = ["market", "competitor", "risk", "swot", "mvp", "gtm", "startup_score"]
        for key in verify_keys:
            name = fields_map[key][0]
            data[key] = GuardrailManager.verify_facts_and_hallucinations(name, data[key], web_search_data)
            
        if request_id:
            self._safe_publish(request_id, "Guardrails", "completed", "Guardrail verification passed.")
            self._safe_publish(request_id, "Report Generator", "running", "Preparing Executive Report...")
            
        return data

    def _determine_status(self, metrics: dict, correlation_id: str) -> str:
        critical_agents = [cfg.name for cfg in AGENT_REGISTRY.values() if cfg.is_critical]
        optional_agents = [cfg.name for cfg in AGENT_REGISTRY.values() if not cfg.is_critical]
        
        overall_status = "success"
        for agent_name in critical_agents:
            if metrics.get(agent_name, {}).get("status") in ["failed", "timeout"]:
                return "failed"
                
        for agent_name in optional_agents:
            if metrics.get(agent_name, {}).get("status") in ["failed", "timeout"]:
                overall_status = "partial_success"
                break
                
        logger.info(f"[{correlation_id}] Final orchestration status: {overall_status}")
        return overall_status

    def _build_final_response(self, startup_idea: str, correlation_id: str, start_time: float, status: str, metrics: dict, agent_outputs: dict, final_data: dict, request_id: str) -> dict:
        execution_time = time.time() - start_time
        
        raw_response = {
            "metadata": {
                "startup_idea": startup_idea, # Keep in JSON payload, but not logs
                "correlation_id": correlation_id,
                "execution_time_seconds": round(execution_time, 2),
                "status": status,
                "agent_metrics": metrics,
            },
            "executive_summary": final_data.get("comparison", {}).get("executive_summary", {}),
            "web_search_agent": {"search_results": agent_outputs.get("web_search", {})},
            "market_agent": final_data.get("market", {}),
            "competitor_agent": final_data.get("competitor", {}),
            "customer_agent": final_data.get("customer", {}),
            "comparison_agent": final_data.get("comparison", {}),
            "swot_agent": final_data.get("swot", {}),
            "mvp_agent": final_data.get("mvp", {}),
            "gtm_agent": final_data.get("gtm", {}),
            "startup_score_agent": final_data.get("startup_score", {}),
            "risk_agent": final_data.get("risk", {}),
            "risk_analysis": final_data.get("risk", {}),
            "final_evaluation": {
                "executive_summary": final_data.get("comparison", {}).get("executive_summary", {}),
                "comparison": final_data.get("comparison", {}),
                "risk": final_data.get("risk", {}),
                "swot": final_data.get("swot", {}),
                "mvp": final_data.get("mvp", {}),
                "gtm": final_data.get("gtm", {}),
                "startup_score": final_data.get("startup_score", {}),
            },
        }

        final_report = GuardrailManager.verify_final_response(raw_response)
        
        if request_id:
            self._safe_publish(request_id, "Orchestrator", "completed", "Validation pipeline finished.")
            
        logger.info(
            f"[{correlation_id}] Orchestration metrics: "
            f"status={status} | duration={execution_time:.2f}s | "
            f"idea_length={len(startup_idea)}"
        )
        return final_report

    def _format_error_response(
        self,
        startup_idea: str,
        correlation_id: str,
        start_time: float,
        error_msg: str,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "metadata": {
                "startup_idea": startup_idea,
                "correlation_id": correlation_id,
                "execution_time_seconds": round(time.time() - start_time, 2),
                "status": "failed",
                "agent_metrics": metrics,
            },
            "error": error_msg,
        }
