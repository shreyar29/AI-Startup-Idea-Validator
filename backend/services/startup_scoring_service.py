from typing import Dict, Any, List
from agents.score_models import StartupScorecard, Verdict, Confidence
from core.agent_config import AGENT_REGISTRY
from services.scoring_constants import *
import logging

logger = logging.getLogger("startup_scoring_service")

class StartupScoringService:
    """
    Investor-Grade Startup Scoring Engine.
    Operates completely deterministically using enriched intelligence payloads 
    from the upstream P2P agent network. Calculates dynamic weighting based on 
    startup category and maps scores to venture capital frameworks.
    """
    
    def calculate_scorecard(self, context: Dict[str, Any]) -> StartupScorecard:
        # Require at least 4 successful upstream analyses
        successful_analyses = 0
        for key in ["market_analysis", "customer_analysis", "competitor_analysis", "risk_analysis", "swot_analysis", "mvp_analysis", "gtm_analysis"]:
            data = context.get(key)
            if data and isinstance(data, dict) and len(data) > 1 and data.get("status") != "failed":
                successful_analyses += 1
                
        if successful_analyses < 4:
            return self.get_degraded_scorecard("Insufficient data for startup scoring")

        # Delegate to specialized extractors that understand Evidence-Quality payloads
        market_score = self._calc_market_score(context.get("market_analysis", {}))
        customer_score = self._calc_customer_score(context.get("customer_analysis", {}))
        competition_score = self._calc_competition_score(context.get("competitor_analysis", {}))
        risk_score = self._calc_risk_score(context.get("risk_analysis", {}))
        execution_score = self._calc_execution_score(context.get("mvp_analysis", {}))
        gtm_score = self._calc_gtm_score(context.get("gtm_analysis", {}))

        # Dynamic Weighting Engine based on Startup Category
        idea_data = context.get("idea", {})
        idea_desc = str(idea_data.get("description", "")).lower()
        
        # Base AgentConfig Weights
        w_market = AGENT_REGISTRY["market"].weight
        w_customer = AGENT_REGISTRY["customer"].weight
        w_competitor = AGENT_REGISTRY["competitor"].weight
        w_risk = AGENT_REGISTRY["risk"].weight
        w_execution = AGENT_REGISTRY["mvp"].weight
        w_gtm = AGENT_REGISTRY["gtm"].weight

        # Apply Dynamic Category Adjustments
        is_deeptech = any(kw in idea_desc for kw in ["ai", "llm", "hardware", "biotech", "quantum", "robotics"])
        is_b2b_saas = any(kw in idea_desc for kw in ["b2b", "enterprise", "saas", "dashboard", "workplace"])
        
        if is_deeptech:
            w_execution += 0.15  # Execution and technical risk are paramount
            w_risk += 0.10
            w_gtm = max(0.05, w_gtm - 0.10) # GTM is secondary to feasibility
        elif is_b2b_saas:
            w_competitor += 0.10 # Crowded markets require strong differentiation
            w_gtm += 0.10 # Distribution is critical
            w_execution = max(0.05, w_execution - 0.10)
        
        total_weight = max(0.01, w_market + w_customer + w_competitor + w_risk + w_execution + w_gtm)
        
        overall_score_raw = (
            (market_score * w_market) +
            (customer_score * w_customer) +
            (competition_score * w_competitor) +
            (risk_score * w_risk) +
            (execution_score * w_execution) +
            (gtm_score * w_gtm)
        ) / total_weight

        overall_score = max(0, min(100, int(round(overall_score_raw))))
        
        verdict = self._determine_verdict(overall_score)
        confidence = self._determine_confidence(context, successful_analyses)
        investment_readiness = self._calculate_investment_readiness(overall_score, risk_score, execution_score, confidence)

        # Explainable Score Drivers
        score_explanation = [
            f"Market Attractiveness (Weight {w_market:.2f}): {market_score}/100",
            f"Customer Validation (Weight {w_customer:.2f}): {customer_score}/100",
            f"Competitive Moat (Weight {w_competitor:.2f}): {competition_score}/100",
            f"Risk Resilience (Weight {w_risk:.2f}): {risk_score}/100 (Higher is safer)",
            f"Execution Feasibility (Weight {w_execution:.2f}): {execution_score}/100",
            f"Go-To-Market Strategy (Weight {w_gtm:.2f}): {gtm_score}/100"
        ]
        


        return StartupScorecard(
            overall_score=overall_score,
            market_score=market_score,
            customer_score=customer_score,
            competition_score=competition_score,
            risk_score=risk_score,
            execution_score=execution_score,
            gtm_score=gtm_score,
            verdict=verdict,
            confidence_level=confidence,
            score_explanation=score_explanation,
            investment_readiness=investment_readiness,
            status="success"
        )

    def get_degraded_scorecard(self, reason: str, status: str = "failed") -> StartupScorecard:
        is_insufficient = "Insufficient" in reason
        return StartupScorecard(
            overall_score=0,
            market_score=0,
            customer_score=0,
            competition_score=0,
            risk_score=0,
            execution_score=0,
            gtm_score=0,
            verdict=Verdict.INSUFFICIENT_DATA,
            confidence_level=Confidence.LOW,
            score_explanation=[],
            investment_readiness="Not Ready (Insufficient Data)",
            message="Insufficient data for startup scoring" if is_insufficient else reason,
            status="degraded" if is_insufficient else status
        )

    def _determine_verdict(self, overall_score: int) -> Verdict:
        if overall_score >= VERDICT_EXCEPTIONAL_THRESHOLD: return Verdict.EXCEPTIONAL
        elif overall_score >= VERDICT_PROMISING_THRESHOLD: return Verdict.PROMISING
        elif overall_score >= VERDICT_MODERATE_THRESHOLD: return Verdict.MODERATE
        elif overall_score >= VERDICT_HIGH_RISK_THRESHOLD: return Verdict.HIGH_RISK
        else: return Verdict.NOT_RECOMMENDED
        
    def _calculate_investment_readiness(self, overall_score: int, risk_score: int, execution_score: int, confidence: Confidence) -> str:
        if confidence == Confidence.LOW:
            return "Seed Stage - Requires Core Validation"
            
        if overall_score >= 80 and risk_score >= 60 and execution_score >= 70:
            return "Series A Ready - Strong fundamentals and clear execution path."
        elif overall_score >= 65 and risk_score >= 40:
            return "Late Seed Ready - Promising market, moderate execution risks."
        elif overall_score >= 50:
            return "Pre-Seed Ready - Needs significant de-risking."
        else:
            return "Not Investable - Pivots Required."

    def _determine_confidence(self, context: Dict[str, Any], successful_analyses: int) -> Confidence:
        """Propagates confidence from upstream agents based on evidence quality."""
        high_conf_count = 0
        total_evals = 0
        
        for key in ["market_analysis", "customer_analysis", "competitor_analysis", "risk_analysis", "swot_analysis", "mvp_analysis", "gtm_analysis"]:
            data = context.get(key, {})
            if data and isinstance(data, dict):
                total_evals += 1
                conf = data.get("confidence_score", data.get("confidence", ""))
                if str(conf).lower() == "high":
                    high_conf_count += 1
                    
        if successful_analyses >= 6 and high_conf_count >= 4:
            return Confidence.HIGH
        elif successful_analyses >= 4 and high_conf_count >= 2:
            return Confidence.MEDIUM
            
        return Confidence.LOW

    def _calc_market_score(self, market: Dict[str, Any]) -> int:
        """Consumes opportunity_score directly from Market Agent."""
        if not market: return 0
        if "opportunity_score" in market:
            return market["opportunity_score"]
        return BASE_MARKET_SCORE
        
    def _calc_customer_score(self, customer: Dict[str, Any]) -> int:
        """Consumes validation_score directly from Customer Agent."""
        if not customer: return 0
        metrics = customer.get("customer_validation_metrics", {})
        if "validation_score" in metrics:
            return metrics["validation_score"]
        return BASE_CUSTOMER_SCORE

    def _calc_competition_score(self, competitor: Dict[str, Any]) -> int:
        """Inverts threat_score into a competitive whitespace score."""
        if not competitor: return 0
        comps = competitor.get("competitors", [])
        
        if comps and isinstance(comps, list) and isinstance(comps[0], dict) and "threat_score" in comps[0]:
            # Average threat score of top 3 competitors
            top_threats = sorted([c.get("threat_score", 0) for c in comps], reverse=True)[:3]
            avg_threat = sum(top_threats) / len(top_threats) if top_threats else 0
            # Higher threat means lower whitespace score
            return max(0, min(100, 100 - int(avg_threat)))
            
        return BASE_COMPETITION_SCORE

    def _calc_risk_score(self, risk: Dict[str, Any]) -> int:
        """Inverts overall_risk_score into a resilience score."""
        if not risk: return 0
        if "overall_risk_score" in risk:
            # 100 Risk = 0 Resilience. 0 Risk = 100 Resilience.
            return max(0, min(100, 100 - risk["overall_risk_score"]))
        return BASE_RISK_SCORE

    def _calc_execution_score(self, mvp: Dict[str, Any]) -> int:
        """Calculates execution feasibility from MVP complexity."""
        if not mvp: return 0
        
        # Penalize when feature scope becomes excessive
        complexity = mvp.get("estimated_complexity", "Medium")
        core_features = len(mvp.get("core_features", []))
        
        if complexity == "Low" and core_features <= 3:
            return 95
        elif complexity == "Low":
            return 85
        elif complexity == "Medium" and core_features <= 5:
            return 75
        elif complexity == "Medium":
            return 60
        elif complexity == "High" and core_features > 8:
            return 25 # Extreme penalty for scope creep
        elif complexity == "High":
            return 40
            
        return BASE_EXECUTION_SCORE

    def _calc_gtm_score(self, gtm: Dict[str, Any]) -> int:
        """Legacy GTM scoring fallback until GTM agent is upgraded."""
        if not gtm: return 0
        score = BASE_GTM_SCORE
        score += len(gtm.get("launch_channels", [])) * GTM_CHANNEL_MULTIPLIER
        score += len(gtm.get("growth_hacks", [])) * GTM_HACK_MULTIPLIER
        if "High" in str(gtm.get("confidence", "")): score += CONFIDENCE_HIGH_BONUS_10
        return max(0, min(100, score))
