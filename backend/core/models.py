from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class IdeaModel(BaseModel):
    description: str
    proposed_features: List[str] = Field(default_factory=list)

class SharedContext(BaseModel):
    """
    Strongly typed Pydantic model for the shared context across the P2P mesh network.
    Includes dict-like access methods to preserve backwards compatibility with existing agents.
    """
    model_config = ConfigDict(extra="allow")

    idea: IdeaModel
    correlation_id: str
    request_id: Optional[str] = None
    research: Dict[str, Any] = Field(default_factory=dict)
    market_analysis: Dict[str, Any] = Field(default_factory=dict)
    customer_analysis: Dict[str, Any] = Field(default_factory=dict)
    competitor_analysis: Dict[str, Any] = Field(default_factory=dict)
    comparison_analysis: Dict[str, Any] = Field(default_factory=dict)
    risk_analysis: Dict[str, Any] = Field(default_factory=dict)
    swot_analysis: Dict[str, Any] = Field(default_factory=dict)
    mvp_analysis: Dict[str, Any] = Field(default_factory=dict)
    gtm_analysis: Dict[str, Any] = Field(default_factory=dict)
    startup_score_analysis: Dict[str, Any] = Field(default_factory=dict)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)
