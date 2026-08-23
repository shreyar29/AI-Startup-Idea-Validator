from core.config import settings

# Centralize Trusted Domains
TRUSTED_DOMAINS = set(settings.guardrails.trusted_domains_list)
# Merge with previous set to ensure backwards compatibility
PREVIOUS_TRUSTED = {
    "gartner.com", "mckinsey.com", "cbinsights.com", "grandviewresearch.com",
    "statista.com", "crunchbase.com", "techcrunch.com", "ycombinator.com",
    "forbes.com", "bloomberg.com", "reuters.com", "wsj.com", "ft.com"
}
TRUSTED_DOMAINS.update(PREVIOUS_TRUSTED)

# Centralize Keyword Lists
STOPWORDS = {
    'the', 'and', 'for', 'with', 'new', 'this', 'that', 'of', 'in', 'on', 'a', 'an', 
    'to', 'is', 'are', 'app', 'platform', 'software'
}

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

# Scoring Constants
TRUSTED_DOMAIN_BONUS = 5
IDEA_OVERLAP_MULTIPLIER = 2
CATEGORY_OVERLAP_MULTIPLIER = 2
BUSINESS_RELEVANCE_MULTIPLIER = 1
DATA_RICHNESS_BONUS = 3
MIN_SCORE_THRESHOLD = 3
MIN_CONTENT_LENGTH = 40
