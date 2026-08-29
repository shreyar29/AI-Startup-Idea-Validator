from typing import Any, Dict
import logging
from export.render_schema import RenderSchema

logger = logging.getLogger(__name__)

class ExportAggregator:
    """
    Centralized Aggregation Layer for all Presentation Outputs (Dashboard, PDF, PPT).
    Guarantees no duplicate extraction logic scattered across the codebase.
    """
    
    @staticmethod
    def _safe_str(val: Any) -> str:
        if isinstance(val, str):
            return val
        if isinstance(val, dict):
            # Attempt to find a standard text field
            for key in ['insight', 'description', 'opportunity', 'risk', 'action', 'title', 'name', 'value']:
                if key in val and isinstance(val[key], str):
                    return val[key]
            # Fallback for dicts
            return next((v for v in val.values() if isinstance(v, str)), str(val))
        return str(val) if val is not None else ""
        
    @staticmethod
    def _extract_list(data_list: Any) -> list:
        if not isinstance(data_list, list):
            return []
        return [ExportAggregator._safe_str(item) for item in data_list]

    @classmethod
    def aggregate(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the raw analysis_payload and flattens it into a presentation payload.
        """
        market = payload.get("market_agent", {})
        customer = payload.get("customer_agent", {})
        competitor = payload.get("competitor_agent", {})
        risk = payload.get("risk_agent", {})
        swot = payload.get("swot_agent", {})
        mvp = payload.get("mvp_agent", {})
        gtm = payload.get("gtm_agent", {})
        startup_score = payload.get("startup_score_agent", {})
        
        # Deduplicate and finalize
        # SWOT might contain risks in 'threats', but we strictly use RiskAgent for risks
        final_risks = cls._extract_list(risk.get("top_risks", risk.get("risks", [])))
        final_recommendations = cls._extract_list(risk.get("recommendations", []))
        final_opportunities = cls._extract_list(swot.get("opportunities", []))
        
        raw_payload = {
            "metadata": payload.get("metadata", {}),
            
            "verdict": startup_score.get("verdict", "No verdict available"),
            "overall_score": startup_score.get("overall_score", 0),
            
            "executive_summary": {
                "founder_recommendation": startup_score.get("founder_recommendation", ""),
                "biggest_opportunity": final_opportunities[0] if final_opportunities else "Unknown",
                "biggest_risk": final_risks[0] if final_risks else "Unknown",
                "recommended_next_step": final_recommendations[0] if final_recommendations else "Unknown",
            },
            
            # Market
            "market": {
                "market_size": market.get("market_size", "Unknown"),
                "growth_rate": market.get("growth_rate", "Unknown"),
                "market_trends": cls._extract_list(market.get("market_trends", [])),
            },
            
            "customer": {
                "target_segments": cls._extract_list(customer.get("target_customer_segments", [])),
                "pain_points": cls._extract_list(customer.get("pain_points", [])),
            },
            
            "competitor": {
                "competitors": competitor.get("competitors", []),
                "competitive_gaps": cls._extract_list(competitor.get("competitor_gaps", [])),
            },
            
            "strategy": {
                "strengths": cls._extract_list(swot.get("strengths", [])),
                "weaknesses": cls._extract_list(swot.get("weaknesses", [])),
                "opportunities": final_opportunities,
            },
            
            "risk_and_action": {
                "top_risks": final_risks,
                "recommendations": final_recommendations,
            },
            
            "execution": {
                "core_features": cls._extract_list(mvp.get("core_features", [])),
                "mvp_scope": mvp.get("mvp_scope", "Unknown"),
                "target_segment": cls._safe_str(gtm.get("target_segment", "Unknown")),
                "acquisition_channels": cls._extract_list(gtm.get("acquisition_channels", [])),
                "pricing_strategy": cls._safe_str(gtm.get("pricing_strategy", "Unknown")),
                "launch_plan": cls._extract_list(gtm.get("launch_plan", [])),
            }
        }
        
        try:
            validated = RenderSchema.model_validate(raw_payload)
            return validated.model_dump()
        except Exception as e:
            logger.error(f"RenderSchema validation failed: {e}")
            return raw_payload
