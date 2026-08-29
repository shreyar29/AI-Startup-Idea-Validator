from typing import Set
from processors.constants import (
    TRUSTED_DOMAIN_BONUS,
    IDEA_OVERLAP_MULTIPLIER,
    CATEGORY_OVERLAP_MULTIPLIER,
    BUSINESS_RELEVANCE_MULTIPLIER,
    DATA_RICHNESS_BONUS,
    BUSINESS_KEYWORDS,
    TRUSTED_DOMAINS
)


class RelevanceScorer:
    """Component responsible for scoring the relevance of search results."""
    
    def __init__(self, idea_words: Set[str], category_keywords: Set[str]):
        self.idea_words = idea_words
        self.category_keywords = category_keywords

    def score(self, content: str, title: str, domain: str) -> int:
        """
        Calculates a relevance score based on domain trust, keyword overlap, 
        and data richness.
        """
        score = 0
        content_lower = content.lower()
        title_lower = title.lower()

        # Trusted Source Bonus
        is_trusted = domain in TRUSTED_DOMAINS
        if is_trusted:
            score += TRUSTED_DOMAIN_BONUS
            
        # Idea Relevance
        overlap = sum(1 for w in self.idea_words if w in content_lower or w in title_lower)
        score += (overlap * IDEA_OVERLAP_MULTIPLIER)
        
        # Category Relevance
        cat_overlap = sum(1 for w in self.category_keywords if w in content_lower or w in title_lower)
        score += (cat_overlap * CATEGORY_OVERLAP_MULTIPLIER)
        
        # Business Relevance
        bus_overlap = sum(1 for w in BUSINESS_KEYWORDS if w in content_lower or w in title_lower)
        score += (bus_overlap * BUSINESS_RELEVANCE_MULTIPLIER)
        
        # Data Richness (Numbers, $, % often indicate good research)
        if any(char.isdigit() or char in {'$', '%'} for char in content):
            score += DATA_RICHNESS_BONUS
            
        return score
