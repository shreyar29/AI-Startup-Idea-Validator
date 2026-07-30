"""
competitor_agent.py
(Competitor Agent)

Purpose:
Milestone 2 — Competitor Discovery & Comparison Agent.
Identifies existing competitors, compares their offerings, and highlights
market gaps for the startup idea being validated using LLM inference over raw search data.
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Any

from utils.error_handler import safe_parse_llm_json, MalformedLLMOutputError

logger = logging.getLogger("competitor_agent")

class CompetitorAnalysisError(Exception):
    """Raised when competitor analysis fails."""

class CompetitorAgent:
    """
    Analyzes competitor landscape for a startup idea using research data.
    Operates as a decentralized node in the A2A Mesh Network.
    """

    def __init__(self, shared_context: dict, llm_client=None):
        self.context = shared_context
        self.llm_client = llm_client
        self.peers = {}
        self._analysis_task = None

    def connect_peers(self, peers: dict):
        """Connects this agent to all other agents in the mesh."""
        self.peers = peers

    async def get_analysis(self):
        """
        Mesh Network endpoint. Returns the analysis, computing it
        only once and caching the result as an asyncio Task.
        """
        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(self._perform_analysis())
        return await self._analysis_task

    async def _perform_analysis(self):
        """Pulls required data from peers and runs the analysis."""
        logger.info("CompetitorAgent: Awaiting research payload from Web Search Agent.")
        if "web_search" in self.peers:
            research_data = await self.peers["web_search"].get_analysis()
            self.context["research"] = research_data
            logger.info("CompetitorAgent: Successfully received research payload.")
            
        result = await self.analyze()
        return result

    def _validate_and_coerce_list(self, val: Any) -> list:
        """Helper to ensure a value is strictly a list of strings."""
        if not val:
            return []
        if isinstance(val, list):
            return [str(v) for v in val if v]
        if isinstance(val, str):
            return [val]
        return []

    async def analyze(self):
        """
        Main entry point. Populates and returns shared_context["competitor_analysis"].
        """
        logger.info("CompetitorAgent: Execution started.")
        
        research = self.context.get("research", {})
        idea = self.context.get("idea", {}).get("description", "Unknown startup idea")

        competitor_snippets = []
        # We can extract from both 'competitors' and 'market_data' as competitors are often mentioned broadly
        for cat in ["competitors", "market_data"]:
            results = research.get(cat, [])
            if isinstance(results, list):
                for r in results:
                    content = r.get("content", "").strip()
                    url = r.get("url", "").strip()
                    title = r.get("title", "").strip()
                    
                    # Prevent deduplication flaws by enforcing unique snippet signatures
                    snippet_id = f"{url}-{len(content)}"
                    if content and snippet_id not in competitor_snippets:
                        competitor_snippets.append(f"Source: {url} | Title: {title}\nContent: {content}")

        if not competitor_snippets:
            logger.warning("CompetitorAgent: No competitor research snippets found in Shared Context. Aborting.")
            return self._return_fallback("Missing competitor research data")
            
        logger.info(f"CompetitorAgent: Consolidating {len(competitor_snippets)} snippets to identify real competitors.")

        raw_text = "\n\n".join(competitor_snippets)[:3000]

        prompt = (
            f"You are a Competitive Intelligence Specialist. Analyze the following startup idea: '{idea}'.\n"
            f"Using the provided web research snippets, identify and analyze the actual competitors mentioned.\n"
            f"DO NOT use generic names like 'Unknown Competitor'. Extract the real company/product names.\n"
            f"Output strictly as a valid JSON object containing a single key 'competitors', which is an array of objects.\n"
            f"Each object in the array MUST have exactly these keys:\n"
            f"- 'name' (string, the real name of the competitor)\n"
            f"- 'product_summary' (string)\n"
            f"- 'features' (list of strings)\n"
            f"- 'pricing' (string or null, e.g., '$10/mo', 'Free tier available')\n"
            f"- 'market_positioning' (string)\n"
            f"- 'strengths' (list of strings)\n"
            f"- 'weaknesses' (list of strings)\n"
            f"- 'source_references' (list of strings, exact URLs from the snippets where this competitor was found)\n\n"
            f"IMPORTANT: You MUST return ONLY valid JSON. No markdown blocks, no explanatory text. Ensure all brackets are closed.\n"
            f"Research Snippets:\n{raw_text}\n"
        )

        logger.info("CompetitorAgent: Requesting LLM extraction for competitor profiles.")
        
        parsed_analysis = None
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                raw_response = await self.llm_client.generate_response(
                    system_prompt="You are an expert competitive intelligence specialist. Return ONLY valid JSON.",
                    user_prompt=prompt if attempt == 0 else f"{prompt}\n\nWARNING: Your previous response was invalid JSON. Please fix formatting: {last_error}",
                    response_format={"type": "json_object"}
                )
                parsed_analysis = safe_parse_llm_json(raw_response)
                logger.info(f"CompetitorAgent: LLM data extraction successful on attempt {attempt + 1}.")
                break
            except MalformedLLMOutputError as e:
                logger.warning(f"CompetitorAgent: Malformed JSON output on attempt {attempt + 1}: {e}")
                last_error = str(e)
            except Exception as exc:
                logger.error(f"CompetitorAgent: LLM analysis API call failed on attempt {attempt + 1}: {exc}.")
                last_error = str(exc)
                break # Break on network/API errors, only retry on JSON parsing failures

        if not parsed_analysis:
            logger.error(f"CompetitorAgent: Failed to generate valid competitor JSON after {max_retries} attempts. Using fallback.")
            return self._return_fallback(f"LLM failure or malformed JSON: {last_error}")

        logger.info("CompetitorAgent: Validating and structuring response generation.")

        raw_competitors = parsed_analysis.get("competitors")
        if not isinstance(raw_competitors, list):
            raw_competitors = []

        validated_competitors = []
        seen_names = set()
        
        for comp in raw_competitors:
            if not isinstance(comp, dict):
                continue
            name = str(comp.get("name") or "").strip()
            
            # Eliminate generic/unknown outputs and duplicates
            if not name or name.lower() in ["unknown competitor", "unknown", "n/a", "none"]:
                continue
                
            if name.lower() in seen_names:
                continue
                
            seen_names.add(name.lower())
                
            validated_competitors.append({
                "name": name,
                "product_summary": str(comp.get("product_summary") or "No summary available."),
                "features": self._validate_and_coerce_list(comp.get("features")),
                "pricing": comp.get("pricing") if comp.get("pricing") else "Pricing unavailable",
                "market_positioning": str(comp.get("market_positioning") or "Unknown positioning."),
                "strengths": self._validate_and_coerce_list(comp.get("strengths")),
                "weaknesses": self._validate_and_coerce_list(comp.get("weaknesses")),
                "source_references": self._validate_and_coerce_list(comp.get("source_references"))
            })

        # Rank by relevance (number of features identified could be a proxy for depth of insight)
        validated_competitors.sort(key=lambda x: len(x["features"]), reverse=True)

        gap_analysis = self._generate_gap_analysis(validated_competitors)

        analysis = {
            "competitors": validated_competitors,
            "gap_analysis": gap_analysis,
            "confidence": "high" if validated_competitors else "low",
            "no_competitor_data_found": len(validated_competitors) == 0,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"--- COMPETITOR AGENT COMPLETE PAYLOAD ---")
        logger.info(json.dumps(analysis, indent=2))
        logger.info("-----------------------------------------")

        logger.info("CompetitorAgent: Successful completion. Output ready for downstream agents.")
        self.context["competitor_analysis"] = analysis
        return analysis

    def _generate_gap_analysis(self, competitors: list) -> list:
        """
        Identifies feature gaps — things no competitor currently offers, 
        which is genuinely useful signal for startup idea validation.
        """
        if not competitors:
            return []

        all_features = set()
        for c in competitors:
            for f in c.get("features", []):
                all_features.add(str(f).lower().strip())

        idea_features = set(
            str(f).lower().strip() for f in self.context.get("idea", {}).get("proposed_features", [])
        )
        
        if not idea_features:
            return ["No specific features proposed to compare gaps against."]

        gaps = list(idea_features - all_features)
        return gaps if gaps else ["No distinct feature gaps identified."]

    def _return_fallback(self, reason: str):
        analysis = {
            "competitors": [],
            "gap_analysis": [],
            "confidence": "low",
            "no_competitor_data_found": True,
            "errors": [f"Competitor parsing failed due to {reason}"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.context["competitor_analysis"] = analysis
        return analysis