"""
competitor_agent.py
(Competitor Agent)

Purpose:
Milestone 2 — Competitor Discovery & Comparison Agent.
Identifies existing competitors, compares their offerings, and highlights
market gaps for the startup idea being validated.

Architecture (per team-beta finalized design):
    - Reads from Shared Context first (idea, research sections already
      populated by Orchestrator / Web Search Agent from Milestone 1).
    - Only invokes another agent's exposed tool (A2A) if something needed
      isn't already available in Shared Context.
    - Never performs its own web search — only the Web Search Agent talks
      to Tavily/OpenRouter.
    - Writes ONLY to its own section: shared_context["competitor_analysis"].

Shared Context Schema (agreed):
    {
        "idea": {},
        "research": {},
        "market_analysis": {},
        "customer_analysis": {},
        "competitor_analysis": {},   <- this agent owns this section
        "comparison_analysis": {}
    }

Exposed A2A tools (per Abhipsha's interface spec + innovative additions):
    - get_competitor_summary()
    - get_competitor_features()
    - get_competitor_pricing_comparison()   [added value]
    - get_market_positioning_map()          [added value]
    - get_competitive_gap_analysis()        [added value]

This module reuses the edge-case mitigations from Milestone 1's
error_handler.py (retry, dedupe, staleness/trust checks, conflicting-data
detection) so competitor analysis degrades gracefully rather than
crashing or silently returning bad data.
"""

import logging
from datetime import datetime, timezone

from backend.utils.error_handler import (
    with_retry,
    safe_execute,
    dedupe_results,
    is_stale,
    is_trusted_source,
    detect_conflicting_data,
    LLMCallError,
    MalformedLLMOutputError,
    safe_parse_llm_json,
)

logger = logging.getLogger("competitor_agent")


