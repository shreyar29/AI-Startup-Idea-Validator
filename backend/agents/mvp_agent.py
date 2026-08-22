from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from utils.error_handler import (
    safe_parse_llm_json,
    MalformedLLMOutputError
)

logger = logging.getLogger("mvp_agent")


class MVPRecommendationError(Exception):
    """Raised when MVP recommendation fails."""


class MVPAgent:
    """
    Milestone 3 - MVP Recommendation Agent

    Reads:
        comparison_analysis
        swot_analysis
        risk_analysis
        idea

    Writes:
        mvp_analysis

    Main responsibilities:
        1. Identify candidate MVP features.
        2. Prioritize features using MoSCoW.
        3. Consider business value and user needs.
        4. Consider competitive position.
        5. Consider identified startup risks.
        6. Recommend a focused MVP scope.
        7. Identify deferred features.
        8. Calculate MVP readiness score.
    """

    def __init__(
        self,
        shared_context: dict[str, Any],
        llm_client=None
    ):
        self.context = shared_context
        self.llm_client = llm_client
        self.peers = {}
        self._analysis_task = None
        self.status = "idle"

    # ==========================================================
    # A2A SUPPORT
    # ==========================================================

    def connect_peers(self, peers: dict):
        """
        Connect MVP Agent to other agents in the A2A network.
        """
        self.peers = peers

    async def get_analysis(self):

        if self._analysis_task is not None:

            if self._analysis_task.done():

                try:
                    self._analysis_task.result()

                except Exception:
                    self._analysis_task = None

        if self._analysis_task is None:

            self._analysis_task = asyncio.create_task(
                self._perform_analysis()
            )

        try:

            return await self._analysis_task

        except asyncio.CancelledError:

            logger.warning(
                "MVP Agent task cancelled."
            )

            self._analysis_task = None
            self.status = "failed"

            raise

    async def _perform_analysis(self):

        self.status = "started"

        try:

            result = await self.analyze()

            self.status = "success"

            return result

        except asyncio.TimeoutError as exc:

            self.status = "timeout"

            logger.error(
                "MVP Agent timed out: %s",
                exc
            )

            return self._return_fallback(
                "MVP analysis timed out."
            )

        except Exception as exc:

            self.status = "failed"

            logger.exception(
                "MVP Agent failed: %s",
                exc
            )

            return self._return_fallback(
                f"Unexpected failure: {str(exc)}"
            )

    # ==========================================================
    # GET INPUTS
    # ==========================================================

    def _get_inputs(self):

        comparison = self.context.get(
            "comparison_analysis",
            {}
        )

        swot = self.context.get(
            "swot_analysis",
            {}
        )

        risk = self.context.get(
            "risk_analysis",
            {}
        )

        idea = self.context.get(
            "idea",
            {}
        )

        return comparison, swot, risk, idea

    # ==========================================================
    # SAFE LIST
    # ==========================================================

    @staticmethod
    def _safe_list(value):

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            return [value]

        return []

    # ==========================================================
    # EXTRACT FEATURES
    # ==========================================================

    def _extract_features(
        self,
        comparison,
        idea
    ):
        """
        Extract actual startup features.

        Priority:
        1. idea.proposed_features
        2. comparison.feature_matrix
        """

        features = []

        # ------------------------------------------------------
        # 1. Startup proposed features
        # ------------------------------------------------------

        proposed_features = idea.get(
            "proposed_features",
            []
        )

        for feature in proposed_features:

            if isinstance(feature, dict):

                name = (
                    feature.get("feature")
                    or feature.get("name")
                    or feature.get("description")
                )

                if name:
                    features.append(str(name))

            elif feature:

                features.append(str(feature))

        # ------------------------------------------------------
        # 2. Comparison feature matrix
        # ------------------------------------------------------

        feature_matrix = comparison.get(
            "feature_matrix",
            []
        )

        for item in feature_matrix:

            if not isinstance(item, dict):
                continue

            feature = item.get(
                "feature"
            )

            if feature:
                features.append(
                    str(feature)
                )

        # ------------------------------------------------------
        # Remove duplicates
        # ------------------------------------------------------

        unique_features = []
        seen = set()

        for feature in features:

            feature = feature.strip()

            if not feature:
                continue

            key = feature.lower()

            if key not in seen:

                seen.add(key)

                unique_features.append(
                    feature
                )

        return unique_features

    # ==========================================================
    # FEATURE MATRIX LOOKUP
    # ==========================================================

    def _get_feature_matrix_item(
        self,
        feature,
        comparison
    ):

        feature_matrix = comparison.get(
            "feature_matrix",
            []
        )

        for item in feature_matrix:

            if not isinstance(item, dict):
                continue

            if str(
                item.get("feature", "")
            ).lower() == feature.lower():

                return item

        return {}

    # ==========================================================
    # RISK LOOKUP
    # ==========================================================

    def _get_relevant_risks(
        self,
        feature,
        risk
    ):

        relevant = []

        risks = risk.get(
            "risks",
            []
        )

        feature_words = set(
            feature.lower().split()
        )

        for item in risks:

            if not isinstance(item, dict):
                continue

            risk_text = str(
                item.get("risk", "")
            ).lower()

            risk_words = set(
                risk_text.split()
            )

            # Simple keyword overlap
            if feature_words.intersection(
                risk_words
            ):

                relevant.append(item)

        return relevant

    # ==========================================================
    # SCORE FEATURE
    # ==========================================================

    def _score_feature(
        self,
        feature,
        comparison,
        swot,
        risk
    ):
        """
        Calculate feature priority using:

        Business Value
        User Need
        Competitive Value
        Risk Reduction
        """

        business_value = 1
        user_need = 1
        competitive_value = 1
        risk_reduction = 1

        feature_text = feature.lower()

        # ------------------------------------------------------
        # Comparison evidence
        # ------------------------------------------------------

        feature_matrix_item = (
            self._get_feature_matrix_item(
                feature,
                comparison
            )
        )

        competitors = feature_matrix_item.get(
            "competitors",
            []
        )

        competitors_have_feature = any(
            isinstance(comp, dict)
            and comp.get("available") is True
            for comp in competitors
        )

        # If competitors do not have the feature,
        # it can provide differentiation.
        if competitors and not competitors_have_feature:

            competitive_value += 2

        # ------------------------------------------------------
        # Competitive advantages
        # ------------------------------------------------------

        advantages = comparison.get(
            "competitive_advantages",
            []
        )

        for advantage in advantages:

            if feature_text in str(
                advantage
            ).lower():

                competitive_value += 2

        # ------------------------------------------------------
        # Market gaps
        # ------------------------------------------------------

        market_gaps = comparison.get(
            "market_gaps",
            []
        )

        for gap in market_gaps:

            gap_text = str(gap).lower()

            if any(
                word in gap_text
                for word in feature_text.split()
                if len(word) > 3
            ):

                business_value += 1
                user_need += 1

        # ------------------------------------------------------
        # SWOT opportunities
        # ------------------------------------------------------

        opportunities = swot.get(
            "opportunities",
            []
        )

        for opportunity in opportunities:

            if isinstance(
                opportunity,
                dict
            ):

                opportunity_text = str(
                    opportunity.get(
                        "point",
                        ""
                    )
                ).lower()

            else:

                opportunity_text = str(
                    opportunity
                ).lower()

            if any(
                word in opportunity_text
                for word in feature_text.split()
                if len(word) > 3
            ):

                business_value += 1

        # ------------------------------------------------------
        # SWOT weaknesses
        # ------------------------------------------------------

        weaknesses = swot.get(
            "weaknesses",
            []
        )

        for weakness in weaknesses:

            if isinstance(
                weakness,
                dict
            ):

                weakness_text = str(
                    weakness.get(
                        "point",
                        ""
                    )
                ).lower()

            else:

                weakness_text = str(
                    weakness
                ).lower()

            if any(
                word in weakness_text
                for word in feature_text.split()
                if len(word) > 3
            ):

                risk_reduction += 1

        # ------------------------------------------------------
        # Risk analysis
        # ------------------------------------------------------

        relevant_risks = (
            self._get_relevant_risks(
                feature,
                risk
            )
        )

        for risk_item in relevant_risks:

            severity = str(
                risk_item.get(
                    "severity",
                    ""
                )
            ).lower()

            if severity == "critical":
                risk_reduction += 3

            elif severity == "high":
                risk_reduction += 2

            elif severity == "medium":
                risk_reduction += 1

        # ------------------------------------------------------
        # Risk-related keywords
        # ------------------------------------------------------

        risk_keywords = [
            "security",
            "privacy",
            "payment",
            "authentication",
            "validation",
            "reliability",
            "safety"
        ]

        if any(
            keyword in feature_text
            for keyword in risk_keywords
        ):

            risk_reduction += 2

        # ------------------------------------------------------
        # User/core-value keywords
        # ------------------------------------------------------

        user_keywords = [
            "user",
            "customer",
            "core",
            "search",
            "booking",
            "recommendation",
            "dashboard",
            "profile",
            "login"
        ]

        if any(
            keyword in feature_text
            for keyword in user_keywords
        ):

            user_need += 2

        # ------------------------------------------------------
        # Business keywords
        # ------------------------------------------------------

        business_keywords = [
            "payment",
            "subscription",
            "revenue",
            "checkout",
            "transaction"
        ]

        if any(
            keyword in feature_text
            for keyword in business_keywords
        ):

            business_value += 2

        # ------------------------------------------------------
        # Limit scores to 1-5
        # ------------------------------------------------------

        business_value = min(
            max(business_value, 1),
            5
        )

        user_need = min(
            max(user_need, 1),
            5
        )

        competitive_value = min(
            max(competitive_value, 1),
            5
        )

        risk_reduction = min(
            max(risk_reduction, 1),
            5
        )

        total_score = (
            business_value
            + user_need
            + competitive_value
            + risk_reduction
        )

        return {
            "business_value": business_value,
            "user_need": user_need,
            "competitive_value": competitive_value,
            "risk_reduction": risk_reduction,
            "total_score": total_score
        }

    # ==========================================================
    # MOSCOW PRIORITIZATION
    # ==========================================================

    def _prioritize_features(
        self,
        features,
        comparison,
        swot,
        risk
    ):

        result = {
            "must_have": [],
            "should_have": [],
            "could_have": [],
            "wont_have": []
        }

        scored_features = []

        for feature in features:

            scores = self._score_feature(
                feature,
                comparison,
                swot,
                risk
            )

            scored_features.append(
                (
                    feature,
                    scores
                )
            )

        # Highest-value features first
        scored_features.sort(
            key=lambda item: item[1]["total_score"],
            reverse=True
        )

        for feature, scores in scored_features:

            total = scores[
                "total_score"
            ]

            if total >= 15:

                category = "must_have"

                rationale = (
                    "Essential for delivering strong user "
                    "and business value while addressing "
                    "important strategic or risk factors."
                )

            elif total >= 11:

                category = "should_have"

                rationale = (
                    "Provides significant value but is not "
                    "required for the first product validation."
                )

            elif total >= 7:

                category = "could_have"

                rationale = (
                    "Useful enhancement that can be introduced "
                    "after the core MVP is validated."
                )

            else:

                category = "wont_have"

                rationale = (
                    "Low priority for the initial MVP and "
                    "can be deferred to a later release."
                )

            result[
                category
            ].append(
                {
                    "feature": feature,
                    **scores,
                    "rationale": rationale
                }
            )

        return result

    # ==========================================================
    # MVP SCOPE
    # ==========================================================

    def _generate_scope(
        self,
        prioritized
    ):

        must_have = prioritized[
            "must_have"
        ]

        should_have = prioritized[
            "should_have"
        ]

        core_features = [
            item["feature"]
            for item in must_have
        ]

        optional_features = [
            item["feature"]
            for item in should_have
        ]

        return {
            "core_features": core_features,

            "optional_features": optional_features,

            "feature_count": len(
                core_features
            ),

            "scope_recommendation": (
                "Build only the Must Have features for "
                "the initial MVP. Add Should Have features "
                "after validating the core product."
            )
        }

    # ==========================================================
    # UNIQUE FEATURE 1:
    # RISK-AWARE PRIORITIZATION
    # ==========================================================

    def _identify_risk_critical_features(
        self,
        prioritized
    ):

        risk_critical = []

        for category in prioritized.values():

            for item in category:

                if item.get(
                    "risk_reduction",
                    0
                ) >= 4:

                    risk_critical.append(
                        {
                            "feature": item[
                                "feature"
                            ],

                            "risk_reduction_score":
                                item[
                                    "risk_reduction"
                                ],

                            "reason": (
                                "This feature can significantly "
                                "reduce an identified startup risk."
                            )
                        }
                    )

        return risk_critical

    # ==========================================================
    # UNIQUE FEATURE 2:
    # MVP READINESS SCORE
    # ==========================================================

    def _calculate_readiness(
        self,
        prioritized,
        comparison,
        risk
    ):

        must_count = len(
            prioritized["must_have"]
        )

        should_count = len(
            prioritized["should_have"]
        )

        validation_score = comparison.get(
            "validation_score",
            0
        )

        risk_score = risk.get(
            "overall_risk_score",
            0
        )

        # Start with 100
        readiness = 100

        # Too many Must Have features
        if must_count > 5:
            readiness -= 10

        if must_count > 8:
            readiness -= 15

        # Too many Should Have features
        if should_count > (
            must_count * 2
        ):

            readiness -= 10

        # Low validation confidence
        if validation_score < 40:
            readiness -= 15

        elif validation_score < 60:
            readiness -= 5

        # High startup risk
        if risk_score >= 75:
            readiness -= 10

        elif risk_score >= 50:
            readiness -= 5

        return max(
            0,
            min(100, readiness)
        )

    # ==========================================================
    # BUILD FINAL OUTPUT
    # ==========================================================

    def _build_output(
        self,
        prioritized,
        comparison,
        risk
    ):

        scope = self._generate_scope(
            prioritized
        )

        risk_features = (
            self._identify_risk_critical_features(
                prioritized
            )
        )

        readiness = (
            self._calculate_readiness(
                prioritized,
                comparison,
                risk
            )
        )

        deferred_features = []

        for category in [
            "could_have",
            "wont_have"
        ]:

            for item in prioritized[
                category
            ]:

                deferred_features.append(
                    item["feature"]
                )

        return {
            "agent": "MVP Recommendation Agent",

            "moscow_prioritization": prioritized,

            "core_value_proposition": (
                "Launch the smallest practical product "
                "that solves the primary customer problem "
                "and allows the startup to validate demand."
            ),

            "mvp_scope_recommendation": scope,

            "risk_critical_features": risk_features,

            "deferred_features": deferred_features,

            "mvp_readiness_score": readiness,

            "prioritization_rationale": (
                "Features were prioritized using business "
                "value, user need, competitive value, market "
                "gaps, SWOT insights and risk reduction."
            ),

            "validation_score_used": comparison.get(
                "validation_score",
                0
            ),

            "risk_level_used": risk.get(
                "overall_risk_level",
                "Unknown"
            ),

            "status": self.status,

            "generated_at": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )
        }

    # ==========================================================
    # LLM SUPPORT
    # ==========================================================

    async def _generate_with_llm(
        self,
        candidate_features,
        comparison,
        swot,
        risk
    ):

        if self.llm_client is None:

            raise MVPRecommendationError(
                "LLM client is not available."
            )

        evidence = {
            "candidate_features":
                candidate_features,

            "comparison": comparison,

            "swot": swot,

            "risk": risk
        }

        prompt = f"""
You are an expert startup product strategist.

Create an MVP recommendation using ONLY the supplied
startup validation data.

Do not perform web research.

Use the MoSCoW framework:

Must Have:
Essential for the product to function and validate
the core startup idea.

Should Have:
Important but not essential for the first launch.

Could Have:
Useful future enhancements.

Won't Have:
Features intentionally deferred.

Prioritize features using:

1. Business value
2. User need
3. Competitive value
4. Market gaps
5. SWOT insights
6. Risk reduction
7. MVP simplicity

Features that significantly reduce high-severity risks
should receive higher priority.

Return ONLY valid JSON.

Required structure:

{{
    "core_value_proposition": "...",

    "must_have": [],

    "should_have": [],

    "could_have": [],

    "wont_have": [],

    "mvp_scope_recommendation": "...",

    "deferred_features": [],

    "prioritization_rationale": "...",

    "mvp_readiness_score": 0
}}

Each feature object should contain:

{{
    "feature": "...",
    "business_value": 1,
    "user_need": 1,
    "competitive_value": 1,
    "risk_reduction": 1,
    "rationale": "..."
}}

Scores must be between 1 and 5.
mvp_readiness_score must be between 0 and 100.

INPUT DATA:

{json.dumps(evidence, indent=2, default=str)}
"""

        raw_response = (
            await self.llm_client.generate_response(
                system_prompt=(
                    "You are an expert startup "
                    "product strategist. "
                    "Return ONLY valid JSON."
                ),

                user_prompt=prompt,

                response_format={
                    "type": "json_object"
                }
            )
        )

        return safe_parse_llm_json(
            raw_response
        )

    # ==========================================================
    # MAIN ANALYSIS
    # ==========================================================

    async def analyze(self):

        logger.info(
            "MVP Recommendation Agent started."
        )

        comparison, swot, risk, idea = (
            self._get_inputs()
        )

        # ------------------------------------------------------
        # Extract actual startup features
        # ------------------------------------------------------

        candidate_features = (
            self._extract_features(
                comparison,
                idea
            )
        )

        if not candidate_features:

            logger.warning(
                "No candidate features found."
            )

            return self._return_fallback(
                "No startup features were found."
            )

        # ------------------------------------------------------
        # Deterministic prioritization
        # ------------------------------------------------------

        prioritized = (
            self._prioritize_features(
                candidate_features,
                comparison,
                swot,
                risk
            )
        )

        output = self._build_output(
            prioritized,
            comparison,
            risk
        )

        # ------------------------------------------------------
        # Optional LLM enhancement
        # ------------------------------------------------------

        if self.llm_client is not None:

            try:

                llm_result = (
                    await self._generate_with_llm(
                        candidate_features,
                        comparison,
                        swot,
                        risk
                    )
                )

                if isinstance(
                    llm_result,
                    dict
                ):

                    # Keep deterministic
                    # risk-aware calculations
                    # as the final source for
                    # readiness and scores.

                    output.update(
                        {
                            key: value
                            for key, value
                            in llm_result.items()
                            if key not in [
                                "mvp_readiness_score"
                            ]
                        }
                    )

            except (
                MalformedLLMOutputError,
                MVPRecommendationError,
                Exception
            ) as exc:

                logger.warning(
                    "LLM enhancement failed: %s. "
                    "Using deterministic result.",
                    exc
                )

        # ------------------------------------------------------
        # Store in Shared Context
        # ------------------------------------------------------

        self.context[
            "mvp_analysis"
        ] = output

        logger.info(
            "MVP Recommendation Agent completed."
        )

        return output

    # ==========================================================
    # FALLBACK
    # ==========================================================

    def _return_fallback(
        self,
        reason
    ):

        output = {
            "agent":
                "MVP Recommendation Agent",

            "moscow_prioritization": {
                "must_have": [],
                "should_have": [],
                "could_have": [],
                "wont_have": []
            },

            "core_value_proposition":
                "Unable to determine MVP scope.",

            "mvp_scope_recommendation":
                "Insufficient upstream data.",

            "risk_critical_features": [],

            "deferred_features": [],

            "mvp_readiness_score": 0,

            "prioritization_rationale":
                "MVP recommendation failed.",

            "status": self.status,

            "failure_reason": reason,

            "generated_at":
                datetime.now(
                    timezone.utc
                ).isoformat()
        }

        self.context[
            "mvp_analysis"
        ] = output

        return output


