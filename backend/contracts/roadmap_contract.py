from pydantic import Field
from typing import List, Dict, Any
from .base_contract import BaseAgentContract

class RoadmapContract(BaseAgentContract):
    day_30_plan: List[str] = Field(default_factory=list)
    day_60_plan: List[str] = Field(default_factory=list)
    day_90_plan: List[str] = Field(default_factory=list)
    key_milestones: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_budget: str = "Unknown"
    confidence_score: float = 0.5
    confidence: str = "MEDIUM"
    source_traceability: List[Dict[str, Any]] = Field(default_factory=list)