class CompetitorAgent:
    """
    Analyzes competitor landscape for a startup idea using research data
    already gathered in Shared Context (no independent web search).
    """

    def __init__(self, shared_context, llm_client=None):
        """
        shared_context: dict conforming to the agreed Shared Context Schema.
        llm_client: optional LLM client (OpenRouter) used for summarizing
                    raw research into structured competitor insights.
        """
        self.context = shared_context
        self.llm_client = llm_client

    # ------------------------------------------------------------------
    # Internal helpers — read-first-from-context pattern
    # ------------------------------------------------------------------

    def _get_research_data(self):
        """
        Reads competitor-relevant research from Shared Context. Falls back
        to requesting it via A2A from the Web Search Agent only if the
        research section is missing or empty (per mesh architecture rule:
        "read from Shared Context first, invoke another agent only if not
        available").
        """
        research = self.context.get("research", {})
        competitor_raw = research.get("competitors", [])

        if not competitor_raw:
            logger.info(
                "No competitor research found in Shared Context. "
                "This should be populated by the Web Search Agent; "
                "returning empty result rather than performing an "
                "independent search."
            )
            return []

        return competitor_raw

    def _filter_and_rank_sources(self, raw_results):
        """
        Applies Milestone 1 data-quality mitigations before analysis:
        dedupe, staleness check, trust weighting.
        """
        deduped = dedupe_results(raw_results, key="url")

        ranked = []
        for result in deduped:
            result["is_stale"] = is_stale(result.get("published_date"))
            result["is_trusted"] = is_trusted_source(result.get("url"))
            ranked.append(result)

        # Trusted + fresh sources first
        ranked.sort(key=lambda r: (not r["is_trusted"], r["is_stale"]))
        return ranked

    @with_retry(retry_on=(LLMCallError,))
    def _summarize_with_llm(self, competitor_name, source_snippets):
        """
        Uses the LLM to turn raw source snippets into a structured
        competitor profile. Wrapped with retry (Milestone 1 pattern) and
        defensive JSON parsing to handle malformed LLM output.
        """
        if not self.llm_client:
            # Fallback: no LLM configured, return a basic structural stub
            return {
                "name": competitor_name,
                "summary": "Summary unavailable (no LLM client configured).",
                "features": [],
                "pricing": None,
            }

        prompt = (
            f"Summarize the following information about the competitor "
            f"'{competitor_name}' into strict JSON with keys: "
            f"name, summary, features (array of strings), pricing "
            f"(string or null). Do not include any text outside the JSON.\n\n"
            f"Source snippets:\n{source_snippets}"
        )

        try:
            raw_response = self.llm_client.complete(prompt)
        except Exception as exc:
            raise LLMCallError(f"LLM summarization call failed: {exc}")

        try:
            parsed = safe_parse_llm_json(
                raw_response, required_keys=["name", "summary", "features"]
            )
        except MalformedLLMOutputError as exc:
            logger.warning("Malformed LLM output for %s: %s", competitor_name, exc)
            # Degrade gracefully rather than crash the agent
            parsed = {
                "name": competitor_name,
                "summary": "Summary could not be generated (malformed LLM output).",
                "features": [],
                "pricing": None,
            }

        return parsed

    # ------------------------------------------------------------------
    # Core analysis
    # ------------------------------------------------------------------

    def analyze(self):
        """
        Main entry point. Populates and returns
        shared_context["competitor_analysis"].
        """
        raw_results, errors = safe_execute(self._get_research_data)
        raw_results = raw_results or []

        if not raw_results:
            analysis = {
                "competitors": [],
                "gap_analysis": [],
                "confidence": "low",
                "no_competitor_data_found": True,
                "errors": errors,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            self.context["competitor_analysis"] = analysis
            return analysis

        ranked_sources = self._filter_and_rank_sources(raw_results)

        # Group sources by competitor name (simple heuristic; the Web
        # Search Agent's structured output should already carry this,
        # but we guard against missing/inconsistent tagging here).
        grouped = {}
        for source in ranked_sources:
            name = source.get("competitor_name", "Unknown Competitor")
            grouped.setdefault(name, []).append(source)

        competitors = []
        conflicting_flags = []

        for name, sources in grouped.items():
            snippets = "\n".join(s.get("summary", "") for s in sources)
            profile, summarize_errors = safe_execute(
                self._summarize_with_llm, name, snippets, fallback_errors=[]
            )
            if summarize_errors:
                errors.extend(summarize_errors)
            if profile is None:
                continue

            # Check for conflicting pricing/claims across sources for
            # the same competitor (Milestone 1 pattern reused).
            pricing_points = [
                {"source": s.get("url"), "value": s.get("pricing")}
                for s in sources
                if s.get("pricing") is not None
            ]
            has_conflict, conflicting_values = detect_conflicting_data(
                pricing_points, field="value"
            )
            if has_conflict:
                conflicting_flags.append(
                    {"competitor": name, "conflicting_pricing": conflicting_values}
                )

            profile["sources"] = [s.get("url") for s in sources]
            profile["stale"] = any(s.get("is_stale") for s in sources)
            competitors.append(profile)

        gap_analysis = self._generate_gap_analysis(competitors)

        analysis = {
            "competitors": competitors,
            "gap_analysis": gap_analysis,
            "confidence": "high" if competitors else "low",
            "no_competitor_data_found": len(competitors) == 0,
            "conflicting_data": bool(conflicting_flags),
            "conflicting_data_details": conflicting_flags,
            "errors": errors,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        self.context["competitor_analysis"] = analysis
        return analysis

    def _generate_gap_analysis(self, competitors):
        """
        Innovative addition: identifies feature gaps — things no
        competitor currently offers, which is genuinely useful signal
        for startup idea validation.
        """
        if not competitors:
            return []

        all_features = set()
        for c in competitors:
            all_features.update(f.lower() for f in c.get("features", []))

        idea_features = set(
            f.lower() for f in self.context.get("idea", {}).get("proposed_features", [])
        )

        gaps = list(idea_features - all_features)
        return gaps

    # ------------------------------------------------------------------
    # Exposed A2A tools (per Abhipsha's interface spec)
    # ------------------------------------------------------------------

    def get_competitor_summary(self):
        """A2A tool: returns high-level competitor list + summaries."""
        analysis = self.context.get("competitor_analysis") or self.analyze()
        return [
            {"name": c["name"], "summary": c["summary"]}
            for c in analysis.get("competitors", [])
        ]

    def get_competitor_features(self):
        """A2A tool: returns feature lists per competitor."""
        analysis = self.context.get("competitor_analysis") or self.analyze()
        return {c["name"]: c.get("features", []) for c in analysis.get("competitors", [])}

    def get_competitor_pricing_comparison(self):
        """A2A tool (added value): returns pricing side-by-side, flags conflicts."""
        analysis = self.context.get("competitor_analysis") or self.analyze()
        return {
            "pricing": {
                c["name"]: c.get("pricing") for c in analysis.get("competitors", [])
            },
            "conflicting_data": analysis.get("conflicting_data", False),
            "conflicting_data_details": analysis.get("conflicting_data_details", []),
        }

    def get_market_positioning_map(self):
        """
        A2A tool (added value): categorizes competitors as direct,
        indirect, or adjacent based on feature overlap with the idea.
        """
        analysis = self.context.get("competitor_analysis") or self.analyze()
        idea_features = set(
            f.lower()
            for f in self.context.get("idea", {}).get("proposed_features", [])
        )

        positioning = {"direct": [], "indirect": [], "adjacent": []}
        for c in analysis.get("competitors", []):
            comp_features = set(f.lower() for f in c.get("features", []))
            if not idea_features:
                positioning["adjacent"].append(c["name"])
                continue
            overlap_ratio = len(comp_features & idea_features) / len(idea_features)
            if overlap_ratio >= 0.6:
                positioning["direct"].append(c["name"])
            elif overlap_ratio >= 0.25:
                positioning["indirect"].append(c["name"])
            else:
                positioning["adjacent"].append(c["name"])

        return positioning

    def get_competitive_gap_analysis(self):
        """A2A tool (added value): features the idea proposes that no competitor offers."""
        analysis = self.context.get("competitor_analysis") or self.analyze()
        return {
            "gaps": analysis.get("gap_analysis", []),
            "confidence": analysis.get("confidence", "low"),
        }