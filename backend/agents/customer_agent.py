"""
customer_agent.py
(Customer Agent)

Purpose:
Milestone 2 — Customer Segmentation Agent.
Synthesizes raw search results into structured customer insights 
(personas, pain points, sentiment, feature demand) using LLM inference over raw search data.
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Any

from utils.error_handler import safe_parse_llm_json, MalformedLLMOutputError

logger = logging.getLogger("customer_agent")

class CustomerAnalysisError(Exception):
    """Raised when customer analysis fails."""

class CustomerAgent:
    """
    Analyzes customer segmentation for a startup idea.
    Operates as a decentralized node in the A2A Mesh Network.
    """

    def __init__(self, context, llm_client=None):
        self.context = context
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
        logger.info("CustomerAgent: Awaiting research payload from Web Search Agent.")
        if "web_search" in self.peers:
            research_data = await self.peers["web_search"].get_analysis()
            self.context["research"] = research_data
            logger.info("CustomerAgent: Successfully received research payload.")
            
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
        Main entry point. Uses LLM to parse raw customer snippets.
        Populates and returns shared_context["customer_analysis"].
        """
        logger.info("CustomerAgent: Execution started.")
        
        research = self.context.get("research", {})
        idea = self.context.get("idea", {}).get("description", "Unknown startup idea")
        proposed_features = self.context.get("idea", {}).get("proposed_features", [])

        # Gather relevant snippets (especially target_audience, but fallback to all)
        snippets = []
        for cat in ["target_audience", "market_data", "competitors"]:
            results = research.get(cat, [])
            if isinstance(results, list):
                for r in results:
                    content = r.get("content", "").strip()
                    if content:
                        snippets.append(content)
                        
        if not snippets:
            logger.warning("CustomerAgent: No customer research snippets found. Aborting.")
            return self._return_fallback("Missing customer research data")
            
        logger.info(f"CustomerAgent: Consolidating {len(snippets)} snippets for customer analysis.")

        raw_text = "\n\n".join(snippets)[:3000]

        prompt = (
            f"You are a Customer Insights Analyst. Analyze the following startup idea: '{idea}'.\n"
            f"Proposed Features: {proposed_features}\n"
            f"Using the provided web research snippets, synthesize comprehensive customer insights.\n"
            f"DO NOT use generic placeholders like 'Unknown Persona' or empty values.\n"
            f"Output strictly as a JSON object with exactly these keys:\n"
            f"- 'target_customer_segments' (list of strings, e.g., ['Freelancers', 'Small Businesses'])\n"
            f"- 'customer_personas' (list of objects, each containing: 'name', 'demographics', 'goals', 'pain_points')\n"
            f"- 'pain_points' (list of strings representing the main problems customers face)\n"
            f"- 'unmet_needs' (list of strings representing what customers need but lack)\n"
            f"- 'sentiment' (object containing: 'overall_sentiment' [Positive/Negative/Mixed], 'positive_factors' [list of strings], 'negative_factors' [list of strings])\n"
            f"- 'feature_demand' (list of objects, each containing: 'feature' [string], 'priority' [High/Medium/Low], 'reason' [string])\n"
            f"- 'customer_validation_metrics' (object containing: 'validation_score' [integer 0-100], 'confidence' [High/Medium/Low], 'summary' [string])\n\n"
            f"IMPORTANT: You MUST return ONLY valid JSON. No markdown blocks, no explanatory text. Ensure all brackets are closed.\n"
            f"Research Snippets:\n{raw_text}\n"
        )

        logger.info("CustomerAgent: Requesting LLM extraction for customer insights (personas, sentiment, pain points).")
        
        parsed_analysis = None
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                raw_response = await self.llm_client.generate_response(
                    system_prompt="You are an expert customer insights analyst. Return ONLY valid JSON.",
                    user_prompt=prompt if attempt == 0 else f"{prompt}\n\nWARNING: Your previous response was invalid JSON. Please fix formatting: {last_error}",
                    response_format={"type": "json_object"}
                )
                parsed_analysis = safe_parse_llm_json(raw_response)
                logger.info(f"CustomerAgent: LLM data extraction successful on attempt {attempt + 1}.")
                break
            except MalformedLLMOutputError as e:
                logger.warning(f"CustomerAgent: Malformed JSON output on attempt {attempt + 1}: {e}")
                last_error = str(e)
            except Exception as exc:
                logger.error(f"CustomerAgent: LLM analysis API call failed on attempt {attempt + 1}: {exc}.")
                last_error = str(exc)
                break # Break on network/API errors, only retry on JSON parsing failures

        if not parsed_analysis:
            logger.error(f"CustomerAgent: Failed to generate valid customer JSON after {max_retries} attempts. Using fallback.")
            return self._return_fallback(f"LLM failure or malformed JSON: {last_error}")

        logger.info("CustomerAgent: Validating and structuring response generation.")

        # Ensure all required keys exist and enforce rigid typing
        sentiment_raw = parsed_analysis.get("sentiment") or {}
        validated_sentiment = {
            "overall_sentiment": str(sentiment_raw.get("overall_sentiment") or "Unknown"),
            "positive_factors": self._validate_and_coerce_list(sentiment_raw.get("positive_factors")),
            "negative_factors": self._validate_and_coerce_list(sentiment_raw.get("negative_factors"))
        }
        
        metrics_raw = parsed_analysis.get("customer_validation_metrics") or {}
        
        try:
            val_score = int(metrics_raw.get("validation_score", 0))
        except (ValueError, TypeError):
            val_score = 0
            
        validated_metrics = {
            "validation_score": val_score,
            "confidence": str(metrics_raw.get("confidence") or "Low"),
            "summary": str(metrics_raw.get("summary") or "Customer validation could not be fully assessed.")
        }

        # Type guard lists of objects
        raw_personas = parsed_analysis.get("customer_personas")
        validated_personas = []
        if isinstance(raw_personas, list):
            for p in raw_personas:
                if isinstance(p, dict):
                    name = str(p.get("name") or "").strip()
                    if not name or name.lower() in ["unknown", "unknown persona", "none", "n/a"]:
                        continue
                    validated_personas.append({
                        "name": name,
                        "demographics": str(p.get("demographics") or "Unknown Demographics"),
                        "goals": self._validate_and_coerce_list(p.get("goals")),
                        "pain_points": self._validate_and_coerce_list(p.get("pain_points"))
                    })
                    
        raw_demand = parsed_analysis.get("feature_demand")
        validated_demand = []
        if isinstance(raw_demand, list):
            for f in raw_demand:
                if isinstance(f, dict):
                    feat = str(f.get("feature") or "").strip()
                    if not feat or feat.lower() in ["unknown", "unknown feature", "none", "n/a"]:
                        continue
                    validated_demand.append({
                        "feature": feat,
                        "priority": str(f.get("priority") or "Medium"),
                        "reason": str(f.get("reason") or "No reason provided.")
                    })

        analysis = {
            "target_customer_segments": self._validate_and_coerce_list(parsed_analysis.get("target_customer_segments")),
            "customer_personas": validated_personas,
            "pain_points": self._validate_and_coerce_list(parsed_analysis.get("pain_points")),
            "unmet_needs": self._validate_and_coerce_list(parsed_analysis.get("unmet_needs")),
            "sentiment": validated_sentiment,
            "feature_demand": validated_demand,
            "customer_validation_metrics": validated_metrics,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"--- CUSTOMER AGENT COMPLETE PAYLOAD ---")
        logger.info(json.dumps(analysis, indent=2))
        logger.info("---------------------------------------")

        logger.info("CustomerAgent: Successful completion. Output ready for downstream agents.")
        self.context["customer_analysis"] = analysis
        return analysis

    def _return_fallback(self, reason: str):
        analysis = {
            "target_customer_segments": [],
            "customer_personas": [],
            "pain_points": [],
            "unmet_needs": [],
            "sentiment": {
                "overall_sentiment": "Unknown",
                "positive_factors": [],
                "negative_factors": []
            },
            "feature_demand": [],
            "customer_validation_metrics": {
                "validation_score": 0,
                "confidence": "Low",
                "summary": f"Customer analysis could not be completed. Reason: {reason}"
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        self.context["customer_analysis"] = analysis
        return analysis