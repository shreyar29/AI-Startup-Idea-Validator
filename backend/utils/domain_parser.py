from urllib.parse import urlparse

def extract_domain(url: str) -> str:
    """Extracts the base domain from a given URL."""
    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return url