# ==============================================================
# A2A HELPER
# ==============================================================

async def run_mvp_agent(
    shared_context: dict[str, Any],
    llm_client=None
):

    agent = MVPAgent(
        shared_context=shared_context,
        llm_client=llm_client
    )

    return await agent.get_analysis()


# ==============================================================
# LOCAL TEST
# ==============================================================

if __name__ == "__main__":

    async def main():

        context = {

            "idea": {
                "description":
                    "AI startup idea",

                "proposed_features": [
                    "User registration",
                    "AI recommendation system",
                    "Personalized dashboard",
                    "Payment integration",
                    "Admin analytics"
                ]
            },

            "comparison_analysis": {

                "feature_matrix": [
                    {
                        "feature":
                            "User registration",

                        "startup": True,

                        "competitors": []
                    },
                    {
                        "feature":
                            "AI recommendation system",

                        "startup": True,

                        "competitors": [
                            {
                                "name": "Competitor A",
                                "available": False
                            }
                        ]
                    }
                ],

                "competitive_advantages": [
                    "Startup offers features not found in competitors."
                ],

                "market_gaps": [
                    "Affordable personalized solutions"
                ],

                "validation_score": 80,

                "innovation_score": 85,

                "confidence": "High",

                "recommendations": [
                    "Focus on underserved market gaps."
                ],

                "summary":
                    "The startup shows strong potential."
            },

            "swot_analysis": {

                "strengths": [
                    {
                        "point":
                            "Strong AI differentiation"
                    }
                ],

                "weaknesses": [
                    {
                        "point":
                            "Limited resources"
                    }
                ],

                "opportunities": [
                    {
                        "point":
                            "Growing demand"
                    }
                ],

                "threats": [
                    {
                        "point":
                            "Established competitors"
                    }
                ],

                "strategic_summary":
                    "Focus on a small MVP.",

                "priority_action":
                    "Validate customer demand."
            },

            "risk_analysis": {

                "overall_risk_level":
                    "Medium",

                "overall_risk_score":
                    45,

                "risks": [
                    {
                        "category":
                            "Technical",

                        "risk":
                            "AI reliability",

                        "severity":
                            "High",

                        "likelihood":
                            "Medium",

                        "impact":
                            "High",

                        "mitigation":
                            "Validate AI performance."
                    }
                ],

                "top_risks": [
                    "AI reliability"
                ],

                "recommendations": [
                    "Validate AI performance."
                ]
            }
        }

        result = await run_mvp_agent(
            context
        )

        print(
            json.dumps(
                result,
                indent=2,
                default=str
            )
        )

    asyncio.run(main())