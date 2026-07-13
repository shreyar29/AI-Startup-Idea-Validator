"""
error_handler.py
Owner: Neha (Edge Case Analyst)

Purpose:
Centralized error-handling and edge-case mitigation utilities for the
Web Search Agent pipeline (Query Strategist -> Web Search Agent -> Tavily API
-> Market Analysis Agent).

This module implements the mitigations documented in docs/edge_case_analysis.md:
    1. API / infrastructure failures      (timeouts, rate limits, LLM failures)
    2. Bad or empty results                (zero results, spam, duplicates)
    3. Input problems                      (vague ideas, non-English markets)
    4. Cost / scope control                (query caps, unnecessary searches)
    5. Data quality / trust                (stale sources, unreliable sources,conflicting data)

It is designed to be imported by backend/agents/web_search_agent.py and used
around every Tavily API call and around the final response assembly, so that
failures never crash the pipeline and always degrade gracefully into the
agreed output schema (status / errors / confidence / stale /
no_market_data_found / conflicting_data).
"""

import time
import random
import logging
from functools import wraps
from datetime import datetime, timezone

logger = logging.getLogger("web_search_agent.error_handler")
logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------------------------
# 1. Custom exceptions
# ---------------------------------------------------------------------------

class WebSearchAgentError(Exception):
    """Base exception for all Web Search Agent errors."""
    pass


class SearchAPIError(WebSearchAgentError):
    """Raised when the Tavily (or fallback) search API call fails outright."""
    pass


class RateLimitError(WebSearchAgentError):
    """Raised when the search API responds with a rate-limit signal."""
    pass


class LLMCallError(WebSearchAgentError):
    """Raised when an OpenRouter / LLM call (e.g. query decomposition) fails."""
    pass


class MalformedLLMOutputError(WebSearchAgentError):
    """
    Raised when an LLM call succeeds (no network/API error) but returns
    output that can't be parsed into the expected structure — e.g. during
    structured startup-idea extraction or query decomposition. Distinct
    from LLMCallError: the call didn't fail, the *content* is unusable.
    """
    pass


class QueryCapExceededError(WebSearchAgentError):
    """Raised internally when a caller tries to exceed the max query cap."""
    pass


# ---------------------------------------------------------------------------
# 2. Config constants (tune these centrally rather than scattering magic
#    numbers across the codebase)
# ---------------------------------------------------------------------------

MAX_QUERIES_PER_REQUEST = 5        # mitigates 4.1 (query explosion)
MAX_RETRIES = 2                    # mitigates 1.1 / 1.2 / 1.3
BASE_BACKOFF_SECONDS = 1.5         # exponential backoff base
REQUEST_TIMEOUT_SECONDS = 10       # mitigates 1.1

# Terms that should NEVER trigger a search (mitigates 4.2).
# Extend this list as the Query Strategist identifies more "don't search" cases.
NO_SEARCH_KEYWORDS = {
    "definition", "define", "what is", "meaning of",
}

# Source domains considered authoritative for weighting (mitigates 5.2).
TRUSTED_DOMAINS = {
    "crunchbase.com", "techcrunch.com", "reuters.com", "bloomberg.com",
    "forbes.com", "statista.com", "gartner.com",
}


# ---------------------------------------------------------------------------
# 3. Retry / backoff decorator (mitigates 1.1, 1.2, 1.3)
# ---------------------------------------------------------------------------

