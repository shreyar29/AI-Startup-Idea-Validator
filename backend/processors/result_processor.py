import logging
import time
from urllib.parse import urlparse

logger = logging.getLogger("result_processor")

class ResultProcessor:
    def __init__(self):
        self.last_stats = {}

    def process(self, raw_results: dict, idea: str = "") -> dict:
        start_time = time.time()
        logger.info("ResultProcessor: Starting advanced deduplication and semantic filtering.")
        processed = {}
        seen_urls = set()
        seen_snippets_hashes = set()
        
        total_raw = 0
        total_discarded_dupes = 0
        total_discarded_low_quality = 0
        total_accepted = 0
        
        category_stats = {}

        # Semantic keywords derived from idea
        stopwords = {'the', 'and', 'for', 'with', 'new', 'this', 'that', 'of', 'in', 'on', 'a', 'an', 'to', 'is', 'are', 'app', 'platform', 'software'}
        idea_words = set(w.lower() for w in idea.split() if len(w) > 2 and w.lower() not in stopwords)
        
        trusted_domains = {
            "gartner.com", "mckinsey.com", "cbinsights.com", "grandviewresearch.com",
            "statista.com", "crunchbase.com", "techcrunch.com", "ycombinator.com",
            "forbes.com", "bloomberg.com", "reuters.com", "wsj.com", "ft.com"
        }
        
        category_keywords = {
            "competitors": {"competitor", "startup", "company", "alternative", "product", "platform", "vs"},
            "market_size": {"cagr", "tam", "sam", "som", "market size", "billion", "million", "forecast", "report", "growth"},
            "customers": {"survey", "user", "behavior", "demographics", "pain point", "adoption", "consumer"},
            "technology": {"api", "iot", "ai", "architecture", "sensor", "gps", "cloud", "platform"},
            "pricing": {"subscription", "enterprise", "freemium", "cost", "price", "tier", "plan"},
            "business_model": {"monetization", "saas", "marketplace", "licensing", "commission", "revenue", "b2b", "b2c"},
            "trends": {"trend", "investment", "funding", "innovation", "emerging", "future"}
        }

        for category, results in raw_results.items():
            processed_list = []
            cat_accepted = 0
            cat_rejected = 0
            
            cat_kw = category_keywords.get(category, set())

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
                    
                content_prefix = content[:100].lower()
                if content_prefix in seen_snippets_hashes:
                    cat_rejected += 1
                    total_discarded_dupes += 1
                    continue

                # 2. Relevance Scoring
                score = 0
                content_lower = content.lower()
                title_lower = title.lower()
                
                # Base length check — aligned with web search agent filter
                if len(content) < 40:
                    cat_rejected += 1
                    total_discarded_low_quality += 1
                    logger.debug(f"Discarded low-quality snippet from URL: {url} (Length: {len(content)})")
                    continue
                
                # Trusted Source Bonus
                if domain in trusted_domains:
                    score += 5
                    
                # Idea Relevance
                overlap = sum(1 for w in idea_words if w in content_lower or w in title_lower)
                score += (overlap * 2)
                
                # Category Relevance
                cat_overlap = sum(1 for w in cat_kw if w in content_lower or w in title_lower)
                score += (cat_overlap * 2)
                
                # Business Relevance
                business_words = {"startup", "market", "pricing", "competitor", "business", "solution"}
                bus_overlap = sum(1 for w in business_words if w in content_lower or w in title_lower)
                score += bus_overlap
                
                # Data Richness (Numbers, $, % often indicate good research)
                if any(char.isdigit() or char in {'$', '%'} for char in content):
                    score += 3
                
                # Explicit Rejection Filters
                if "dictionary" in domain or "meaning" in title_lower or "definition" in title_lower:
                    cat_rejected += 1
                    total_discarded_low_quality += 1
                    continue
                
                # Threshold
                if score < 3 and len(idea_words) > 0:
                    cat_rejected += 1
                    total_discarded_low_quality += 1
                    logger.debug(f"Discarded low-relevance snippet: {url} (Score: {score})")
                    continue
                
                # Passed all filters
                seen_urls.add(url)
                seen_snippets_hashes.add(content_prefix)
                
                total_accepted += 1
                cat_accepted += 1
                
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

        exec_time = time.time() - start_time
        
        self.last_stats = {
            "total_raw_results": total_raw,
            "total_accepted": total_accepted,
            "total_rejected_duplicates": total_discarded_dupes,
            "total_rejected_low_quality": total_discarded_low_quality,
            "processing_time_seconds": round(exec_time, 3),
            "category_statistics": category_stats,
            "search_confidence": "High" if total_accepted > 10 else ("Medium" if total_accepted > 0 else "Low")
        }

        logger.info(
            f"ResultProcessor: Complete. Raw: {total_raw} | "
            f"Dupes: {total_discarded_dupes} | Low-Quality: {total_discarded_low_quality} | "
            f"Accepted: {total_accepted} | Time: {exec_time:.2f}s"
        )
        return processed
