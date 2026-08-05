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
from typing import Dict, Any, List
from core.config import settings
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
        self.status = "idle"

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
        self.status = "started"
        try:
            logger.info("CustomerAgent: Awaiting research payload from Web Search Agent.")
            if "web_search" in self.peers:
                research_data = await self.peers["web_search"].get_analysis()
                self.context["research"] = research_data
                logger.info("CustomerAgent: Successfully received research payload.")
                
            result = await self.analyze()
            return result
        except asyncio.TimeoutError:
            self.status = "timeout"
            raise
        except Exception:
            self.status = "failed"
            raise

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
        
        research = self.context.get("research") or {}
        idea_data = self.context.get("idea") or {}
        idea = idea_data.get("description", "Unknown startup idea")
        proposed_features = idea_data.get("proposed_features", [])

        # Gather relevant snippets from categories matching Query Strategist output
        snippets = []
        if "search_results" in research and isinstance(research["search_results"], dict):
            research = research["search_results"]
            
        for cat in ["customers", "market_size", "competitors", "trends", "target_audience", "market_data"]:
            results = research.get(cat, [])
            if isinstance(results, list):
                for r in results:
                    content = str(r.get("content") or "").strip()
                    if content:
                        snippets.append(content)
                        
        if not snippets:
            self.status = "failed"
            logger.warning("CustomerAgent: No research snippets found. Returning degraded output.")
            analysis = {
                "target_customer_segments": [],
                "customer_personas": [],
                "pain_points": [],
                "unmet_needs": [],
                "customer_journey": [],
                "sentiment": {"overall_sentiment": "Unknown", "positive_factors": [], "negative_factors": []},
                "feature_demand": [],
                "customer_validation_metrics": {"validation_score": 0, "confidence": "Low", "summary": "No research data available."},
                "status": self.status,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            self.context["customer_analysis"] = analysis
            return analysis
            
        logger.info(f"CustomerAgent: Consolidating {len(snippets)} snippets for customer analysis.")
        
        max_snippets = settings.agent.CUSTOMER_MAX_SNIPPETS
        max_snippet_length = settings.agent.CUSTOMER_MAX_SNIPPET_LENGTH
        timeout_seconds = settings.agent.CUSTOMER_LLM_TIMEOUT
        
        top_snippets = snippets[:max_snippets]

        def generate_prompt(snippet_list):
            raw_text = "\n\n".join([s[:max_snippet_length] for s in snippet_list])
            p = (
                f"Extract customer facts for startup idea: '{idea}'.\n"
                f"RULES:\n"
                f"1. Extract ONLY: target_customer_segments, pain_points, customer_goals, buying_behaviour, feature_demand, customer_journey.\n"
                f"2. Use ONLY explicit facts from evidence. Do NOT explain or reason.\n"
                f"3. If unavailable, return 'Unknown' or an empty list.\n\n"
                f"Output strictly as a JSON object containing exactly these keys:\n"
                f"- 'target_customer_segments' (list of strings)\n"
                f"- 'pain_points' (list of strings)\n"
                f"- 'customer_goals' (list of strings)\n"
                f"- 'buying_behaviour' (list of strings)\n"
                f"- 'feature_demand' (list of objects: 'feature', 'priority', 'reason')\n"
                f"- 'customer_journey' (list of strings)\n\n"
                f"Evidence:\n{raw_text}\n"
            )
            return p

        prompt = generate_prompt(top_snippets)

        logger.info("CustomerAgent: Requesting LLM extraction for customer insights (personas, sentiment, pain points).")
        
        parsed_analysis = None
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                raw_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        system_prompt="You are a factual data extractor. Return ONLY valid JSON.",
                        user_prompt=prompt if attempt == 0 else f"{prompt}\n\nWARNING: Your previous response was invalid JSON. Please fix formatting: {last_error}",
                        response_format={"type": "json_object"}
                    ),
                    timeout=timeout_seconds
                )
                parsed_analysis = safe_parse_llm_json(raw_response)
                logger.info(f"CustomerAgent: LLM data extraction successful on attempt {attempt + 1}.")
                break
            except asyncio.TimeoutError:
                logger.error(f"CustomerAgent: LLM timeout on attempt {attempt + 1} after {timeout_seconds}s.")
                last_error = "LLM Timeout"
                if attempt == 0 and len(top_snippets) > 2:
                    logger.info("CustomerAgent: Retrying with top 2 snippets to reduce context.")
                    top_snippets = top_snippets[:2]
                    prompt = generate_prompt(top_snippets)
                else:
                    break
            except MalformedLLMOutputError as e:
                logger.warning(f"CustomerAgent: Malformed JSON output on attempt {attempt + 1}: {e}")
                last_error = str(e)
            except Exception as exc:
                logger.error(f"CustomerAgent: LLM analysis API call failed on attempt {attempt + 1}: {exc}.")
                last_error = str(exc)
                break # Break on network/API errors, only retry on JSON parsing failures

        if not parsed_analysis:
            self.status = "timeout" if last_error == "LLM Timeout" else "failed"
            logger.error(f"Customer Segmentation Agent: All retries failed. Last error: {last_error}. Degrading gracefully.")
            parsed_analysis = {
                "customer_validation_metrics": {
                    "validation_score": 0,
                    "confidence": "Low",
                    "summary": f"LLM failure or malformed JSON: {last_error}"
                }
            }

        logger.info("CustomerAgent: Validating and structuring response generation.")

        def dedupe_list(raw_list):
            val_list = self._validate_and_coerce_list(raw_list)
            return list(dict.fromkeys(val_list))

        target_customer_segments = dedupe_list(parsed_analysis.get("target_customer_segments"))
        pain_points = dedupe_list(parsed_analysis.get("pain_points"))
        customer_goals = dedupe_list(parsed_analysis.get("customer_goals"))
        buying_behaviour = dedupe_list(parsed_analysis.get("buying_behaviour"))
        customer_journey = dedupe_list(parsed_analysis.get("customer_journey"))
        
        unmet_needs = []
        validated_sentiment = {
            "overall_sentiment": "Unknown",
            "positive_factors": [],
            "negative_factors": []
        }
        validated_metrics = {
            "validation_score": 0,
            "confidence": "Medium",
            "summary": "Validation delegated to Comparison Agent."
        }

        # Map factual outputs into the existing persona schema
        validated_personas = []
        if target_customer_segments or pain_points or customer_goals or buying_behaviour:
            validated_personas.append({
                "name": "Primary Customer Profile",
                "demographics": "Unknown",
                "occupation": "Unknown",
                "goals": customer_goals,
                "pain_points": pain_points,
                "buying_behaviour": ", ".join(buying_behaviour) if buying_behaviour else "Unknown"
            })
                    
        raw_demand = parsed_analysis.get("feature_demand")
        validated_demand = []
        seen_features = set()
        
        if isinstance(raw_demand, list):
            for f in raw_demand:
                if isinstance(f, dict):
                    feat = str(f.get("feature") or "").strip()
                    if not feat or feat.lower() in ["unknown", "unknown feature", "none", "n/a"] or feat.lower() in seen_features:
                        continue
                    seen_features.add(feat.lower())
                    validated_demand.append({
                        "feature": feat,
                        "priority": str(f.get("priority") or "Medium"),
                        "reason": str(f.get("reason") or "No reason provided.")
                    })

        if self.status not in ["failed", "timeout"]:
            self.status = "success"
            
        analysis = {
            "target_customer_segments": target_customer_segments,
            "customer_personas": validated_personas,
            "pain_points": pain_points,
            "unmet_needs": unmet_needs,
            "customer_journey": customer_journey,
            "sentiment": validated_sentiment,
            "feature_demand": validated_demand,
            "customer_validation_metrics": validated_metrics,
            "status": self.status,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        stats = {
            "segments_discovered": len(target_customer_segments),
            "personas_generated": len(validated_personas),
            "pain_points_extracted": len(pain_points),
            "feature_requests_extracted": len(validated_demand),
            "validation_score": validated_metrics["validation_score"],
            "confidence": validated_metrics["confidence"]
        }
        logger.info(f"CustomerAgent Processing Stats: {stats}")

        logger.info(f"--- CUSTOMER AGENT COMPLETE PAYLOAD ---")
        logger.info(json.dumps(analysis, indent=2))
        logger.info("---------------------------------------")

        logger.info("CustomerAgent: Successful completion. Output ready for downstream agents.")
        self.context["customer_analysis"] = analysis
        return analysis