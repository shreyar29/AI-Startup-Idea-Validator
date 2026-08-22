"""
swot_agent.py

Milestone 3 - SWOT Analysis Agent

Responsibilities
----------------
- Reads Market, Customer and Competitor analysis from Shared Context.
- Does NOT perform independent web searches.
- Derives Strengths, Weaknesses, Opportunities and Threats.
- Writes ONLY to shared_context["swot_analysis"].
- Provides a structured JSON-compatible output.
- Can optionally use an injected LLM client for deeper reasoning.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import logging
import json

logger = logging.getLogger("swot_agent")


class SWOTAnalysisError(Exception):
    """Raised when SWOT analysis cannot be completed."""


class SWOTAgent:
    """
    Milestone 3 SWOT Analysis Agent.

    Reads:
        market_analysis
        customer_analysis
        competitor_analysis

    Writes:
        swot_analysis
    """

    def __init__(
        self,
        shared_context: dict[str, Any],
        llm_client=None,
    ):
        self.context = shared_context
        self.llm_client = llm_client

    async def analyze(self) -> dict[str, Any]:
        """
        Main SWOT Agent entry point.
        """

        logger.info("SWOT Agent started.")

        market = self.context.get("market_analysis", {})
        customer = self.context.get("customer_analysis", {})
        competitor = self.context.get("competitor_analysis", {})
        idea = self.context.get("idea", {})

        if not (market or customer or competitor):
            logger.error("No upstream analysis found.")
            raise SWOTAnalysisError(
                "No Market, Customer or Competitor analysis found "
                "in Shared Context."
            )

        logger.info(
            "Loaded upstream analysis: Market=%s Customer=%s Competitor=%s",
            bool(market),
            bool(customer),
            bool(competitor),
        )

        # ---------------------------------------------------------
        # LLM PATH
        # ---------------------------------------------------------
        if self.llm_client is not None:
            try:
                analysis = await self._generate_with_llm(
                    idea,
                    market,
                    customer,
                    competitor,
                )

                analysis = self._validate_and_normalize(analysis)

                self.context["swot_analysis"] = analysis

                logger.info("SWOT Agent completed using LLM.")
                return analysis

            except Exception as exc:
                logger.warning(
                    "LLM SWOT generation failed: %s. "
                    "Falling back to deterministic analysis.",
                    exc,
                )

        # ---------------------------------------------------------
        # DETERMINISTIC FALLBACK
        # ---------------------------------------------------------
        analysis = self._generate_deterministic_swot(
            idea,
            market,
            customer,
            competitor,
        )

        self.context["swot_analysis"] = analysis

        logger.info("SWOT Agent completed using fallback analysis.")

        return analysis

    # =============================================================
    # LLM ANALYSIS
    # =============================================================

    async def _generate_with_llm(
        self,
        idea: dict[str, Any],
        market: dict[str, Any],
        customer: dict[str, Any],
        competitor: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Supports common async LLM client interfaces.

        The project can inject its existing LLM client without
        requiring the SWOT agent to perform its own research.
        """

        prompt = self._build_prompt(
            idea,
            market,
            customer,
            competitor,
        )

        # Common project-specific wrapper style.
        if hasattr(self.llm_client, "generate"):
            response = self.llm_client.generate(prompt)

            if hasattr(response, "__await__"):
                response = await response

            return self._parse_llm_response(response)

        # OpenAI-compatible async client style.
        if hasattr(self.llm_client, "chat"):
            chat = self.llm_client.chat

            if hasattr(chat, "completions"):
                response = await chat.completions.create(
                    model=getattr(
                        self.llm_client,
                        "model",
                        "gpt-4o-mini",
                    ),
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a startup strategy analyst. "
                                "Return ONLY valid JSON."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=0.2,
                )

                content = response.choices[0].message.content

                return self._parse_llm_response(content)

        raise SWOTAnalysisError(
            "Unsupported LLM client interface."
        )

    def _build_prompt(
        self,
        idea: dict[str, Any],
        market: dict[str, Any],
        customer: dict[str, Any],
        competitor: dict[str, Any],
    ) -> str:
        """
        Creates the structured SWOT reasoning prompt.
        """

        return f"""
Analyze the startup idea using ONLY the supplied evidence.

STARTUP IDEA:
{json.dumps(idea, default=str, indent=2)}

MARKET ANALYSIS:
{json.dumps(market, default=str, indent=2)}

CUSTOMER ANALYSIS:
{json.dumps(customer, default=str, indent=2)}

COMPETITOR ANALYSIS:
{json.dumps(competitor, default=str, indent=2)}

Generate a strategic SWOT analysis.

Requirements:

1. Strengths:
   Internal advantages of the startup.

2. Weaknesses:
   Internal limitations, gaps or disadvantages.

3. Opportunities:
   External market opportunities that the startup can exploit.

4. Threats:
   External factors that could negatively affect the startup.

For every item provide:
- point
- evidence
- reasoning
- confidence

Return ONLY JSON in exactly this structure:

{{
  "strengths": [
    {{
      "point": "...",
      "evidence": "...",
      "reasoning": "...",
      "confidence": 0.0
    }}
  ],
  "weaknesses": [
    {{
      "point": "...",
      "evidence": "...",
      "reasoning": "...",
      "confidence": 0.0
    }}
  ],
  "opportunities": [
    {{
      "point": "...",
      "evidence": "...",
      "reasoning": "...",
      "confidence": 0.0
    }}
  ],
  "threats": [
    {{
      "point": "...",
      "evidence": "...",
      "reasoning": "...",
      "confidence": 0.0
    }}
  ],
  "strategic_summary": "...",
  "priority_action": "..."
}}
"""

    # =============================================================
    # RESPONSE PARSING
    # =============================================================

    def _parse_llm_response(self, response: Any) -> dict[str, Any]:
        """
        Converts common LLM response formats into a dictionary.
        """

        if isinstance(response, dict):
            return response

        if hasattr(response, "text"):
            response = response.text

        if not isinstance(response, str):
            raise SWOTAnalysisError(
                "LLM returned an unsupported response format."
            )

        text = response.strip()

        # Remove markdown JSON fences if present.
        if text.startswith("```"):
            text = text.replace("```json", "", 1)
            text = text.replace("```", "")
            text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise SWOTAnalysisError(
                "LLM returned invalid JSON."
            ) from exc

    # =============================================================
    # VALIDATION
    # =============================================================

    def _validate_and_normalize(
        self,
        analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ensures the SWOT response always has the agreed structure.
        """

        categories = [
            "strengths",
            "weaknesses",
            "opportunities",
            "threats",
        ]

        for category in categories:
            if category not in analysis:
                analysis[category] = []

            if not isinstance(analysis[category], list):
                analysis[category] = []

            normalized_items = []

            for item in analysis[category]:
                if isinstance(item, str):
                    item = {
                        "point": item,
                        "evidence": "",
                        "reasoning": "",
                        "confidence": 0.5,
                    }

                if not isinstance(item, dict):
                    continue

                confidence = item.get("confidence", 0.5)

                try:
                    confidence = float(confidence)
                except (TypeError, ValueError):
                    confidence = 0.5

                confidence = max(
                    0.0,
                    min(1.0, confidence),
                )

                normalized_items.append(
                    {
                        "point": str(
                            item.get("point", "")
                        ),
                        "evidence": str(
                            item.get("evidence", "")
                        ),
                        "reasoning": str(
                            item.get("reasoning", "")
                        ),
                        "confidence": confidence,
                    }
                )

            analysis[category] = normalized_items

        analysis.setdefault(
            "strategic_summary",
            self._create_summary(analysis),
        )

        analysis.setdefault(
            "priority_action",
            self._create_priority_action(analysis),
        )

        analysis["generated_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        return analysis

    # =============================================================
    # DETERMINISTIC FALLBACK
    # =============================================================

    def _generate_deterministic_swot(
        self,
        idea: dict[str, Any],
        market: dict[str, Any],
        customer: dict[str, Any],
        competitor: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Produces a useful SWOT even when an LLM is unavailable.

        This guarantees the agent can still execute and return
        structured output.
        """

        strengths = []
        weaknesses = []
        opportunities = []
        threats = []

        # ---------------------------------------------------------
        # Strengths
        # ---------------------------------------------------------

        advantages = self._extract_values(
            competitor,
            [
                "competitive_advantages",
                "advantages",
                "differentiators",
                "unique_features",
            ],
        )

        for value in advantages[:5]:
            strengths.append(
                self._item(
                    str(value),
                    "Competitor analysis",
                    "The analysis identifies a potential "
                    "differentiating advantage.",
                )
            )

        customer_needs = self._extract_values(
            customer,
            [
                "pain_points",
                "needs",
                "customer_needs",
                "unmet_needs",
            ],
        )

        if customer_needs:
            strengths.append(
                self._item(
                    "Alignment with identified customer needs",
                    "Customer analysis contains identified "
                    "pain points or needs.",
                    "The startup can potentially address "
                    "validated customer problems.",
                )
            )

        # ---------------------------------------------------------
        # Weaknesses
        # ---------------------------------------------------------

        gaps = self._extract_values(
            competitor,
            [
                "market_gaps",
                "feature_gaps",
                "gaps",
                "limitations",
            ],
        )

        for value in gaps[:5]:
            weaknesses.append(
                self._item(
                    str(value),
                    "Competitor or market analysis",
                    "The identified gap may indicate an "
                    "execution or differentiation challenge.",
                )
            )

        market_challenges = self._extract_values(
            market,
            [
                "challenges",
                "barriers",
                "constraints",
                "risks",
            ],
        )

        for value in market_challenges[:3]:
            weaknesses.append(
                self._item(
                    str(value),
                    "Market analysis",
                    "The factor may limit early startup execution.",
                )
            )

        # ---------------------------------------------------------
        # Opportunities
        # ---------------------------------------------------------

        trends = self._extract_values(
            market,
            [
                "trends",
                "market_trends",
                "growth_trends",
                "opportunities",
            ],
        )

        for value in trends[:5]:
            opportunities.append(
                self._item(
                    str(value),
                    "Market analysis",
                    "A relevant market trend may create "
                    "an opportunity for the startup.",
                )
            )

        market_gaps = self._extract_values(
            market,
            [
                "market_gaps",
                "unmet_needs",
                "gaps",
            ],
        )

        for value in market_gaps[:5]:
            opportunities.append(
                self._item(
                    str(value),
                    "Market analysis",
                    "An unmet market need can provide "
                    "an opportunity for entry.",
                )
            )

        # ---------------------------------------------------------
        # Threats
        # ---------------------------------------------------------

        competitors = self._extract_values(
            competitor,
            [
                "competitors",
                "competitive_threats",
                "threats",
            ],
        )

        if competitors:
            threats.append(
                self._item(
                    "Established or emerging competitors",
                    "Competitor analysis identifies existing "
                    "players in the market.",
                    "Competitors can reduce market share and "
                    "increase customer acquisition difficulty.",
                )
            )

        competitor_threats = self._extract_values(
            competitor,
            [
                "threats",
                "competitive_risks",
                "risks",
            ],
        )

        for value in competitor_threats[:5]:
            threats.append(
                self._item(
                    str(value),
                    "Competitor analysis",
                    "The identified factor could negatively "
                    "affect competitive positioning.",
                )
            )

        market_risks = self._extract_values(
            market,
            [
                "risks",
                "market_risks",
                "barriers",
            ],
        )

        for value in market_risks[:5]:
            threats.append(
                self._item(
                    str(value),
                    "Market analysis",
                    "The factor represents an external "
                    "market threat.",
                )
            )

        # Guarantee at least one item in every category.
        if not strengths:
            strengths.append(
                self._item(
                    "Potential alignment with the identified "
                    "startup opportunity",
                    "Available upstream analysis",
                    "The startup has an opportunity to leverage "
                    "the findings from the existing analysis.",
                )
            )

        if not weaknesses:
            weaknesses.append(
                self._item(
                    "Limited evidence available for some internal "
                    "capabilities",
                    "Available upstream analysis",
                    "Insufficient evidence can make early "
                    "strategic decisions uncertain.",
                )
            )

        if not opportunities:
            opportunities.append(
                self._item(
                    "Potential market entry opportunity",
                    "Market analysis",
                    "The identified market can provide room "
                    "for a differentiated solution.",
                )
            )

        if not threats:
            threats.append(
                self._item(
                    "Competitive and market uncertainty",
                    "Market and competitor analysis",
                    "External market conditions may affect "
                    "startup growth.",
                )
            )

        result = {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats,
        }

        result["strategic_summary"] = self._create_summary(result)
        result["priority_action"] = self._create_priority_action(result)
        result["generated_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        return result

    # =============================================================
    # HELPERS
    # =============================================================

    @staticmethod
    def _item(
        point: str,
        evidence: str,
        reasoning: str,
        confidence: float = 0.75,
    ) -> dict[str, Any]:

        return {
            "point": point,
            "evidence": evidence,
            "reasoning": reasoning,
            "confidence": confidence,
        }

    @staticmethod
    def _extract_values(
        data: Any,
        keys: list[str],
    ) -> list[Any]:
        """
        Recursively extracts useful values from common analysis
        structures.
        """

        if not isinstance(data, dict):
            return []

        values = []

        for key in keys:
            value = data.get(key)

            if isinstance(value, list):
                values.extend(value)

            elif isinstance(value, str):
                values.append(value)

            elif isinstance(value, dict):
                for nested_value in value.values():
                    if isinstance(nested_value, list):
                        values.extend(nested_value)
                    elif isinstance(nested_value, str):
                        values.append(nested_value)

        # Convert dictionaries into readable strings.
        cleaned = []

        for value in values:
            if isinstance(value, dict):
                if "name" in value:
                    cleaned.append(value["name"])
                elif "point" in value:
                    cleaned.append(value["point"])
                elif "description" in value:
                    cleaned.append(value["description"])
                else:
                    cleaned.append(
                        json.dumps(value, default=str)
                    )
            else:
                cleaned.append(value)

        return cleaned

    @staticmethod
    def _create_summary(
        analysis: dict[str, Any],
    ) -> str:

        strength_count = len(
            analysis.get("strengths", [])
        )
        weakness_count = len(
            analysis.get("weaknesses", [])
        )
        opportunity_count = len(
            analysis.get("opportunities", [])
        )
        threat_count = len(
            analysis.get("threats", [])
        )

        return (
            f"The SWOT analysis identifies {strength_count} "
            f"strength(s), {weakness_count} weakness(es), "
            f"{opportunity_count} opportunit"
            f"{'y' if opportunity_count == 1 else 'ies'}, "
            f"and {threat_count} threat(s) based on the "
            f"available Market, Customer and Competitor evidence."
        )

    @staticmethod
    def _create_priority_action(
        analysis: dict[str, Any],
    ) -> str:

        opportunities = analysis.get(
            "opportunities",
            [],
        )

        threats = analysis.get(
            "threats",
            [],
        )

        if opportunities and threats:
            return (
                "Prioritize the strongest validated market "
                "opportunity while addressing the highest-risk "
                "competitive or market threat."
            )

        return (
            "Validate the highest-impact SWOT findings with "
            "additional customer and market evidence before "
            "major investment."
        )


# =============================================================
# A2A-COMPATIBLE HELPER
# =============================================================

async def run_swot_agent(
    shared_context: dict[str, Any],
    llm_client=None,
) -> dict[str, Any]:
    """
    Convenience entry point for the orchestrator/A2A layer.
    """

    agent = SWOTAgent(
        shared_context=shared_context,
        llm_client=llm_client,
    )

    return await agent.analyze()


# =============================================================
# LOCAL SMOKE TEST
# =============================================================

if __name__ == "__main__":
    import asyncio

    demo_context = {
        "idea": {
            "name": "Demo Startup",
            "description": "An AI-powered startup solution.",
        },
        "market_analysis": {
            "trends": [
                "Growing adoption of AI solutions",
                "Increasing demand for automation",
            ],
            "market_gaps": [
                "Limited affordable solutions",
            ],
        },
        "customer_analysis": {
            "pain_points": [
                "High manual effort",
                "Limited access to affordable tools",
            ],
            "needs": [
                "Automation",
                "Easy-to-use product",
            ],
        },
        "competitor_analysis": {
            "competitors": [
                {"name": "Competitor A"},
                {"name": "Competitor B"},
            ],
            "feature_gaps": [
                "Limited personalization",
            ],
            "competitive_advantages": [
                "Potential AI-based differentiation",
            ],
        },
    }

    async def main():
        result = await run_swot_agent(demo_context)

        print(
            json.dumps(
                result,
                indent=2,
                default=str,
            )
        )

        print("\nShared Context:")
        print(
            json.dumps(
                demo_context,
                indent=2,
                default=str,
            )
        )

    asyncio.run(main())