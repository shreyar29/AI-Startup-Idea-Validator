import logging
from typing import Any, Dict
from .base_agent import BaseAgent
from contracts.roadmap_contract import RoadmapContract
from telemetry.mesh_telemetry import track_agent_metrics

logger = logging.getLogger("roadmap_agent")

class ActionRoadmapAgent(BaseAgent):
    """
    Generates a 30-60-90 day execution plan based on the validated startup idea.
    """
    def __init__(self, context: Any, llm_provider: Any):
        super().__init__(context)
        self.llm_provider = llm_provider
        
    @track_agent_metrics("roadmap_agent")
    async def get_analysis(self) -> Dict[str, Any]:
        idea = self.context.get("startup_idea")
        if not idea:
            raise ValueError("Startup idea missing from context.")
            
        logger.info(f"Generating Action Roadmap for idea: {idea}")
        
        # Stub logic. The real implementation calls the LLM with response_format={"type": "json_object"}
        # and parses the response into RoadmapContract.
        
        raw_output = {
            "day_30_plan": ["Define MVP scope", "Secure landing page domain", "Interview 10 users"],
            "day_60_plan": ["Launch closed beta", "Iterate on user feedback", "Establish analytics"],
            "day_90_plan": ["Public launch", "Execute GTM strategy", "Begin seed fundraising"],
            "key_milestones": [{"title": "MVP Launch", "month": 2}],
            "estimated_budget": "$10,000",
            "confidence_score": 0.85,
            "confidence": "HIGH"
        }
        
        validated_contract = RoadmapContract.validate_and_log(raw_output, "roadmap_agent")
        return validated_contract.model_dump()
