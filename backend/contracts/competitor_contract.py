from pydantic import Field
from typing import List, Dict, Any
from .base_contract import BaseAgentContract

class CompetitorContract(BaseAgentContract):
    competitors: List[Dict[str, Any]] = Field(default_factory=list)
    competitor_gaps: List[str] = Field(default_factory=list)
    gap_analysis: List[str] = Field(default_factory=list)
    no_competitor_data_found: bool = False
    confidence_score: float = 0.5
    confidence: str = "MEDIUM"
    source_traceability: List[Dict[str, Any]] = Field(default_factory=list)
