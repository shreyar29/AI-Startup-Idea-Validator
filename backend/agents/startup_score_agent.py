"""
startup_score_agent.py
(Startup Score Agent)

Purpose:
Production-grade Startup Score Agent.
Generates an objective startup viability score using all previous agent outputs.
Delegates heavy calculation to the StartupScoringService.
"""

import asyncio
import logging
import time
from typing import Any, Dict

from services.startup_scoring_service import StartupScoringService

logger = logging.getLogger("startup_score_agent")

class StartupScoreAgent:
    """
    Evaluates all existing startup intelligence to generate a viability score.

    Operates as a decentralized node in the A2A Mesh Network.
    """

    def __init__(self, shared_context: dict, llm_client=None):
        self.context = shared_context
        self.llm_client = llm_client
        self.peers = {}
        self._analysis_task = None
        self.status = "idle"
        self.scoring_service = StartupScoringService()

    def connect_peers(self, peers: dict):
        """Connect this agent to other agents in the mesh."""
        self.peers = peers

    async def get_analysis(self):
        """
        Mesh endpoint.
        Runs the analysis once and caches the asyncio task.
        """
        if self._analysis_task is not None:
            if self._analysis_task.done():
                try:
                    self._analysis_task.result()
                    if self.status in ["failed", "timeout"]:
                        self._analysis_task = None
                except Exception:
                    self._analysis_task = None

        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(
                self._perform_analysis()
            )

        try:
            return await self._analysis_task
        except asyncio.CancelledError:
            logger.warning("StartupScoreAgent: Task cancelled.")
            self._analysis_task = None
            self.status = "failed"
            raise

    async def _perform_analysis(self):
        """Run the Startup Score analysis."""
        self.status = "started"
        start_time = time.time()

        correlation_id = self.context.get("correlation_id", "N/A")
        log_prefix = f"[{correlation_id}] StartupScoreAgent:"

        try:
            logger.info(f"{log_prefix} Starting Startup Score analysis.")

            # Await required peers to prevent race condition
            if self.peers:
                dependencies = []
                for peer_name in ["market", "customer", "competitor", "risk", "swot", "mvp", "gtm"]:
                    if peer_name in self.peers:
                        dependencies.append(self.peers[peer_name].get_analysis())
                
                if dependencies:
                    await asyncio.gather(*dependencies, return_exceptions=True)

            result = await self.analyze(log_prefix)

            self.status = "success"
            duration = time.time() - start_time
            logger.info(f"{log_prefix} Completed successfully in {duration:.2f}s.")

            return result

        except asyncio.TimeoutError as exc:
            self.status = "timeout"
            logger.error(f"{log_prefix} Startup Score analysis timed out: {exc}")
            return self._return_degraded("Startup Score analysis timed out.")

        except Exception as exc:
            self.status = "failed"
            logger.exception(f"{log_prefix} Startup Score analysis failed: {exc}")
            return self._return_degraded(f"Unexpected failure: {str(exc)}")

    def _return_degraded(self, reason: str) -> Dict[str, Any]:
        """Return a safe response when analysis fails."""
        scorecard = self.scoring_service.get_degraded_scorecard(reason, self.status)
        analysis_dict = scorecard.model_dump()
        self.context["startup_score_analysis"] = analysis_dict
        return analysis_dict

    async def analyze(self, log_prefix: str = "StartupScoreAgent:") -> Dict[str, Any]:
        """Main Startup Score Agent entry point."""
        logger.info(f"{log_prefix} Execution started.")
            
        scorecard = self.scoring_service.calculate_scorecard(self.context)
        analysis_dict = scorecard.model_dump()
        
        self.context["startup_score_analysis"] = analysis_dict

        logger.info(
            f"{log_prefix} Startup Score Complete. "
            f"Overall: {analysis_dict['overall_score']}/100, Verdict: {analysis_dict['verdict']}"
        )

        return analysis_dict
