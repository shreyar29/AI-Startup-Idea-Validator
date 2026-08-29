from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class AgentMetadata(BaseModel):
    status: str = "idle"
    failure_reason: Optional[str] = None
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class StartupIdea(BaseModel):
    description: str
    proposed_features: List[str] = Field(default_factory=list)

class MarketAnalysis(AgentMetadata):
    market_size: str = Field(default="Unknown", description="TAM, SAM, SOM sizing")
    growth_rate: str = "Unknown"
    market_trends: List[str] = Field(default_factory=list, description="Market growth trends and dynamics")
    market_maturity: str = "Unknown"
    opportunity_score: int = 50
    confidence_score: float = 0.5

class CustomerAnalysis(AgentMetadata):
    target_customer_segments: List[str] = Field(default_factory=list)
    pain_points: List[Any] = Field(default_factory=list)
    personas: List[Any] = Field(default_factory=list)
    customer_validation_metrics: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 0.5

class CompetitorAnalysis(AgentMetadata):
    competitors: List[Any] = Field(default_factory=list)
    competitor_gaps: List[str] = Field(default_factory=list)
    confidence_score: float = 0.5

class RiskAnalysis(AgentMetadata):
    risks: List[Any] = Field(default_factory=list, description="External risks, market threats, and likelihood")
    overall_risk_score: int = 50
    recommendations: List[str] = Field(default_factory=list, description="Mitigation strategies for identified risks")
    confidence_score: float = 0.5

class SWOTAnalysis(AgentMetadata):
    strengths: List[Any] = Field(default_factory=list, description="Internal strengths of the team or idea")
    weaknesses: List[Any] = Field(default_factory=list, description="Internal weaknesses of the team or idea")
    opportunities: List[Any] = Field(default_factory=list, description="Strategic positioning opportunities")
    confidence_score: float = 0.5

class MVPAnalysis(AgentMetadata):
    core_features: List[Any] = Field(default_factory=list)
    optional_features: List[Any] = Field(default_factory=list)
    future_features: List[Any] = Field(default_factory=list)
    mvp_scope: str = "Unknown"
    estimated_complexity: str = "Medium"
    confidence_score: float = 0.5

class GTMAnalysis(AgentMetadata):
    target_segment: Any = Field(default_factory=dict)
    pricing_strategy: Any = Field(default_factory=dict)
    acquisition_channels: List[Any] = Field(default_factory=list)
    launch_roadmap: Any = Field(default_factory=dict)
    launch_plan: List[Any] = Field(default_factory=list)
    go_to_market_score: int = 50
    estimated_cac_risk: str = "Medium"
    confidence_score: float = 0.5

class SharedContext(BaseModel):
    correlation_id: str
    request_id: Optional[str] = None
    idea: StartupIdea
    research: Dict[str, Any] = Field(default_factory=dict)
    market_analysis: Optional[MarketAnalysis] = None
    customer_analysis: Optional[CustomerAnalysis] = None
    competitor_analysis: Optional[CompetitorAnalysis] = None
    risk_analysis: Optional[RiskAnalysis] = None
    swot_analysis: Optional[SWOTAnalysis] = None
    mvp_analysis: Optional[MVPAnalysis] = None
    gtm_analysis: Optional[GTMAnalysis] = None
    startup_score_analysis: Optional[Any] = None

    def dict_safe(self) -> Dict[str, Any]:
        """Returns a nested dictionary representing the shared context, suitable for legacy dict-based interactions."""
        return self.model_dump(exclude_none=True)
