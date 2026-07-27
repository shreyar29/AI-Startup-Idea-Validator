"""
comparison_agent.py

Purpose
-------
Milestone 2 - Comparison Agent


Responsibilities
----------------
- Reads Market, Customer and Competitor analyses from Shared Context.
- Synthesizes the analyses into a final startup evaluation.
- Generates SWOT, Feature Comparison, Validation Score,
  Innovation Score and Recommendations.
- Writes ONLY to comparison_analysis.
- Exposes A2A tools for other agents.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import logging

logger = logging.getLogger("comparison_agent")


class ComparisonAnalysisError(Exception):
    """Raised when comparison analysis fails."""


class ComparisonAgent:

    def __init__(self, shared_context: dict[str, Any], llm_client=None):
        self.context = shared_context
        self.llm_client = llm_client

    async def compare(self) -> dict[str, Any]:
        """
        Main Comparison Agent entry point.
        """

        logger.info("Comparison Agent started.")

        market = self.context.get("market_analysis", {})
        customer = self.context.get("customer_analysis", {})
        competitor = self.context.get("competitor_analysis", {})
        idea = self.context.get("idea", {})

        if not (market or customer or competitor):
            logger.error("Shared Context is empty.")
            raise ComparisonAnalysisError(
                "No analysis data found in Shared Context."
            )

        logger.info(
            "Loaded Shared Context successfully. "
            "Market=%s, Customer=%s, Competitor=%s",
            bool(market),
            bool(customer),
            bool(competitor),
        )
             
        logger.info("Generating feature comparison matrix.")
        feature_matrix = self._generate_feature_matrix(
            idea,
            competitor
        )
        logger.info("Identifying competitive advantages.")
        competitive_advantages = self._identify_competitive_advantages(
            market,
            competitor
        )
        logger.info("Identifying market gaps.")
        market_gaps = self._identify_market_gaps(
            market,
            competitor
        )
        logger.info("Generating SWOT analysis.")
        swot = self._generate_swot(
            market,
            customer,
            competitor,
            competitive_advantages,
            market_gaps
        )
        logger.info("Calculating validation score.")
        validation_score = self._calculate_validation_score(
            market,
            customer,
            competitor
        )
        logger.info("Calculating innovation score.")
        innovation_score = self._calculate_innovation_score(
            competitive_advantages,
            market_gaps
        )

        confidence = self._calculate_confidence(
            market,
            customer,
            competitor
        )
        logger.info("Generating recommendations.")
        recommendations = self._generate_recommendations(
            market,
            customer,
            competitor,
            market_gaps
        )

        summary = self._generate_summary(
            validation_score,
            innovation_score,
            confidence,
            competitive_advantages,
            market_gaps
        )

        analysis = {
            "feature_matrix": feature_matrix,
            "competitive_advantages": competitive_advantages,
            "market_gaps": market_gaps,
            "swot": swot,
            "validation_score": validation_score,
            "innovation_score": innovation_score,
            "confidence": confidence,
            "recommendations": recommendations,
            "summary": summary,
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat()
        }
        logger.info("Writing results to Shared Context.")
        self.context["comparison_analysis"] = analysis

        logger.info(
    "Comparison Agent completed successfully. "
    "Validation=%d | Innovation=%d | Confidence=%s",
    validation_score,
    innovation_score,
    confidence,
)

        return analysis

    # ==========================================================
    # INTERNAL ANALYSIS FUNCTIONS
    # ==========================================================

    def _generate_feature_matrix(
        self,
        idea,
        competitor
    ):

        startup_features = idea.get(
            "proposed_features",
            []
        )

        competitors = competitor.get(
            "competitors",
            []
        )

        matrix = []

        for feature in startup_features:

            row = {
                "feature": feature,
                "startup": True,
                "competitors": []
            }

            for comp in competitors:

                row["competitors"].append({

                    "name": comp.get("name", "Unknown"),

                    "available":
                        feature.lower()
                        in [
                            f.lower()
                            for f in comp.get(
                                "features",
                                []
                            )
                        ]

                })

            matrix.append(row)

        return matrix


    def _identify_competitive_advantages(
        self,
        market,
        competitor
    ):

        advantages = []

        gaps = competitor.get(
            "gap_analysis",
            []
        )

        if gaps:

            advantages.append(
                "Startup offers features not found in competitors."
            )

        if market.get("opportunities"):

            advantages.append(
                "Startup aligns with identified market opportunities."
            )

        if competitor.get("confidence") == "low":

            advantages.append(
                "Low competition confidence indicates room for exploration."
            )

        return advantages


    def _identify_market_gaps(
        self,
        market,
        competitor
    ):

        gaps = []

        for opportunity in market.get(
            "opportunities",
            []
        ):

            gaps.append(opportunity)

        for gap in competitor.get(
            "gap_analysis",
            []
        ):

            if gap not in gaps:
                gaps.append(gap)

        return gaps    
    def _generate_swot(
        self,
        market,
        customer,
        competitor,
        advantages,
        gaps
    ):

        strengths = []
        weaknesses = []
        opportunities = []
        threats = []

        strengths.extend(advantages)

        if customer:
            strengths.append(
                "Target customer segment identified."
            )

        if not customer:
            weaknesses.append(
                "Customer analysis is incomplete."
            )

        if competitor.get("competitors"):
            threats.append(
                "Established competitors already exist."
            )

        if market.get("challenges"):
            threats.extend(
                market.get("challenges", [])
            )

        opportunities.extend(gaps)

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats
        }


    def _calculate_validation_score(
        self,
        market,
        customer,
        competitor
    ):

        score = 0

        if market.get("market_size"):
            score += 20

        if market.get("growth_rate"):
            score += 20

        if customer:
            score += 20

        if competitor.get("gap_analysis"):
            score += 20

        if market.get("opportunities"):
            score += 20

        return min(score, 100)


    def _calculate_innovation_score(
        self,
        advantages,
        gaps
    ):

        score = 60

        score += min(
            len(advantages) * 10,
            20
        )

        score += min(
            len(gaps) * 5,
            20
        )

        return min(score, 100)


    def _calculate_confidence(
        self,
        market,
        customer,
        competitor
    ):

        sections = sum([
            bool(market),
            bool(customer),
            bool(competitor)
        ])

        if sections == 3:
            return "High"

        if sections == 2:
            return "Medium"

        return "Low"


    def _generate_recommendations(
        self,
        market,
        customer,
        competitor,
        gaps
    ):

        recommendations = []

        if gaps:
            recommendations.append(
                "Focus on underserved market gaps identified during analysis."
            )

        if competitor.get("competitors"):
            recommendations.append(
                "Differentiate the product from existing competitors."
            )

        if market.get("opportunities"):
            recommendations.append(
                "Prioritize high-growth market opportunities."
            )

        if customer:
            recommendations.append(
                "Validate the solution with the identified customer segment."
            )

        if market.get("challenges"):
            recommendations.append(
                "Develop strategies to mitigate market challenges."
            )

        return recommendations


    def _generate_summary(
        self,
        validation_score,
        innovation_score,
        confidence,
        advantages,
        gaps
    ):

        return (
            f"The startup achieved a validation score of "
            f"{validation_score}/100 with an innovation score "
            f"of {innovation_score}/100. "
            f"{len(advantages)} competitive advantages and "
            f"{len(gaps)} market opportunities were identified. "
            f"Overall confidence in the analysis is {confidence}."
        )

    # =====================================================
    # A2A TOOL METHODS
    # =====================================================

    def get_validation_summary(self):
        """
        Returns the overall comparison summary.
        """
        return self.context.get(
            "comparison_analysis",
            {}
        )

    def generate_swot(self):
        """
        Returns SWOT analysis.
        """
        return self.context.get(
            "comparison_analysis",
            {}
        ).get(
            "swot",
            {}
        )

    def generate_recommendations(self):
        """
        Returns startup recommendations.
        """
        return self.context.get(
            "comparison_analysis",
            {}
        ).get(
            "recommendations",
            []
        )

    def get_feature_matrix(self):
        """
        Returns startup vs competitor feature matrix.
        """
        return self.context.get(
            "comparison_analysis",
            {}
        ).get(
            "feature_matrix",
            []
        )

    def calculate_validation_score(self):
        """
        Returns validation score.
        """
        return self.context.get(
            "comparison_analysis",
            {}
        ).get(
            "validation_score",
            0
        )

    def get_competitive_advantages(self):
        """
        A2A Tool:
        Returns startup competitive advantages.
        """
        return self.context.get(
            "comparison_analysis",
            {}
        ).get(
            "competitive_advantages",
            []
        )

    def get_market_gap_analysis(self):
        """
        A2A Tool:
        Returns identified market gaps.
        """
        return self.context.get(
            "comparison_analysis",
            {}
        ).get(
            "market_gaps",
            []
        )

    def get_innovation_score(self):
        """
        A2A Tool:
        Returns innovation score.
        """
        return self.context.get(
            "comparison_analysis",
            {}
        ).get(
            "innovation_score",
            0
        )