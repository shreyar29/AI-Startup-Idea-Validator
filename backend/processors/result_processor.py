import logging
import time
import hashlib
import contextvars
from urllib.parse import urlparse
from typing import Dict, Any, List
from core.config import settings

logger = logging.getLogger("result_processor")

# 4. Centralize Trusted Domains
TRUSTED_DOMAINS = set(settings.guardrails.trusted_domains_list)
# Merge with previous set to ensure backwards compatibility
PREVIOUS_TRUSTED = {
    "gartner.com", "mckinsey.com", "cbinsights.com", "grandviewresearch.com",
    "statista.com", "crunchbase.com", "techcrunch.com", "ycombinator.com",
    "forbes.com", "bloomberg.com", "reuters.com", "wsj.com", "ft.com"
}
TRUSTED_DOMAINS.update(PREVIOUS_TRUSTED)

# 6. Centralize Keyword Lists
STOPWORDS = {'the', 'and', 'for', 'with', 'new', 'this', 'that', 'of', 'in', 'on', 'a', 'an', 'to', 'is', 'are', 'app', 'platform', 'software'}

BUSINESS_KEYWORDS = {"startup", "market", "pricing", "competitor", "business", "solution"}

CATEGORY_KEYWORDS = {
    "competitors": {"competitor", "startup", "company", "alternative", "product", "platform", "vs"},
    "market_size": {"cagr", "tam", "sam", "som", "market size", "billion", "million", "forecast", "report", "growth"},
    "customers": {"survey", "user", "behavior", "demographics", "pain point", "adoption", "consumer"},
    "technology": {"api", "iot", "ai", "architecture", "sensor", "gps", "cloud", "platform"},
    "pricing": {"subscription", "enterprise", "freemium", "cost", "price", "tier", "plan"},
    "business_model": {"monetization", "saas", "marketplace", "licensing", "commission", "revenue", "b2b", "b2c"},
    "trends": {"trend", "investment", "funding", "innovation", "emerging", "future"}
}

# 5. Replace Magic Numbers
TRUSTED_DOMAIN_BONUS = 5
IDEA_OVERLAP_MULTIPLIER = 2
CATEGORY_OVERLAP_MULTIPLIER = 2
BUSINESS_RELEVANCE_MULTIPLIER = 1
DATA_RICHNESS_BONUS = 3
MIN_SCORE_THRESHOLD = 3
MIN_CONTENT_LENGTH = 40

# 1. Thread-safe statistics
_processor_stats: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar("processor_stats", default={})

