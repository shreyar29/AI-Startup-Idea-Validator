"""
customer_agent.py
(Customer Agent)

Purpose:
Milestone 2 — Customer Segmentation Agent.
Synthesizes raw search results into structured customer insights 
(personas, pain points, sentiment, feature demand) using deterministic evidence extraction.
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List
from core.config import settings
from datetime import datetime, timezone

logger = logging.getLogger("customer_agent")

class CustomerAnalysisError(Exception):
    """Raised when customer analysis fails."""

class CustomerAgent:
    """
    Analyzes customer segmentation for a startup idea.
    Operates as a decentralized node in the A2A Mesh Network.
    """

    def __init__(self, context: dict):
        self.context = context
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
        Implements proper lifecycle resets on failure/timeout.
        """
        if self._analysis_task is not None:
            if self._analysis_task.done():
                try:
                    self._analysis_task.result()
                    if self.status in ["failed", "timeout"]:
                        logger.warning("CustomerAgent: Previous task completed in degraded state. Resetting task.")
                        self._analysis_task = None
                except Exception as e:
                    logger.warning(f"CustomerAgent: Previous task failed with '{e}'. Resetting task.")
                    self._analysis_task = None

        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(self._perform_analysis())
            
        try:
            return await self._analysis_task
        except asyncio.CancelledError:
            logger.warning("CustomerAgent: Task cancelled. Resetting state.")
            self._analysis_task = None
            self.status = "failed"
            raise
        except Exception:
            raise

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

    def _extract_core_insight(self, sentence: str) -> str:
        bad_phrases = ["survey methodology", "conducted in", "designed around", "according to", "report shows", "research indicates", "study found", "analysis", "data shows"]
        if any(b in sentence.lower() for b in bad_phrases):
            return ""
            
        match = re.search(r'(?:includes|target|for|such as|like|struggle with|want to|need to|require|aimed at|focus on)\s+([^.]+)', sentence, re.IGNORECASE)
        if match:
            res = match.group(1).strip()
            res = re.sub(r'[,;].*', '', res)
            if 3 < len(res) < 50:
                return res.capitalize()
                
        words = sentence.split()
        if len(words) < 10 and len(sentence) > 3:
            return sentence.capitalize()
        return ""

    def _dedupe_list(self, raw_list: list) -> list:
        val_list = self._validate_and_coerce_list(raw_list)
        return list(dict.fromkeys(val_list))

    async def analyze(self):
        """
        Main entry point. Uses LLM to parse raw customer snippets.
        Populates and returns shared_context["customer_analysis"].
        """
        logger.info("CustomerAgent: Execution started.")
        
        research = self.context.get("research") or {}

        max_snippets = settings.agent.CUSTOMER_MAX_SNIPPETS
        max_snippet_length = settings.agent.CUSTOMER_MAX_SNIPPET_LENGTH
        
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
                        snippets.append(content[:max_snippet_length] if max_snippet_length else content)
                        
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
        
        top_snippets = snippets[:max_snippets]

        parsed_analysis = {
            "target_customer_segments": [],
            "pain_points": [],
            "customer_goals": [],
            "buying_behaviour": [],
            "feature_demand": [],
            "customer_journey": []
        }
        
        for s in top_snippets:
            sentences = [sen.strip() for sen in s.split('.') if sen.strip()]
            for sen in sentences:
                sen_lower = sen.lower()
                insight = self._extract_core_insight(sen)
                if not insight: continue
                
                # Target customer segments
                if any(kw in sen_lower for kw in ["target", "audience", "demographic", "users who", "focus on", "user", "customer", "client", "consumer", "buyer"]):
                    if insight not in parsed_analysis["target_customer_segments"]:
                        parsed_analysis["target_customer_segments"].append(insight)
                # Pain points
                if any(kw in sen_lower for kw in ["pain", "struggle", "difficult", "hard to", "challenge", "problem"]):
                    if insight not in parsed_analysis["pain_points"]:
                        parsed_analysis["pain_points"].append(insight)
                # Customer goals
                if any(kw in sen_lower for kw in ["goal", "achieve", "want to", "looking for", "desire"]):
                    if insight not in parsed_analysis["customer_goals"]:
                        parsed_analysis["customer_goals"].append(insight)
                # Buying behavior
                if any(kw in sen_lower for kw in ["buy", "purchase", "spend", "willing to pay", "budget", "cost"]):
                    if insight not in parsed_analysis["buying_behaviour"]:
                        parsed_analysis["buying_behaviour"].append(insight)
                # Feature demand
                if any(kw in sen_lower for kw in ["need", "require", "feature", "must have", "demand"]):
                    parsed_analysis["feature_demand"].append({
                        "feature": insight,
                        "priority": "High" if "must" in sen_lower or "crucial" in sen_lower else "Medium",
                        "reason": sen[:100] + "..." if len(sen) > 100 else sen
                    })
                # Customer journey
                if any(kw in sen_lower for kw in ["journey", "process", "step", "first", "then", "flow"]):
                    if insight not in parsed_analysis["customer_journey"]:
                        parsed_analysis["customer_journey"].append(insight)
                        
        # Cap list sizes
        parsed_analysis["target_customer_segments"] = parsed_analysis["target_customer_segments"][:5]
        parsed_analysis["pain_points"] = parsed_analysis["pain_points"][:5]
        parsed_analysis["customer_goals"] = parsed_analysis["customer_goals"][:5]
        parsed_analysis["buying_behaviour"] = parsed_analysis["buying_behaviour"][:3]
        parsed_analysis["feature_demand"] = parsed_analysis["feature_demand"][:5]
        parsed_analysis["customer_journey"] = parsed_analysis["customer_journey"][:3]
        
        logger.info("CustomerAgent: Extracted customer insights using deterministic python logic.")

        logger.info("CustomerAgent: Validating and structuring response generation.")

        target_customer_segments = self._dedupe_list(parsed_analysis.get("target_customer_segments"))
        pain_points = self._dedupe_list(parsed_analysis.get("pain_points"))
        customer_goals = self._dedupe_list(parsed_analysis.get("customer_goals"))
        buying_behaviour = self._dedupe_list(parsed_analysis.get("buying_behaviour"))
        customer_journey = self._dedupe_list(parsed_analysis.get("customer_journey"))
        
        unmet_needs = []
        validated_sentiment = {
            "overall_sentiment": "Unknown",
            "positive_factors": [],
            "negative_factors": []
        }

        # Map factual outputs into the existing persona schema
        validated_personas = []
        if target_customer_segments or pain_points or customer_goals or buying_behaviour:
            demographics = "25-45"
            occupation = "Professionals"
            location = "Urban/Suburban"
            income = "Middle to High"
            budget = "Flexible"
            decision_drivers = ["Value for money", "Ease of use"]
            
            for seg in target_customer_segments:
                seg_lower = seg.lower()
                if any(x in seg_lower for x in ["student", "teen", "college", "university", "gen z"]): demographics = "18-24"; occupation = "Student"; income = "Low to Middle"; budget = "Price-sensitive"
                elif any(x in seg_lower for x in ["senior", "elderly", "retiree", "boomer"]): demographics = "65+"; occupation = "Retired"; decision_drivers = ["Simplicity", "Reliability"]
                elif any(x in seg_lower for x in ["b2b", "enterprise", "business", "company", "corporate", "agency"]): demographics = "30-55"; occupation = "Business Owner / Executive"; income = "High"; budget = "High / ROI-driven"; decision_drivers = ["Efficiency", "Scalability", "ROI"]
                elif any(x in seg_lower for x in ["mom", "parent", "dad", "family", "children"]): demographics = "30-50"; occupation = "Working Parent"; budget = "Moderate"; decision_drivers = ["Time-saving", "Safety", "Value"]
                elif any(x in seg_lower for x in ["developer", "engineer", "programmer", "it pro"]): occupation = "Software Engineer"; decision_drivers = ["Flexibility", "Performance", "Customization"]
                if "rural" in seg_lower: location = "Rural"
                if "global" in seg_lower or "international" in seg_lower: location = "Global"

            persona_name = target_customer_segments[0].title() if target_customer_segments else "Primary Customer Profile"

            validated_personas.append({
                "name": persona_name,
                "demographics": demographics,
                "occupation": occupation,
                "location": location,
                "income": income,
                "budget": budget,
                "decision_drivers": decision_drivers,
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

        score = 0
        if target_customer_segments: score += 25
        if pain_points: score += 25
        if validated_personas: score += 25
        if validated_demand: score += 25
        
        if score == 100:
            confidence = "High"
            summary = "Strong evidence found for customer segments, pain points, and feature demand."
        elif score >= 50:
            confidence = "Medium"
            summary = "Partial evidence found for target customer profile."
        else:
            confidence = "Low"
            summary = "Insufficient evidence to validate customer segments."

        validated_metrics = {
            "validation_score": score,
            "confidence": confidence,
            "summary": summary
        }

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

        logger.debug(f"--- CUSTOMER AGENT COMPLETE PAYLOAD ---")
        logger.debug(json.dumps(analysis, indent=2))
        logger.debug("---------------------------------------")

        logger.info("CustomerAgent: Successful completion. Output ready for downstream agents.")
        self.context["customer_analysis"] = analysis
        return analysis