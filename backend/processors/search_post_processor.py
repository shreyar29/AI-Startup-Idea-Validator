import logging
from typing import Any, Dict, List, Tuple, Set
from utils.domain_parser import extract_domain
from core.config import settings

logger = logging.getLogger(__name__)

_TRUSTED_DOMAINS = settings.guardrails.trusted_domains_list

class SearchPostProcessor:
    """
    Handles filtering, ranking, domain deduplication, and trusted-source analysis 
    for search results after they have been processed by the main ResultProcessor.
    """
    def filter_and_rank_results(
        self, processed_results: Dict[str, List[Dict[str, Any]]]
    ) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Any]]:
        refined_results = {}
        category_metadata = {}
        
        for category, results in processed_results.items():
            results_found = len(results)
            
            valid_results = []
            for r in results:
                url = str(r.get("url") or "")
                content = str(r.get("content") or "")
                
                # Filter out missing URL or empty content
                if not url.strip() or not content.strip():
                    continue
                    
                # Filter out extremely short content
                if len(content.strip()) < 40:
                    continue
                    
                # Do not filter out by relevance, just use it for sorting
                try:
                    relevance_score = float(r.get("relevance_score", r.get("score", 0.0)))
                except (ValueError, TypeError):
                    relevance_score = 0.0
                
                valid_results.append((relevance_score, r))
                
            # Sort by relevance descending
            valid_results.sort(key=lambda x: x[0], reverse=True)
            
            # Deduplicate domains and keep top 5
            final_cat_results = []
            seen_domains: Set[str] = set()
            trusted_count = 0
            
            for score, r in valid_results:
                url = r.get("url", "")
                domain = extract_domain(url)
                    
                if domain in seen_domains:
                    continue
                    
                seen_domains.add(domain)
                final_cat_results.append(r)
                
                if any(td in domain for td in _TRUSTED_DOMAINS):
                    trusted_count += 1
                
                if len(final_cat_results) >= 5:
                    break
                    
            # Never Return Empty Results if original had data
            fallback_used = False
            if len(final_cat_results) == 0 and results_found > 0:
                fallback_used = True
                final_cat_results = results  # Fallback to original results
                # Compute trusted sources for metadata accurately
                for r in final_cat_results:
                    domain = extract_domain(str(r.get("url", "")))
                    if any(td in domain for td in _TRUSTED_DOMAINS):
                        trusted_count += 1
                        
            logger.info(f"Category '{category}' | Original: {results_found} | After filtering: {len(final_cat_results)} | Fallback used: {fallback_used}")
                    
            refined_results[category] = final_cat_results
            category_metadata[category] = {
                "results_found": results_found,
                "results_kept": len(final_cat_results),
                "trusted_sources": trusted_count,
                "fallback_used": fallback_used
            }
            
        return refined_results, category_metadata