class ResultProcessor:
    def __init__(self):
        pass

    @property
    def last_stats(self) -> Dict[str, Any]:
        return _processor_stats.get()
        
    @last_stats.setter
    def last_stats(self, value: Dict[str, Any]):
        _processor_stats.set(value)

    def process(self, raw_results: dict, idea: str = "") -> dict:
        # 2. Replace time.time() with perf_counter()
        start_time = time.perf_counter()
        logger.info("ResultProcessor: Starting advanced deduplication and semantic filtering.")
        processed = {}
        seen_urls = set()
        seen_snippets_hashes = set()
        
        total_raw = 0
        total_discarded_dupes = 0
        total_discarded_low_quality = 0
        total_accepted = 0
        total_trusted = 0
        total_relevance = 0
        
        category_stats = {}

        idea_words = set(w.lower() for w in idea.split() if len(w) > 2 and w.lower() not in STOPWORDS)
        
        for category, results in raw_results.items():
            processed_list = []
            cat_accepted = 0
            cat_rejected = 0
            
            cat_kw = CATEGORY_KEYWORDS.get(category, set())

            if not isinstance(results, list):
                logger.warning(f"ResultProcessor: Expected list for category '{category}', got {type(results).__name__}. Treating as empty list.")
                results = []

            for item in results:
                total_raw += 1
                
                url = item.get("url", "").strip()
                content = item.get("content", "").strip()
                title = item.get("title", "No Title").strip()
                
                if not url or not content:
                    cat_rejected += 1
                    total_discarded_low_quality += 1
                    continue

                domain = urlparse(url).netloc.lower().replace("www.", "")

                # 1. Deduplication (URLs and content snippets)
                if url in seen_urls:
                    cat_rejected += 1
                    total_discarded_dupes += 1
                    continue
                    
                # 3. Deterministic Content Deduplication
                content_prefix = content[:250].lower().strip()
                content_hash = hashlib.sha256(content_prefix.encode("utf-8")).hexdigest()
                if content_hash in seen_snippets_hashes:
                    cat_rejected += 1
                    total_discarded_dupes += 1
                    continue

                # 2. Relevance Scoring
                score = 0
                content_lower = content.lower()
                title_lower = title.lower()
                
                # Base length check — aligned with web search agent filter
                if len(content) < MIN_CONTENT_LENGTH:
                    cat_rejected += 1
                    total_discarded_low_quality += 1
                    logger.debug(f"Discarded low-quality snippet from URL: {url} (Length: {len(content)})")
                    continue
                
                # Trusted Source Bonus
                is_trusted = domain in TRUSTED_DOMAINS
                if is_trusted:
                    score += TRUSTED_DOMAIN_BONUS
                    
                # Idea Relevance
                overlap = sum(1 for w in idea_words if w in content_lower or w in title_lower)
                score += (overlap * IDEA_OVERLAP_MULTIPLIER)
                
                # Category Relevance
                cat_overlap = sum(1 for w in cat_kw if w in content_lower or w in title_lower)
                score += (cat_overlap * CATEGORY_OVERLAP_MULTIPLIER)
                
                # Business Relevance
                bus_overlap = sum(1 for w in BUSINESS_KEYWORDS if w in content_lower or w in title_lower)
                score += (bus_overlap * BUSINESS_RELEVANCE_MULTIPLIER)
                
                # Data Richness (Numbers, $, % often indicate good research)
                if any(char.isdigit() or char in {'$', '%'} for char in content):
                    score += DATA_RICHNESS_BONUS
                
                # Explicit Rejection Filters
                if "dictionary" in domain or "meaning" in title_lower or "definition" in title_lower:
                    cat_rejected += 1
                    total_discarded_low_quality += 1
                    continue
                
                # Threshold
                if score < MIN_SCORE_THRESHOLD and len(idea_words) > 0:
                    cat_rejected += 1
                    total_discarded_low_quality += 1
                    logger.debug(f"Discarded low-relevance snippet: {url} (Score: {score})")
                    continue
                
                # Passed all filters
                seen_urls.add(url)
                seen_snippets_hashes.add(content_hash)
                
                total_accepted += 1
                cat_accepted += 1
                if is_trusted:
                    total_trusted += 1
                total_relevance += score
                
                processed_list.append({
                    "title": title,
                    "url": url,
                    "content": content,
                    "relevance_score": score,
                    "domain": domain
                })
                
            # Sort by relevance score
            processed_list.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            processed[category] = processed_list
            category_stats[category] = {"accepted": cat_accepted, "rejected": cat_rejected}
            logger.info(f"ResultProcessor: Category '{category}' - Accepted {len(processed_list)} snippets.")

        exec_time = time.perf_counter() - start_time
        
        # 7. Improve Search Confidence Calculation
        avg_score = (total_relevance / total_accepted) if total_accepted > 0 else 0
        trusted_ratio = (total_trusted / total_accepted) if total_accepted > 0 else 0
        categories_with_results = sum(1 for stat in category_stats.values() if stat["accepted"] > 0)
        total_categories = len(raw_results)
        category_coverage = (categories_with_results / total_categories) if total_categories > 0 else 0

        # Confidence Algorithm
        # Weightings: Count (25%), Avg Score (25%), Trusted (25%), Coverage (25%)
        # Normalization targets: 15 results, 10 avg score, 30% trusted, 100% coverage
        score_val = min(1.0, total_accepted / 15) * 0.25
        score_val += min(1.0, avg_score / 10) * 0.25
        score_val += min(1.0, trusted_ratio / 0.3) * 0.25
        score_val += category_coverage * 0.25
        
        if score_val >= 0.8:
            search_confidence = "High"
        elif score_val >= 0.4:
            search_confidence = "Medium"
        else:
            search_confidence = "Low"

        self.last_stats = {
            "total_raw_results": total_raw,
            "total_accepted": total_accepted,
            "total_rejected_duplicates": total_discarded_dupes,
            "total_rejected_low_quality": total_discarded_low_quality,
            "processing_time_seconds": round(exec_time, 3),
            "category_statistics": category_stats,
            "search_confidence": search_confidence
        }

        logger.info(
            f"ResultProcessor: Complete. Raw: {total_raw} | "
            f"Dupes: {total_discarded_dupes} | Low-Quality: {total_discarded_low_quality} | "
            f"Accepted: {total_accepted} | Time: {exec_time:.2f}s"
        )
        return processed
