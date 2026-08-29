import logging
import time
import hashlib
import contextvars
from urllib.parse import urlparse
from typing import Dict, Any, List, Set, Tuple

from processors.constants import (
    STOPWORDS, CATEGORY_KEYWORDS, MIN_CONTENT_LENGTH, MIN_SCORE_THRESHOLD, TRUSTED_DOMAINS
)
from processors.models import RawSearchResult, ProcessedSearchResult, ProcessingStats
from processors.relevance_scorer import RelevanceScorer
from processors.confidence_calculator import ConfidenceCalculator

logger = logging.getLogger("result_processor")

# Thread-safe statistics
_processor_stats: contextvars.ContextVar[ProcessingStats] = contextvars.ContextVar("processor_stats", default=None)

class ResultProcessor:
    def __init__(self):
        self.confidence_calculator = ConfidenceCalculator()

    @property
    def last_stats(self) -> Dict[str, Any]:
        stats = _processor_stats.get()
        return stats.model_dump() if stats else {}
        
    @last_stats.setter
    def last_stats(self, value: Dict[str, Any]):
        _processor_stats.set(ProcessingStats(**value))

    def process(self, raw_results: Dict[str, List[Dict[str, Any]]], idea: str = "") -> Dict[str, List[Dict[str, Any]]]:
        start_time = time.perf_counter()
        logger.info("ResultProcessor: Starting advanced deduplication and semantic filtering.")
        
        processed: Dict[str, List[Dict[str, Any]]] = {}
        seen_urls: Set[str] = set()
        seen_snippets_hashes: Set[str] = set()
        
        # State tracking dictionary for aggregations across categories
        state = {
            "total_raw": 0,
            "total_discarded_dupes": 0,
            "total_discarded_low_quality": 0,
            "total_accepted": 0,
            "total_trusted": 0,
            "total_relevance": 0
        }
        category_stats: Dict[str, Dict[str, int]] = {}

        idea_words = self._extract_idea_words(idea)
        
        for category, results in raw_results.items():
            if not isinstance(results, list):
                logger.warning(f"ResultProcessor: Expected list for category '{category}', got {type(results).__name__}. Treating as empty list.")
                results = []
                
            processed_list, cat_accepted, cat_rejected = self._process_category(
                category=category,
                results=results,
                idea_words=idea_words,
                seen_urls=seen_urls,
                seen_snippets_hashes=seen_snippets_hashes,
                state=state
            )
            
            processed[category] = [item.model_dump() for item in processed_list]
            category_stats[category] = {"accepted": cat_accepted, "rejected": cat_rejected}
            logger.info(f"ResultProcessor: Category '{category}' - Accepted {len(processed_list)} snippets.")

        exec_time = time.perf_counter() - start_time
        
        self._update_stats(
            state=state,
            category_stats=category_stats,
            total_categories=len(raw_results),
            exec_time=exec_time
        )

        logger.info(
            f"ResultProcessor: Complete. Raw: {state['total_raw']} | "
            f"Dupes: {state['total_discarded_dupes']} | Low-Quality: {state['total_discarded_low_quality']} | "
            f"Accepted: {state['total_accepted']} | Time: {exec_time:.2f}s"
        )
        return processed

    def _extract_idea_words(self, idea: str) -> Set[str]:
        return set(w.lower() for w in idea.split() if len(w) > 2 and w.lower() not in STOPWORDS)

    def _parse_url_domain(self, url: str) -> str:
        return urlparse(url).netloc.lower().replace("www.", "")
        
    def _is_valid_item(self, raw_item: RawSearchResult) -> bool:
        return bool(raw_item.url and raw_item.content)

    def _is_explicitly_rejected(self, domain: str, title: str) -> bool:
        title_lower = title.lower()
        if "dictionary" in domain or "meaning" in title_lower or "definition" in title_lower:
            return True
        return False

    def _process_category(
        self, 
        category: str, 
        results: List[Dict[str, Any]], 
        idea_words: Set[str], 
        seen_urls: Set[str], 
        seen_snippets_hashes: Set[str], 
        state: Dict[str, int]
    ) -> Tuple[List[ProcessedSearchResult], int, int]:
        
        processed_list = []
        cat_accepted = 0
        cat_rejected = 0
        cat_kw = CATEGORY_KEYWORDS.get(category, set())
        scorer = RelevanceScorer(idea_words, cat_kw)

        for item_dict in results:
            state["total_raw"] += 1
            raw_item = RawSearchResult(**item_dict)
            
            raw_item.url = raw_item.url.strip()
            raw_item.content = raw_item.content.strip()
            raw_item.title = raw_item.title.strip()
            
            if not self._is_valid_item(raw_item):
                cat_rejected += 1
                state["total_discarded_low_quality"] += 1
                continue

            domain = self._parse_url_domain(raw_item.url)

            # Deduplication
            content_prefix = raw_item.content[:250].lower().strip()
            content_hash = hashlib.sha256(content_prefix.encode("utf-8")).hexdigest()
            
            if raw_item.url in seen_urls or content_hash in seen_snippets_hashes:
                cat_rejected += 1
                state["total_discarded_dupes"] += 1
                continue

            # Quality filters
            if len(raw_item.content) < MIN_CONTENT_LENGTH:
                cat_rejected += 1
                state["total_discarded_low_quality"] += 1
                logger.debug(f"Discarded low-quality snippet from URL: {raw_item.url} (Length: {len(raw_item.content)})")
                continue
                
            if self._is_explicitly_rejected(domain, raw_item.title):
                cat_rejected += 1
                state["total_discarded_low_quality"] += 1
                continue

            # Scoring
            score = scorer.score(raw_item.content, raw_item.title, domain)
            
            # Threshold
            if score < MIN_SCORE_THRESHOLD and len(idea_words) > 0:
                cat_rejected += 1
                state["total_discarded_low_quality"] += 1
                logger.debug(f"Discarded low-relevance snippet: {raw_item.url} (Score: {score})")
                continue

            # Accepted
            seen_urls.add(raw_item.url)
            seen_snippets_hashes.add(content_hash)
            
            state["total_accepted"] += 1
            cat_accepted += 1
            if domain in TRUSTED_DOMAINS:
                state["total_trusted"] += 1
            state["total_relevance"] += score
            
            processed_list.append(ProcessedSearchResult(
                title=raw_item.title,
                url=raw_item.url,
                content=raw_item.content,
                relevance_score=score,
                domain=domain
            ))
            
        processed_list.sort(key=lambda x: x.relevance_score, reverse=True)
        return processed_list, cat_accepted, cat_rejected

    def _update_stats(
        self, 
        state: Dict[str, int], 
        category_stats: Dict[str, Dict[str, int]], 
        total_categories: int, 
        exec_time: float
    ):
        categories_with_results = sum(1 for stat in category_stats.values() if stat["accepted"] > 0)
        
        search_confidence = self.confidence_calculator.calculate(
            total_accepted=state["total_accepted"],
            total_relevance=state["total_relevance"],
            total_trusted=state["total_trusted"],
            categories_with_results=categories_with_results,
            total_categories=total_categories
        )

        stats = ProcessingStats(
            total_raw_results=state["total_raw"],
            total_accepted=state["total_accepted"],
            total_rejected_duplicates=state["total_discarded_dupes"],
            total_rejected_low_quality=state["total_discarded_low_quality"],
            processing_time_seconds=round(exec_time, 3),
            category_statistics=category_stats,
            search_confidence=search_confidence
        )
        
        _processor_stats.set(stats)
