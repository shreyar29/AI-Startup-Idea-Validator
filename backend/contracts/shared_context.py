import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("contracts.shared_context")

class SharedContextContract(BaseModel):
    correlation_id: str
    report_id: Optional[str] = None
    session_id: Optional[str] = None
    idea: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Agent Results
    web_search: Optional[Dict[str, Any]] = None
    market_analysis: Optional[Dict[str, Any]] = None
    competitor_analysis: Optional[Dict[str, Any]] = None
    customer_analysis: Optional[Dict[str, Any]] = None
    swot_analysis: Optional[Dict[str, Any]] = None
    risk_analysis: Optional[Dict[str, Any]] = None
    mvp_analysis: Optional[Dict[str, Any]] = None
    gtm_analysis: Optional[Dict[str, Any]] = None
    comparison_analysis: Optional[Dict[str, Any]] = None
    startup_score_analysis: Optional[Dict[str, Any]] = None
