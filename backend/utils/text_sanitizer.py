import re

def sanitize_queries(queries: list[str]) -> list[str]:
    """
    Sanitize a list of search queries by removing malformed Unicode,
    duplicate words, unnecessary whitespace, and invalid symbols.
    """
    sanitized = []
    for q in queries:
        if not isinstance(q, str):
            continue
            
        # Remove malformed unicode/invalid symbols (keep alphanumeric and basic punctuation)
        q = re.sub(r'[^\w\s\-\.\']', ' ', q)
        
        # Remove extra whitespace
        q = re.sub(r'\s+', ' ', q).strip()
        
        # Remove duplicate words while preserving order
        words = q.split()
        seen = set()
        deduped = []
        for w in words:
            wl = w.lower()
            if wl not in seen:
                seen.add(wl)
                deduped.append(w)
                
        q = ' '.join(deduped)
        if q:
            sanitized.append(q)
            
    return sanitized

def sanitize_category_queries(categorized_queries: dict[str, list[str]]) -> dict[str, list[str]]:
    """Sanitizes queries across all categories."""
    return {
        cat: sanitize_queries(queries)
        for cat, queries in categorized_queries.items()
    }
