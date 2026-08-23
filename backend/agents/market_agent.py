"""
market_agent.py
(Market Agent)

Purpose:
Milestone 2 — Market Opportunity Agent.
Synthesizes raw search results into structured market insights (market size, growth rate, trends, opportunities, challenges) using deterministic evidence extraction.
"""

import asyncio
import logging
import json
import time
import re
from core.config import settings
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger("market_agent")

class MarketAnalysisError(Exception):
    """Raised when market analysis fails."""

class MarketOpportunityAgent:
    """
    Analyzes the market for a startup idea using research data.
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
        """
        if self._analysis_task is not None:
            if self._analysis_task.done():
                try:
                    self._analysis_task.result()
                    if self.status in ["failed", "timeout"]:
                        logger.warning("MarketOpportunityAgent: Previous task completed in degraded state. Resetting task.")
                        self._analysis_task = None
                except Exception as e:
                    logger.warning(f"MarketOpportunityAgent: Previous task failed with '{e}'. Resetting task.")
                    self._analysis_task = None

        if self._analysis_task is None:
            self._analysis_task = asyncio.create_task(self._perform_analysis())
            
        try:
            return await self._analysis_task
        except asyncio.CancelledError:
            logger.warning("MarketOpportunityAgent: Task cancelled. Resetting state.")
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
        log_prefix = f"[{correlation_id}] MarketAgent:"
        
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
            return self._return_degraded("Analysis timed out.", "Low", log_prefix)
        except Exception as e:
            self.status = "failed"
            duration = time.perf_counter() - start_time
            logger.exception(f"{log_prefix} Failed unexpectedly after {duration:.2f}s: {e}")
            return self._return_degraded(f"Unexpected failure: {str(e)}", "Low", log_prefix)

    def _validate_and_coerce_list(self, val: Any) -> list:
        """Helper to ensure a value is strictly a list of strings."""
        if not val:
            return []
        if isinstance(val, list):
            return [str(v) for v in val if v]
        if isinstance(val, str):
            return [val]
        return []

    def _dedupe_list(self, raw_list: list) -> list:
        val_list = self._validate_and_coerce_list(raw_list)
        return list(dict.fromkeys(val_list))

    def _get_field(self, data: dict, key: str, default: str = "Insufficient verified evidence.") -> str:
        val = data.get(key)
        if not val or val == "Data unavailable":
            return default
        return str(val)

    def _return_degraded(self, reason: str, confidence: str, log_prefix: str = "MarketAgent:"):
        analysis = {
            "market_size": "Data unavailable",
            "growth_rate": "Data unavailable",
            "market_maturity": "Data unavailable",
            "market_segmentation": [],
            "growth_drivers": [],
            "market_trends": [],
            "opportunities": [],
            "challenges": [],
            "industry_insights": [],
            "market_summary": f"Analysis could not be completed: {reason}",
            "confidence_score": confidence,
            "market_timing": "Data unavailable",
            "opportunity_score": 0,
            "status": self.status,
            "failure_reason": reason,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "evidence": []
        }
        self.context["market_analysis"] = analysis
        return analysis

    async def analyze(self, log_prefix: str = "MarketAgent:"):
        """
        Main entry point. Uses deterministic python logic to extract quantitative market metrics
        and trends from raw search snippets.
        Populates and returns shared_context["market_analysis"].
        """
        logger.info(f"{log_prefix} Execution started.")
        
        research = self.context.get("research") or {}
        if "search_results" in research and isinstance(research["search_results"], dict):
            research = research["search_results"]

        # Configuration Limits
        max_snippets = settings.agent.MARKET_MAX_SNIPPETS
        max_snippet_length = settings.agent.MARKET_MAX_SNIPPET_LENGTH
        auth_domains = [
            "gartner.", "statista.", "mckinsey.", "grandviewresearch.", ".gov", ".edu", "forrester.", "idc.", "bloomberg.",
            "grandviewresearch.com", "mordorintelligence.com", "imarcgroup.com", "fortunebusinessinsights.com",
            "marketresearchfuture.com", "snsinsider.com", "globenewswire.com", "businesswire.com"
        ]
        priority_categories = ["market", "growth", "forecast", "industry", "trend"]

        snippets = []
        seen_hashes = set()
        current_year = datetime.now().year
        year_pattern = re.compile(r'\b(20\d{2})\b')

        for cat, results in research.items():
            if not isinstance(results, list):
                continue
                
            cat_lower = cat.lower()
            if not any(p in cat_lower for p in priority_categories):
                continue
                
            for r in results:
                content = str(r.get("content") or "").strip()
                url = str(r.get("url") or "").strip()
                relevance = r.get("relevance_score", 0)
                
                if not content or not url:
                    continue
                    
                snippet_hash = hashlib.sha256(content[:250].lower().encode('utf-8')).hexdigest()
                if snippet_hash not in seen_hashes:
                    seen_hashes.add(snippet_hash)
                    
                    # Boost authority
                    is_authoritative = any(d in url.lower() for d in auth_domains)
                    
                    # Freshness
                    years = [int(y) for y in year_pattern.findall(content) if 2010 <= int(y) <= current_year + 5]
                    freshness_score = 0
                    if years:
                        max_year = max(years)
                        if max_year >= current_year: freshness_score = 10
                        elif max_year >= current_year - 2: freshness_score = 7
                        elif max_year >= current_year - 5: freshness_score = 4
                        
                    score = relevance + (5 if is_authoritative else 0) + (freshness_score / 2)
                    
                    snippets.append({
                        "category": cat,
                        "url": url,
                        "content": content,
                        "score": score,
                        "length": len(content),
                        "authority_score": 10 if is_authoritative else 2,
                        "relevance_score": relevance,
                        "freshness_score": freshness_score
                    })

        if not snippets:
            logger.warning(f"{log_prefix} No market-related research data found. Degrading gracefully.")
            return self._return_degraded("No valid market research snippets found.", "Low", log_prefix)
            
        logger.info(f"{log_prefix} Consolidated {len(snippets)} unique snippets for analysis.")
        
        snippets.sort(key=lambda x: (x["score"], x["length"]), reverse=True)
        top_snippets = snippets[:max_snippets]
        
        parsed_analysis = {
            "market_size": "Insufficient verified evidence.",
            "growth_rate": "Insufficient verified evidence.",
            "market_maturity": "Insufficient verified evidence.",
            "market_trends": [],
            "drivers": [],
            "risks": [],
            "regulations": [],
            "segmentation": []
        }
        
        size_pattern = re.compile(r'\$?\d+(?:\.\d+)?\s*(?:billion|million|trillion|B|M|T)', re.IGNORECASE)
        cagr_pattern = re.compile(r'(?:cagr\s*(?:of)?\s*)?(\d+(?:\.\d+)?%|\d+(?:\.\d+)?\s*percent)', re.IGNORECASE)
        
        structured_evidence = []
        
        for s in top_snippets:
            content = s.get('content', '')
            url = s.get('url', '')
            
            structured_evidence.append({
                "url": url,
                "authority_score": s["authority_score"],
                "category": s["category"],
                "relevance_score": s["relevance_score"],
                "freshness_score": s["freshness_score"]
            })
            
            sentences = [sen.strip() for sen in content.split('.') if sen.strip()]
            
            if parsed_analysis["market_size"] == "Insufficient verified evidence.":
                size_match = size_pattern.search(content)
                if size_match:
                    parsed_analysis["market_size"] = size_match.group(0)
                else:
                    for sen in sentences:
                        if "market size" in sen.lower() or "valued at" in sen.lower():
                            parsed_analysis["market_size"] = sen[:60] + "..." if len(sen) > 60 else sen
                            break

            if parsed_analysis["growth_rate"] == "Insufficient verified evidence.":
                cagr_match = cagr_pattern.search(content)
                if cagr_match:
                    parsed_analysis["growth_rate"] = cagr_match.group(0)
                else:
                    for sen in sentences:
                        if "cagr" in sen.lower() or "grow at" in sen.lower() or "growth rate" in sen.lower():
                            parsed_analysis["growth_rate"] = sen[:60] + "..." if len(sen) > 60 else sen
                            break

            if parsed_analysis["market_maturity"] == "Insufficient verified evidence.":
                if "mature" in content.lower() or "established" in content.lower():
                    parsed_analysis["market_maturity"] = "Mature"
                elif "emerging" in content.lower() or "early" in content.lower():
                    parsed_analysis["market_maturity"] = "Emerging"
                elif "growing" in content.lower():
                    parsed_analysis["market_maturity"] = "Growing"

            for sen in sentences:
                sen_lower = sen.lower()
                clean_sen = sen.capitalize()
                if any(kw in sen_lower for kw in ["trend", "increasing", "growing", "demand", "shift"]):
                    if clean_sen not in parsed_analysis["market_trends"] and len(sen) > 10:
                        parsed_analysis["market_trends"].append(clean_sen)
                if any(kw in sen_lower for kw in ["drive", "driver", "fuel", "propel", "catalyst", "adoption"]):
                    if clean_sen not in parsed_analysis["drivers"] and len(sen) > 10:
                        parsed_analysis["drivers"].append(clean_sen)
                if any(kw in sen_lower for kw in ["risk", "threat", "challenge", "barrier", "obstacle", "hinder"]):
                    if clean_sen not in parsed_analysis["risks"] and len(sen) > 10:
                        parsed_analysis["risks"].append(clean_sen)
                if any(kw in sen_lower for kw in ["regulation", "compliance", "law", "policy", "legal"]):
                    if clean_sen not in parsed_analysis["regulations"] and len(sen) > 10:
                        parsed_analysis["regulations"].append(clean_sen)
                if any(kw in sen_lower for kw in ["segment", "demographic", "audience", "adoption by"]):
                    if clean_sen not in parsed_analysis["segmentation"] and len(sen) > 10:
                        parsed_analysis["segmentation"].append(clean_sen)
                        
        if parsed_analysis["market_maturity"] == "Insufficient verified evidence.":
            parsed_analysis["market_maturity"] = "Growing"
            
        parsed_analysis["market_trends"] = parsed_analysis["market_trends"][:5]
        parsed_analysis["drivers"] = parsed_analysis["drivers"][:5]
        parsed_analysis["risks"] = parsed_analysis["risks"][:5]
        parsed_analysis["regulations"] = parsed_analysis["regulations"][:5]
        parsed_analysis["segmentation"] = parsed_analysis["segmentation"][:4]
        logger.info(f"{log_prefix} Extracted market analysis using deterministic python logic.")

        logger.info(f"{log_prefix} Validating and structuring response generation.")

        market_size = self._get_field(parsed_analysis, "market_size")
        growth_rate = self._get_field(parsed_analysis, "growth_rate")
        market_maturity = self._get_field(parsed_analysis, "market_maturity")
        
        market_trends = self._dedupe_list(parsed_analysis.get("market_trends"))
        growth_drivers = self._dedupe_list(parsed_analysis.get("drivers"))
        risks = self._dedupe_list(parsed_analysis.get("risks"))
        regulations = self._dedupe_list(parsed_analysis.get("regulations"))
        market_segmentation = self._dedupe_list(parsed_analysis.get("segmentation"))
        
        opportunities = list(set([t for t in market_trends] + [d for d in growth_drivers]))[:5]
        challenges = risks
        industry_insights = regulations

        # Calculate evidence-quality based confidence score
        completeness = sum(1 for v in [market_size, growth_rate, market_maturity] if v != "Insufficient verified evidence.")
        completeness += 1 if market_trends else 0
        completeness += 1 if growth_drivers else 0
        
        evidence_count = len(structured_evidence)
        auth_count = sum(1 for e in structured_evidence if e["authority_score"] >= 10)
        
        total_confidence_points = (completeness * 10) + (evidence_count * 2) + (auth_count * 5)
        
        if total_confidence_points >= 50:
            confidence = "High"
        elif total_confidence_points >= 25:
            confidence = "Medium"
        else:
            confidence = "Low"

        # Calculate opportunity score (0-100)
        opportunity_score = 30
        opportunity_score += len(opportunities) * 6
        opportunity_score -= len(challenges) * 4
        
        if growth_rate != "Insufficient verified evidence.":
            try:
                gr_match = re.search(r'(\d+(?:\.\d+)?)', growth_rate)
                if gr_match:
                    gr_val = float(gr_match.group(1))
                    if gr_val >= 15: opportunity_score += 25
                    elif gr_val >= 5: opportunity_score += 15
                    else: opportunity_score += 5
            except Exception:
                pass
                
        if market_maturity == "Growing": opportunity_score += 15
        elif market_maturity == "Emerging": opportunity_score += 20
        elif market_maturity == "Mature": opportunity_score -= 5
        
        opportunity_score = max(0, min(100, int(opportunity_score)))

        # Dynamic Market Summary
        summary_parts = []
        if market_size != "Insufficient verified evidence.":
            summary_parts.append(f"The market size is currently estimated at {market_size}.")
        if growth_rate != "Insufficient verified evidence.":
            summary_parts.append(f"It is experiencing a growth rate of {growth_rate}.")
        summary_parts.append(f"The overall market maturity is assessed as '{market_maturity}'.")
        
        if opportunities:
            summary_parts.append(f"Key identified opportunities include {', '.join(opportunities[:2].copy())}.")
        
        market_summary = " ".join(summary_parts) if summary_parts else "Market intelligence could not be definitively summarized from the available data."

        analysis = {
            "market_size": market_size,
            "growth_rate": growth_rate,
            "market_maturity": market_maturity,
            "market_segmentation": market_segmentation,
            "growth_drivers": growth_drivers,
            "market_trends": market_trends,
            "opportunities": opportunities,
            "challenges": challenges,
            "industry_insights": industry_insights,
            "regulations": regulations,
            "evidence": structured_evidence,
            "market_summary": market_summary,
            "confidence_score": confidence,
            "market_timing": "Data unavailable",
            "opportunity_score": opportunity_score,
            "status": "success",
            "failure_reason": None,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        stats = {
            "trends_extracted": len(market_trends),
            "opportunities_extracted": len(opportunities),
            "challenges_extracted": len(challenges),
            "confidence": confidence,
            "opportunity_score": opportunity_score
        }
        logger.info(f"{log_prefix} Processing Stats: {stats}")

        logger.info(f"{log_prefix} Successful completion. Output ready for downstream agents.")
        self.context["market_analysis"] = analysis
        return analysis
