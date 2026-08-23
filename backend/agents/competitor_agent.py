"""
competitor_agent.py
(Competitor Agent)

Purpose:
Milestone 2 — Competitor Discovery & Comparison Agent.
Identifies existing competitors, compares their offerings, and highlights
market gaps for the startup idea being validated using deterministic evidence extraction over raw search data.
"""

import asyncio
import logging
import json
import time
import hashlib
import re
from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import Any, Dict, List
from core.config import settings

_REVIEW_DOMAINS = [
    "g2", "capterra", "trustpilot", "forbes", "techradar", "techcrunch", "pcmag", "gartner", 
    "ycombinator", "reddit", "quora", "medium", "softwareadvice", "getapp", "pinterest", 
    "cnbc", "researchgate", "businessresearchcompany", "grandviewresearch", "bloomberg", 
    "reuters", "wsj", "nytimes", "wired", "theverge", "statista", "sourceforge", "github", 
    "wikipedia", "slant", "alternativeto", "trustradius", "producthunt", "news", "blog", 
    "directory", "list", "top", "best"
]

logger = logging.getLogger("competitor_agent")

class CompetitorAnalysisError(Exception):
    """Raised when competitor analysis fails."""

class CompetitorAgent:
    """
    Analyzes competitor landscape for a startup idea using research data.
    Operates as a decentralized node in the A2A Mesh Network.
    """

    def __init__(self, shared_context: dict):
        self.context = shared_context
        self.peers = {}
        self._analysis_task = None
        self.status = "idle" # States: idle, started, success, failed, timeout

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
                        logger.warning("CompetitorAgent: Previous task completed in degraded state. Resetting task.")
                        self._analysis_task = None
                except Exception as e:
                    logger.warning(f"CompetitorAgent: Previous task failed with '{e}'. Resetting task.")
                    self._analysis_task = None

        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(self._perform_analysis())
            
        try:
            return await self._analysis_task
        except asyncio.CancelledError:
            logger.warning("CompetitorAgent: Task cancelled. Resetting state.")
            self._analysis_task = None
            self.status = "failed"
            raise
        except Exception:
            raise

    async def _perform_analysis(self):
        """Pulls required data from peers and runs the analysis."""
        self.status = "started"
        start_time = time.perf_counter()
        correlation_id = self.context.get("correlation_id", "N/A")
        log_prefix = f"[{correlation_id}] CompetitorAgent:"
        
        try:
            logger.info(f"{log_prefix} Awaiting research payload from Web Search Agent.")
            if "web_search" in self.peers:
                research_data = await self.peers["web_search"].get_analysis()
                self.context["research"] = research_data
                logger.info(f"{log_prefix} Successfully received research payload.")
                
            result = await self.analyze(log_prefix)
            self.status = "success"
            
            duration = time.perf_counter() - start_time
            logger.info(f"{log_prefix} Completed successfully in {duration:.2f}s.")
            return result
            
        except asyncio.TimeoutError as e:
            self.status = "timeout"
            duration = time.perf_counter() - start_time
            logger.error(f"{log_prefix} Timed out after {duration:.2f}s: {e}")
            return self._return_degraded("Analysis timed out.", "Low")
        except Exception as e:
            self.status = "failed"
            duration = time.perf_counter() - start_time
            logger.exception(f"{log_prefix} Failed unexpectedly after {duration:.2f}s: {e}")
            return self._return_degraded(f"Unexpected failure: {str(e)}", "Low")

    def _validate_and_coerce_list(self, val: Any) -> list:
        """Helper to ensure a value is strictly a list of strings."""
        if not val:
            return []
        if isinstance(val, list):
            return [str(v) for v in val if v]
        if isinstance(val, str):
            return [val]
        return []

    def _return_degraded(self, reason: str, confidence: str):
        analysis = {
            "competitors": [],
            "competitor_gaps": [f"Analysis could not be completed: {reason}"],
            "gap_analysis": [f"Analysis could not be completed: {reason}"],
            "confidence": confidence,
            "no_competitor_data_found": True,
            "failure_reason": reason,
            "status": self.status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.context["competitor_analysis"] = analysis
        return analysis

    async def analyze(self, log_prefix: str = "CompetitorAgent:"):
        """
        Main entry point. Populates and returns shared_context["competitor_analysis"].
        """
        logger.info(f"{log_prefix} Execution started.")
        
        research = self.context.get("research") or {}
        if "search_results" in research and isinstance(research["search_results"], dict):
            research = research["search_results"]
            
        idea_data = self.context.get("idea") or {}
        idea = idea_data.get("description", "Unknown startup idea")

        competitor_snippets = []
        seen_hashes = set()
        
        # Configuration Limits
        max_snippets = settings.agent.COMPETITOR_MAX_SNIPPETS
        max_snippet_length = settings.agent.COMPETITOR_MAX_SNIPPET_LENGTH
        
        priority_categories = ["competitor", "alternatives", "products", "business", "startup"]
        
        # Dynamically consume all categories from web search
        for cat, results in research.items():
            if not any(p in cat.lower() for p in priority_categories):
                continue
            if isinstance(results, list):
                for r in results:
                    content = str(r.get("content") or "").strip()
                    url = str(r.get("url") or "").strip()
                    title = str(r.get("title") or "").strip()
                    relevance = r.get("relevance_score", 0)
                    
                    if not content or not url:
                        continue
                        
                    # Deterministic semantic duplicate detection using content hash prefix
                    snippet_hash = hashlib.sha256(content[:250].lower().encode('utf-8')).hexdigest()
                    if snippet_hash not in seen_hashes:
                        seen_hashes.add(snippet_hash)
                        competitor_snippets.append({
                            "url": url,
                            "title": title,
                            "content": content,
                            "relevance": relevance,
                            "length": len(content)
                        })

        if not competitor_snippets:
            logger.warning(f"{log_prefix} No research data snippets found. Degrading gracefully.")
            return self._return_degraded("No valid research snippets found in context.", "Low")
            
        logger.info(f"{log_prefix} Consolidated {len(competitor_snippets)} unique snippets.")

        # Optimize snippet selection: sort by relevance and length, take top N
        competitor_snippets.sort(key=lambda x: (x["relevance"], x["length"]), reverse=True)
        top_snippets = competitor_snippets[:max_snippets]
        
        parsed_analysis = {"competitors": []}

        for s in top_snippets:
            title = s.get("title", "")
            content = s.get("content", "")
            url = s.get("url", "")
            
            name = "Unknown"
            
            try:
                domain = urlparse(url).netloc.lower()
                domain_parts = domain.replace("www.", "").split(".")
                domain_name = domain_parts[0] if len(domain_parts) > 0 else ""
                
                if domain_name and domain_name not in _REVIEW_DOMAINS and len(domain_name) > 2:
                    name = domain_name.capitalize()
                else:
                    path = urlparse(url).path.lower()
                    path_parts = [p for p in path.split("/") if p]
                    
                    if "products" in path_parts or "software" in path_parts:
                        for i, p in enumerate(path_parts):
                            if p in ["products", "software", "reviews", "app"] and i + 1 < len(path_parts):
                                possible_name = path_parts[i+1].replace("-", " ")
                                if len(possible_name) > 2:
                                    name = possible_name.title()
                                    break
                                    
                    if name == "Unknown" and title:
                        clean_title = title.split("|")[0].split("-")[0].strip()
                        if clean_title:
                            lower_title = clean_title.lower()
                            if not any(x in lower_title for x in ["best", "top", "alternatives", "vs", "software", "tools", "review"]):
                                name = clean_title
                            else:
                                vs_match = re.search(r'([A-Z][a-zA-Z0-9]+)\s+vs\.?\s+([A-Z][a-zA-Z0-9]+)', title)
                                if vs_match:
                                    name = vs_match.group(1) if vs_match.group(1).lower() != idea.lower() else vs_match.group(2)
            except Exception:
                pass
                
            if not name or name.lower() in ["unknown", "", "home", "about", "index"]:
                if title:
                    fallback = title.split("|")[0].split("-")[0].strip()
                    if fallback and len(fallback) < 25:
                        name = fallback
                        
            if not name or name.lower() in ["unknown", ""]:
                continue
                
            pricing = "Unknown"
            price_match = re.search(r'(\$\d+(?:\.\d+)?(?:\/(?:mo|year|month))?)', content, re.IGNORECASE)
            if price_match:
                pricing = price_match.group(1)
            elif re.search(r'\b(free|freemium)\b', content, re.IGNORECASE):
                pricing = "Free/Freemium"
            elif re.search(r'\b(custom pricing|contact us|enterprise plan)\b', content, re.IGNORECASE):
                pricing = "Custom/Enterprise"
                
            features = []
            strengths = []
            weaknesses = []
            target_customers = "Unknown"
            business_model = "Unknown"
            
            sentences = [sen.strip() for sen in content.split('.') if sen.strip()]
            for sen in sentences:
                clean_sen = sen[:100] + "..." if len(sen) > 100 else sen
                lower_sen = sen.lower()
                if any(kw in lower_sen for kw in ["offer", "feature", "provide", "platform", "tool", "solution", "support", "allow"]):
                    if len(sen) > 15 and clean_sen not in features:
                        features.append(clean_sen)
                if any(kw in lower_sen for kw in ["strength", "best for", "excel at", "pro", "advantage", "stand out"]):
                    if len(sen) > 15 and clean_sen not in strengths:
                        strengths.append(clean_sen)
                if any(kw in lower_sen for kw in ["weakness", "bad", "lack", "con", "disadvantage", "struggle", "complain", "fail"]):
                    if len(sen) > 15 and clean_sen not in weaknesses:
                        weaknesses.append(clean_sen)
                if target_customers == "Unknown" and any(kw in lower_sen for kw in ["target", "designed for", "aimed at", "users", "audience"]):
                    target_customers = clean_sen
                if business_model == "Unknown" and any(kw in lower_sen for kw in ["freemium", "subscription", "enterprise", "b2b", "b2c", "saas"]):
                    if "freemium" in lower_sen: business_model = "Freemium"
                    elif "subscription" in lower_sen: business_model = "Subscription"
                    elif "saas" in lower_sen: business_model = "SaaS"
                    else: business_model = "B2B/Enterprise"
                        
            parsed_analysis["competitors"].append({
                "name": name,
                "features": features[:3],
                "pricing": pricing,
                "strengths": strengths[:3],
                "weaknesses": weaknesses[:3],
                "target_customers": target_customers,
                "business_model": business_model,
                "source_references": [url]
            })
            
        logger.info(f"{log_prefix} Extracted competitor analysis using deterministic python logic.")

        logger.info(f"{log_prefix} Validating and structuring response generation.")

        raw_competitors = parsed_analysis.get("competitors")
        if not isinstance(raw_competitors, list):
            raw_competitors = []
            
        validated_competitors = []
        competitor_map = {}
        
        comps_discovered = len(raw_competitors)
        comps_rejected = 0
        comps_merged = 0
        
        for comp in raw_competitors:
            if not isinstance(comp, dict):
                comps_rejected += 1
                continue
            name = str(comp.get("name") or "").strip()
            
            if not name or name.lower() in ["unknown competitor", "unknown", "n/a", "none"]:
                comps_rejected += 1
                continue
                
            name_lower = name.lower()
            features = self._validate_and_coerce_list(comp.get("features"))
            source_references = self._validate_and_coerce_list(comp.get("source_references"))
            pricing = str(comp.get("pricing") or "Unknown")
            strengths = self._validate_and_coerce_list(comp.get("strengths"))
            weaknesses = self._validate_and_coerce_list(comp.get("weaknesses"))
            target_customers = str(comp.get("target_customers") or "Unavailable")
            business_model = str(comp.get("business_model") or "Unavailable")

            if name_lower in competitor_map:
                existing = competitor_map[name_lower]
                existing["features"] = list(dict.fromkeys(existing["features"] + features))
                existing["source_references"] = list(dict.fromkeys(existing["source_references"] + source_references))
                existing["strengths"] = list(dict.fromkeys(existing["strengths"] + strengths))
                existing["weaknesses"] = list(dict.fromkeys(existing["weaknesses"] + weaknesses))
                
                if existing["pricing"] in ["Pricing unavailable", "Unavailable", "Unknown", ""] and pricing not in [None, "Pricing unavailable", "Unavailable", "Unknown", ""]:
                    existing["pricing"] = pricing
                if existing.get("target_customers") in ["Unavailable", "Unknown", ""] and target_customers not in [None, "Unavailable", "Unknown", ""]:
                    existing["target_customers"] = target_customers
                if existing.get("business_model") in ["Unavailable", "Unknown", ""] and business_model not in [None, "Unavailable", "Unknown", ""]:
                    existing["business_model"] = business_model
                    
                comps_merged += 1
                continue
                
            summary = f"Provides {', '.join(features[:3])}." if features else "Product details unknown."
            
            has_sources = len(source_references) > 0
            comp_confidence = "High" if has_sources else "Medium"
            
            positioning = f"Positioned as a {business_model} solution targeting {target_customers[:50]}."
            if features: positioning += f" Core focus on {features[0][:30]}."
            
            valid_comp = {
                "name": name,
                "product_summary": summary,
                "features": features,
                "pricing": pricing,
                "business_model": business_model,
                "market_positioning": positioning,
                "target_customers": target_customers,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "source_references": source_references,
                "confidence_score": comp_confidence,
                "threat_score": 0,
                "rank": 0
            }
            competitor_map[name_lower] = valid_comp
            validated_competitors.append(valid_comp)
        
        # Threat Score & Ranking
        for comp in validated_competitors:
            overlap = len(comp["features"]) * 5 + len(comp["strengths"]) * 3
            if len(comp["source_references"]) > 1: overlap += 15
            if comp["business_model"] != "Unavailable": overlap += 10
            if comp["pricing"] != "Unknown": overlap += 10
            
            # Additional penalty if it targets similar audience based on 'idea'
            idea_words = set(idea.lower().split())
            audience_words = set(comp["target_customers"].lower().split())
            if idea_words.intersection(audience_words):
                overlap += 10
                
            comp["threat_score"] = min(100, max(0, overlap))
            
        validated_competitors.sort(key=lambda x: x["threat_score"], reverse=True)
        for i, comp in enumerate(validated_competitors):
            comp["rank"] = i + 1
            
        logger.info(f"{log_prefix} Processing Stats: Discovered={comps_discovered}, Rejected={comps_rejected}, Merged={comps_merged}, Final Valid={len(validated_competitors)}")

        raw_gap_analysis = self._generate_gap_analysis(validated_competitors)

        # Evidence-Quality based Confidence
        total_sources = sum(len(c["source_references"]) for c in validated_competitors)
        multi_source_competitors = sum(1 for c in validated_competitors if len(c["source_references"]) > 1)
        
        if not validated_competitors:
            overall_confidence = "Low"
        elif total_sources >= 5 and multi_source_competitors >= 1:
            overall_confidence = "High"
        elif total_sources >= 2:
            overall_confidence = "Medium"
        else:
            overall_confidence = "Low"

        self.status = "success"
        analysis = {
            "competitors": validated_competitors,
            "competitor_gaps": self._validate_and_coerce_list(raw_gap_analysis),
            "gap_analysis": self._validate_and_coerce_list(raw_gap_analysis),
            "confidence": overall_confidence,
            "no_competitor_data_found": len(validated_competitors) == 0,
            "failure_reason": None,
            "status": self.status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info("CompetitorAgent: Successful completion. Output ready for downstream agents.")
        self.context["competitor_analysis"] = analysis
        return analysis

    def _generate_gap_analysis(self, competitors: list) -> list:
        if not competitors:
            return ["No competitor data available for gap analysis."]
        
        all_features = {}
        all_pricing = []
        all_audience = []
        
        for c in competitors:
            for f in c.get("features", []):
                feat = str(f).lower().strip()
                all_features[feat] = all_features.get(feat, 0) + 1
            if c.get("pricing") not in ["Unknown", "Pricing unavailable", ""]:
                all_pricing.append(c["pricing"].lower())
            if c.get("target_customers") not in ["Unknown", "Unavailable", ""]:
                all_audience.append(c["target_customers"])
                
        if not all_features:
            return ["No competitor features found to identify gaps."]
            
        common_features = [f for f, count in all_features.items() if count > len(competitors) // 2]
        rare_features = [f for f, count in all_features.items() if count <= len(competitors) // 2]
        
        gaps = []
        if common_features:
            gaps.append(f"Most competitors focus on: {', '.join(common_features[:3])}.")
        if rare_features:
            gaps.append(f"Opportunity Space: Few competitors provide: {', '.join(rare_features[:3])}.")
            
        free_tier = any("free" in p for p in all_pricing)
        if all_pricing and not free_tier:
            gaps.append("Pricing Gap: No major competitor offers a Free/Freemium tier.")
        elif all_pricing and free_tier:
            gaps.append("Pricing Threat: Existing free/freemium options dominate entry-level.")
            
        return gaps if gaps else ["No distinct competitive gaps identified."]