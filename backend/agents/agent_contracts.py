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
    market_size: str = Field(description="TAM, SAM, SOM sizing with explanation if data is unavailable")
    growth_rate: str = Field(description="Market growth rate with explanation if data is unavailable")
    market_trends: List[str] = Field(default_factory=list, description="Market growth trends and dynamics")
    market_maturity: str = Field(description="Maturity stage with explanation if data is unavailable")
    opportunity_score: int = Field(default=50, description="Score from 0-100")
    confidence_level: str = Field(default="Medium", description="High, Medium, or Low based on evidence strength")

class CustomerAnalysis(AgentMetadata):
    target_customer_segments: List[str] = Field(default_factory=list)
    pain_points: List[Any] = Field(default_factory=list)
    personas: List[Any] = Field(default_factory=list)
    customer_validation_metrics: Dict[str, Any] = Field(default_factory=dict)
    customer_score: int = Field(default=50, description="Score from 0-100")
    confidence_level: str = Field(default="Medium", description="High, Medium, or Low based on evidence strength")

class CompetitorAnalysis(AgentMetadata):
    competitors: List[Any] = Field(default_factory=list)
    competitor_gaps: List[str] = Field(default_factory=list)
    competition_score: int = Field(default=50, description="Score from 0-100")
    confidence_level: str = Field(default="Medium", description="High, Medium, or Low based on evidence strength")

class RiskAnalysis(AgentMetadata):
    risks: List[Any] = Field(default_factory=list, description="External risks, market threats, and likelihood")
    overall_risk_score: int = Field(default=50, description="Score from 0-100")
    overall_risk_level: str = Field(default="Medium", description="Critical, High, Medium, or Low")
    recommendations: List[str] = Field(default_factory=list, description="Mitigation strategies for identified risks")
    confidence_level: str = Field(default="Medium", description="High, Medium, or Low based on evidence strength")

class SWOTAnalysis(AgentMetadata):
    strengths: List[Any] = Field(default_factory=list, description="Internal strengths of the team or idea")
    weaknesses: List[Any] = Field(default_factory=list, description="Internal weaknesses of the team or idea")
    opportunities: List[Any] = Field(default_factory=list, description="Strategic positioning opportunities")
    threats: List[Any] = Field(default_factory=list, description="External threats and risks")
    tows_matrix: Dict[str, Any] = Field(default_factory=dict, description="Actionable strategies for each SWOT intersection")
    executive_summary: str = Field(default="", description="High level strategic overview")
    strategic_recommendation: str = Field(default="", description="Final overarching recommendation")
    swot_score: int = Field(default=50, description="Score from 0-100")
    confidence_level: str = Field(default="Medium", description="High, Medium, or Low based on evidence strength")

class MVPAnalysis(AgentMetadata):
    core_features: List[Any] = Field(default_factory=list)
    optional_features: List[Any] = Field(default_factory=list)
    future_features: List[Any] = Field(default_factory=list)
    mvp_scope: str = Field(description="Scope description with explanation if data is unavailable")
    estimated_complexity: str = Field(default="Medium", description="Low, Medium, or High complexity")
    mvp_score: int = Field(default=50, description="Score from 0-100")
    confidence_level: str = Field(default="Medium", description="High, Medium, or Low based on evidence strength")

class GTMAnalysis(AgentMetadata):
    target_segment: Any = Field(default_factory=dict)
    pricing_strategy: Any = Field(default_factory=dict)
    acquisition_channels: List[Any] = Field(default_factory=list)
    launch_roadmap: Any = Field(default_factory=dict)
    launch_plan: List[Any] = Field(default_factory=list)
    action_plan: Any = Field(default_factory=dict)
    funnel_pipeline: List[Any] = Field(default_factory=list)
    cac_ltv_metrics: Any = Field(default_factory=dict)
    go_to_market_score: int = Field(default=50, description="Score from 0-100")
    estimated_cac_risk: str = Field(default="Medium", description="Low, Medium, or High")
    confidence_level: str = Field(default="Medium", description="High, Medium, or Low based on evidence strength")

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
