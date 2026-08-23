from pydantic import Field
from typing import List, Dict, Any
from .base_contract import BaseAgentContract

class EvidenceReference(BaseAgentContract):
    source: str
    url: str
    retrieval_score: float = 0.0
    confidence_score: float = 0.0
    agent_name: str

class MarketContract(BaseAgentContract):
    market_size: str = "Unknown"
    growth_rate: str = "Unknown"
    market_trends: List[str] = Field(default_factory=list)
    market_maturity: str = "Unknown"
    opportunity_score: int = 50
    confidence_score: float = 0.5
    confidence: str = "MEDIUM"
    source_traceability: List[Dict[str, Any]] = Field(default_factory=list)