def with_retry(max_retries=MAX_RETRIES, base_backoff=BASE_BACKOFF_SECONDS,
                retry_on=(SearchAPIError, RateLimitError, LLMCallError)):
    """
    Decorator that retries a function call on transient failures with
    exponential backoff + jitter. After exhausting retries, re-raises the
    last exception so the caller can decide on a fallback.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as exc:
                    last_exc = exc
                    if attempt == max_retries:
                        logger.warning(
                            "%s failed after %d attempts: %s",
                            func.__name__, attempt + 1, exc
                        )
                        raise
                    sleep_time = base_backoff * (2 ** attempt) + random.uniform(0, 0.5)
                    logger.info(
                        "%s failed (attempt %d/%d): %s. Retrying in %.1fs...",
                        func.__name__, attempt + 1, max_retries + 1, exc, sleep_time
                    )
                    time.sleep(sleep_time)
            raise last_exc
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# 4. Query-level safeguards (mitigates 3.1, 3.2, 4.1, 4.2)
# ---------------------------------------------------------------------------

def enforce_query_cap(queries):
    """
    Enforces MAX_QUERIES_PER_REQUEST. If the Query Strategist's decomposition
    layer returns too many queries, keep only the highest-priority ones
    (mitigates 4.1). Expects queries as a list of dicts with at least
    {"query": str, "priority": int} — falls back to input order if
    priority is missing.
    """
    if len(queries) <= MAX_QUERIES_PER_REQUEST:
        return queries

    logger.info(
        "Query cap exceeded (%d received, max %d). Trimming to top priority.",
        len(queries), MAX_QUERIES_PER_REQUEST
    )
    sorted_queries = sorted(
        queries, key=lambda q: q.get("priority", 999)
    )
    return sorted_queries[:MAX_QUERIES_PER_REQUEST]


def should_skip_search(query_text):
    """
    Returns True if a query should NOT be sent to the search API at all
    (mitigates 4.2 — cost control / avoiding unnecessary searches).
    Basic keyword check; extend with the Query Strategist's exclusion rules.
    """
    lowered = query_text.lower()
    return any(keyword in lowered for keyword in NO_SEARCH_KEYWORDS)


def flag_low_confidence_if_vague(startup_idea, min_word_count=4):
    """
    Mitigates 3.1 (vague startup idea). Returns True if the idea is too
    short/generic to produce targeted queries, signaling downstream that
    confidence should be set to "low".
    """
    word_count = len(startup_idea.strip().split())
    return word_count < min_word_count


def safe_parse_llm_json(raw_text, required_keys=None):
    """
    Mitigates malformed LLM output during structured extraction (e.g. the
    Query Strategist converting a startup idea into structured queries, or
    an LLM-based idea-extraction step). The LLM call itself may succeed but
    still return invalid JSON, or valid JSON missing expected fields.

    Strips common Markdown code-fence wrapping, parses JSON, and validates
    that required_keys are present. Raises MalformedLLMOutputError on any
    failure so the caller can retry with a stricter prompt or fall back
    to a default/partial structure instead of crashing.
    """
    import json

    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError) as exc:
        raise MalformedLLMOutputError(f"Could not parse LLM output as JSON: {exc}")

    if required_keys:
        missing = [key for key in required_keys if key not in parsed]
        if missing:
            raise MalformedLLMOutputError(
                f"LLM output missing required keys: {missing}"
            )

    return parsed


def resolve_search_language(geography, default="en"):
    """
    Mitigates 3.2 (non-English market). Placeholder policy: search in
    English first; callers can use the returned language hint to decide
    whether to re-run queries in the local language if results are thin.
    Extend this mapping as more markets are supported.
    """
    geography_language_map = {
        "japan": "ja",
        "france": "fr",
        "germany": "de",
        "china": "zh",
        "brazil": "pt",
    }
    return geography_language_map.get((geography or "").strip().lower(), default)


# ---------------------------------------------------------------------------
# 5. Result-level safeguards (mitigates 2.1, 2.2, 2.3, 5.1, 5.2, 5.3)
# ---------------------------------------------------------------------------

def broaden_query(query_text):
    """
    Mitigates 2.1 (zero results). Strips overly specific modifiers so a
    niche query can be retried more broadly. Simple heuristic: drop
    trailing qualifier clauses after commas/parentheses and quoted phrases.
    """
    broadened = query_text.split(",")[0]
    broadened = broadened.split("(")[0]
    return broadened.strip()


def dedupe_results(results, key="url"):
    """
    Mitigates 2.3 (duplicate sources). Deduplicates by URL/domain, keeping
    the first (assumed highest-ranked) occurrence.
    """
    seen = set()
    deduped = []
    for result in results:
        identifier = result.get(key, "")
        domain = identifier.split("//")[-1].split("/")[0] if identifier else identifier
        if domain and domain not in seen:
            seen.add(domain)
            deduped.append(result)
    return deduped


def is_stale(published_date_str, max_age_days=365):
    """
    Mitigates 5.1 (outdated source). Returns True if a result's published
    date is missing or older than max_age_days — callers should deprioritize
    or flag these when recency matters (market size, funding, "current"
    competitors).
    """
    if not published_date_str:
        return True
    try:
        published = datetime.fromisoformat(published_date_str.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - published).days
        return age_days > max_age_days
    except (ValueError, TypeError):
        return True


def is_trusted_source(url):
    """
    Mitigates 5.2 (unreliable source). Returns True if the URL's domain is
    in the curated TRUSTED_DOMAINS set. Used to weight/rank results, not
    to exclude untrusted ones outright.
    """
    if not url:
        return False
    domain = url.split("//")[-1].split("/")[0].replace("www.", "")
    return domain in TRUSTED_DOMAINS


def detect_conflicting_data(results, field="value"):
    """
    Mitigates 5.3 (conflicting data). Given a list of extracted data points
    (e.g. market size figures) from different sources, returns True if
    they disagree meaningfully, along with the distinct values found.
    Expects results as a list of dicts like {"source": str, "value": ...}.
    """
    values = {r.get(field) for r in results if r.get(field) is not None}
    return len(values) > 1, list(values)


# ---------------------------------------------------------------------------
# 6. Response assembly helpers — build the agreed output schema fields
#    (status, errors, confidence, stale, no_market_data_found,
#    conflicting_data) so edge cases are surfaced, never silently swallowed.
# ---------------------------------------------------------------------------

def build_response(request_id, search_results, errors=None,
                    confidence="high", stale=False,
                    no_market_data_found=False, conflicting_data=False):
    """
    Assembles the final response object passed to the Market Analysis Agent.
    Ensures every edge-case flag is always present in the output, even when
    everything succeeded (defaults reflect the "happy path").
    """
    errors = errors or []

    if no_market_data_found or not search_results:
        status = "Failed" if errors else "Partial Success"
    elif errors:
        status = "Partial Success"
    else:
        status = "Success"

    return {
        "request_id": request_id,
        "status": status,
        "total_results": len(search_results),
        "search_results": search_results,
        "errors": errors,
        "confidence": confidence,
        "stale": stale,
        "no_market_data_found": no_market_data_found,
        "conflicting_data": conflicting_data,
    }


def safe_execute(func, *args, fallback_errors=None, **kwargs):
    """
    Generic safe-execution wrapper for any pipeline step. Catches known
    WebSearchAgentError subclasses (after retries have already been
    exhausted by @with_retry) and converts them into a structured error
    entry instead of letting an exception propagate and crash the pipeline.

    Returns (result, errors) where result is None on failure.
    """
    errors = fallback_errors or []
    try:
        return func(*args, **kwargs), errors
    except RateLimitError as exc:
        logger.error("Rate limit error in %s: %s", func.__name__, exc)
        errors.append(f"rate_limit_exceeded: {exc}")
        return None, errors
    except SearchAPIError as exc:
        logger.error("Search API error in %s: %s", func.__name__, exc)
        errors.append(f"search_api_failed: {exc}")
        return None, errors
    except LLMCallError as exc:
        logger.error("LLM call error in %s: %s", func.__name__, exc)
        errors.append(f"llm_call_failed: {exc}")
        return None, errors
    except Exception as exc:  # noqa: BLE001 - last-resort catch-all
        logger.exception("Unexpected error in %s", func.__name__)
        errors.append(f"unexpected_error: {exc}")
        return None, errors