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

    async def analyze(self):
        """
        Main entry point. Uses Python deterministic logic to parse raw customer snippets.
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
                    url = str(r.get("url") or "").strip()
                    if content and url:
                        snippets.append({
                            "content": content[:max_snippet_length] if max_snippet_length else content,
                            "url": url,
                            "relevance": r.get("relevance_score", 0)
                        })
                        
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
        
        # Sort by relevance to ensure we process best snippets first
        snippets.sort(key=lambda x: x["relevance"], reverse=True)
        top_snippets = snippets[:max_snippets]

        # Use dictionaries to aggregate evidence and mention counts
        parsed_analysis = {
            "target_customer_segments": {},
            "pain_points": {},
            "customer_goals": {},
            "buying_behaviour": {},
            "feature_demand": {},
            "customer_journey": {},
            "unmet_needs": {},
            "positive_factors": {},
            "negative_factors": {}
        }
        
        pos_count = 0
        neg_count = 0
        
        for s in top_snippets:
            url = s["url"]
            sentences = [sen.strip() for sen in s["content"].split('.') if sen.strip()]
            for sen in sentences:
                sen_lower = sen.lower()
                insight = self._extract_core_insight(sen)
                if not insight: continue
                
                def add_insight(category, text, url):
                    text = text.capitalize()
                    if text not in parsed_analysis[category]:
                        parsed_analysis[category][text] = set()
                    parsed_analysis[category][text].add(url)

                # Target customer segments
                if any(kw in sen_lower for kw in ["target", "audience", "demographic", "users who", "focus on", "user", "customer", "client", "consumer", "buyer"]):
                    add_insight("target_customer_segments", insight, url)
                
                # Pain points
                if any(kw in sen_lower for kw in ["pain", "struggle", "difficult", "hard to", "challenge", "problem"]):
                    add_insight("pain_points", insight, url)
                    
                # Unmet needs (Gap analysis)
                if any(kw in sen_lower for kw in ["lack of", "no solution", "missing", "wish there was", "unmet", "gap", "shortcoming"]):
                    add_insight("unmet_needs", insight, url)

                # Customer goals
                if any(kw in sen_lower for kw in ["goal", "achieve", "want to", "looking for", "desire"]):
                    add_insight("customer_goals", insight, url)
                    
                # Buying behavior
                if any(kw in sen_lower for kw in ["buy", "purchase", "spend", "willing to pay", "budget", "cost"]):
                    add_insight("buying_behaviour", insight, url)
                    
                # Feature demand
                if any(kw in sen_lower for kw in ["need", "require", "feature", "must have", "demand"]):
                    priority = "High" if "must" in sen_lower or "crucial" in sen_lower else "Medium"
                    key = f"{insight} [Priority: {priority}]"
                    add_insight("feature_demand", key, url)
                    
                # Customer journey
                if any(kw in sen_lower for kw in ["journey", "process", "step", "first", "then", "flow", "onboarding", "experience"]):
                    add_insight("customer_journey", insight, url)
                    
                # Sentiment extraction
                if any(kw in sen_lower for kw in ["love", "great", "excellent", "enjoy", "appreciate", "helpful", "good"]):
                    pos_count += 1
                    add_insight("positive_factors", insight, url)
                if any(kw in sen_lower for kw in ["hate", "bad", "terrible", "frustrating", "annoying", "poor", "difficult", "struggle"]):
                    neg_count += 1
                    add_insight("negative_factors", insight, url)
                        
        # Helper to convert dict sets to sorted lists of dicts (for evidence quality)
        def format_insights(category_dict, limit=5):
            items = [{"insight": k, "mentions": len(v), "evidence": list(v)} for k, v in category_dict.items()]
            items.sort(key=lambda x: x["mentions"], reverse=True)
            return items[:limit]
            
        target_customer_segments = format_insights(parsed_analysis["target_customer_segments"], 5)
        pain_points = format_insights(parsed_analysis["pain_points"], 5)
        unmet_needs = format_insights(parsed_analysis["unmet_needs"], 5)
        customer_goals = format_insights(parsed_analysis["customer_goals"], 5)
        buying_behaviour = format_insights(parsed_analysis["buying_behaviour"], 3)
        customer_journey = format_insights(parsed_analysis["customer_journey"], 5)
        
        feature_demand = []
        for feat in format_insights(parsed_analysis["feature_demand"], 5):
            insight_text = feat["insight"]
            priority = "High" if "High" in insight_text else "Medium"
            clean_feat = insight_text.split(" [Priority:")[0]
            feature_demand.append({
                "feature": clean_feat,
                "priority": priority,
                "mentions": feat["mentions"],
                "source_agreement": feat["mentions"] > 1,
                "evidence": feat["evidence"]
            })
            
        # Overall Sentiment calculation
        overall_sentiment = "Neutral"
        if pos_count > neg_count + 2: overall_sentiment = "Positive"
        elif neg_count > pos_count + 2: overall_sentiment = "Negative"
        elif pos_count > 0 or neg_count > 0: overall_sentiment = "Mixed"
        
        validated_sentiment = {
            "overall_sentiment": overall_sentiment,
            "positive_factors": format_insights(parsed_analysis["positive_factors"], 3),
            "negative_factors": format_insights(parsed_analysis["negative_factors"], 3)
        }

        # Map factual outputs into the persona schema, flagging inferred vs evidence-based fields
        validated_personas = []
        if target_customer_segments or pain_points or customer_goals or buying_behaviour:
            # Default inferred fields
            demographics = "25-45"
            occupation = "Professionals"
            location = "Urban/Suburban"
            income = "Middle to High"
            budget = "Flexible"
            decision_drivers = ["Value for money", "Ease of use"]
            
            # Combine all text for inference
            all_text = " ".join([s["insight"].lower() for s in target_customer_segments + pain_points])
            
            if any(x in all_text for x in ["student", "teen", "college", "university", "gen z"]): demographics = "18-24"; occupation = "Student"; income = "Low to Middle"; budget = "Price-sensitive"
            elif any(x in all_text for x in ["senior", "elderly", "retiree", "boomer"]): demographics = "65+"; occupation = "Retired"; decision_drivers = ["Simplicity", "Reliability"]
            elif any(x in all_text for x in ["b2b", "enterprise", "business", "company", "corporate", "agency"]): demographics = "30-55"; occupation = "Business Owner / Executive"; income = "High"; budget = "High / ROI-driven"; decision_drivers = ["Efficiency", "Scalability", "ROI"]
            elif any(x in all_text for x in ["mom", "parent", "dad", "family", "children"]): demographics = "30-50"; occupation = "Working Parent"; budget = "Moderate"; decision_drivers = ["Time-saving", "Safety", "Value"]
            elif any(x in all_text for x in ["developer", "engineer", "programmer", "it pro"]): occupation = "Software Engineer"; decision_drivers = ["Flexibility", "Performance", "Customization"]
            if "rural" in all_text: location = "Rural"
            if "global" in all_text or "international" in all_text: location = "Global"

            persona_name = target_customer_segments[0]["insight"].title() if target_customer_segments else "Primary Customer Profile"

            validated_personas.append({
                "name": persona_name,
                "inferred_attributes": {
                    "demographics": demographics,
                    "occupation": occupation,
                    "location": location,
                    "income": income,
                    "budget": budget,
                    "decision_drivers": decision_drivers
                },
                "evidence_based_attributes": {
                    "goals": [g["insight"] for g in customer_goals],
                    "pain_points": [p["insight"] for p in pain_points],
                    "buying_behaviour": [b["insight"] for b in buying_behaviour]
                },
                "evidence_references": list(set(
                    [url for seg in target_customer_segments for url in seg["evidence"]]
                ))
            })

        # Calculate Evidence-Quality Score
        total_evidence_urls = len(set(
            url for item_list in [target_customer_segments, pain_points, unmet_needs, feature_demand] 
            for item in item_list for url in item["evidence"]
        ))
        
        score = 0
        if target_customer_segments: score += 20
        if pain_points: score += 20
        if unmet_needs: score += 20
        if feature_demand: score += 20
        
        # Add points for evidence volume
        if total_evidence_urls >= 5: score += 20
        elif total_evidence_urls >= 2: score += 10
        
        score = min(100, score)
        
        if score >= 80:
            confidence = "High"
            summary = f"Strong evidence found across {total_evidence_urls} sources validating segments, pain points, and unmet needs."
        elif score >= 40:
            confidence = "Medium"
            summary = f"Partial evidence found across {total_evidence_urls} sources for target customer profile."
        else:
            confidence = "Low"
            summary = "Insufficient evidence to validate customer segments."

        validated_metrics = {
            "validation_score": score,
            "confidence": confidence,
            "total_unique_sources": total_evidence_urls,
            "summary": summary
        }

        if self.status not in ["failed", "timeout"]:
            self.status = "success"
            
        # Calculate willingness to pay heuristic
        willingness_to_pay = {"low": "$0", "expected": "$10/mo", "premium": "$50/mo"}
        all_text = " ".join([s["insight"].lower() for s in target_customer_segments + pain_points])
        
        if "enterprise" in all_text or "b2b" in all_text or "business" in all_text:
            willingness_to_pay = {"low": "$99/mo", "expected": "$499/mo", "premium": "$2000+/mo"}
        elif "student" in all_text or "teen" in all_text:
            willingness_to_pay = {"low": "$0 (Ad-supported)", "expected": "$4.99/mo", "premium": "$12.99/mo"}
        elif "developer" in all_text or "engineer" in all_text:
            willingness_to_pay = {"low": "$0 (Open Source)", "expected": "$20/mo", "premium": "$99/mo"}

        analysis = {
            "target_customer_segments": target_customer_segments,
            "customer_personas": validated_personas,
            "pain_points": pain_points,
            "unmet_needs": unmet_needs,
            "customer_journey": customer_journey,
            "sentiment": validated_sentiment,
            "feature_demand": feature_demand,
            "willingness_to_pay": willingness_to_pay,
            "customer_validation_metrics": validated_metrics,
            "status": self.status,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        stats = {
            "segments_discovered": len(target_customer_segments),
            "personas_generated": len(validated_personas),
            "pain_points_extracted": len(pain_points),
            "unmet_needs_extracted": len(unmet_needs),
            "feature_requests_extracted": len(feature_demand),
            "validation_score": validated_metrics["validation_score"],
            "confidence": validated_metrics["confidence"]
        }
        logger.info(f"CustomerAgent Processing Stats: {stats}")

        logger.info("CustomerAgent: Successful completion. Output ready for downstream agents.")
        
        from contracts.customer_contract import CustomerContract
        from contracts.validator import SafeContractValidator
        
        validated_analysis = SafeContractValidator.validate(CustomerContract, analysis, "customer_agent")
        self.context["customer_analysis"] = validated_analysis
        return validated_analysis