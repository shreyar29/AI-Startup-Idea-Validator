"""
comparison_agent.py

Purpose
-------
Implements the Comparison Agent.

Responsibilities
----------------
- Read Market, Customer and Competitor analyses from Shared Context.
- Compare the startup idea against competitors.
- Generate SWOT analysis.
- Calculate validation score.
- Generate recommendations.
- Write only to comparison_analysis.
"""

from __future__ import annotations

from typing import Any
from datetime import datetime


class ComparisonAnalysisError(Exception):
    """Raised when comparison analysis fails."""


class ComparisonAgent:
    """
    Comparison Agent for Milestone 2.

    Reads:
        market_analysis
        customer_analysis
        competitor_analysis

    Writes:
        comparison_analysis
    """

    def __init__(self, shared_context: dict[str, Any]):
        self.context = shared_context

    async def compare(self) -> dict[str, Any]:
        """
        Main entry point.
        """

        market = self.context.get("market_analysis", {})
        customer = self.context.get("customer_analysis", {})
        competitor = self.context.get("competitor_analysis", {})

        feature_matrix = self._generate_feature_matrix(competitor)
        swot = self._generate_swot(market, customer, competitor)

        validation_score = self._calculate_validation_score(
            market,
            customer,
            competitor
        )

        recommendations = self._generate_recommendations(
            market,
            customer,
            competitor
        )

        result = {
            "feature_matrix": feature_matrix,
            "competitive_advantages": [],
            "market_gaps": [],
            "swot": swot,
            "validation_score": validation_score,
            "innovation_score": 80,
            "confidence": "Medium",
            "recommendations": recommendations,
            "summary": "Comparison analysis completed successfully.",
            "generated_at": datetime.utcnow().isoformat()
        }

        self.context["comparison_analysis"] = result

        return result

    def _generate_feature_matrix(self, competitor: dict) -> list:
        """
        Compare startup features against competitors.
        """
        return []

    def _generate_swot(
        self,
        market: dict,
        customer: dict,
        competitor: dict
    ) -> dict:

        return {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }

    def _calculate_validation_score(
        self,
        market: dict,
        customer: dict,
        competitor: dict
    ) -> int:

        score = 50

        if market:
            score += 15

        if customer:
            score += 15

        if competitor:
            score += 20

        return min(score, 100)

    def _generate_recommendations(
        self,
        market: dict,
        customer: dict,
        competitor: dict
    ) -> list:

        recommendations = []

        recommendations.append(
            "Focus on differentiating features from competitors."
        )

        recommendations.append(
            "Target underserved customer segments."
        )

        recommendations.append(
            "Validate pricing with market research."
        )

        return recommendations

    # =====================================================
    # A2A TOOL METHODS
    # =====================================================

    def get_validation_summary(self):
        return self.context.get("comparison_analysis", {})

    def generate_swot(self):
        return self.context.get(
            "comparison_analysis",
            {}
        ).get("swot", {})

    def generate_recommendations(self):
        return self.context.get(
            "comparison_analysis",
            {}
        ).get("recommendations", [])

    def get_feature_matrix(self):
        return self.context.get(
            "comparison_analysis",
            {}
        ).get("feature_matrix", [])

    def calculate_validation_score(self):
        return self.context.get(
            "comparison_analysis",
            {}
        ).get("validation_score", 0)