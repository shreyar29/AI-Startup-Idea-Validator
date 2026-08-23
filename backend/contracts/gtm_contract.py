from pydantic import Field
from typing import List, Dict, Any
from .base_contract import BaseAgentContract

class GTMContract(BaseAgentContract):
    target_segment: Dict[str, Any] = Field(default_factory=dict)
    pricing_strategy: Dict[str, Any] = Field(default_factory=dict)
    acquisition_channels: List[Dict[str, Any]] = Field(default_factory=list)
    launch_roadmap: Dict[str, Any] = Field(default_factory=dict)
    launch_plan: List[Dict[str, Any]] = Field(default_factory=list)
    go_to_market_score: int = 50
    estimated_cac_risk: str = "Medium"
    confidence_score: float = 0.5
    confidence: str = "MEDIUM"
    source_traceability: List[Dict[str, Any]] = Field(default_factory=list)
