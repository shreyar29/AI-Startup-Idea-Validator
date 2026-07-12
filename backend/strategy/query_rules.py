"""
query_rules.py

Purpose
-------
This module centralizes all configurable rules, constants, and validation
logic used by the Query Strategist. It exists so that categories, keywords,
exclusion rules, and input validation limits live in ONE place, separate
from the orchestration logic in query_strategist.py.

query_strategist.py should never hardcode a category name, a keyword, or a
validation threshold directly. It should import everything it needs from
this module. This keeps query_strategist.py focused purely on the flow of
"call the LLM, parse the response, validate the structure" while this file
owns "what the rules of query generation actually are."

This module contains NO API calls, NO executable/side-effecting code, and
performs NO web search. It only defines rules and pure helper functions that
operate on those rules.
"""

from __future__ import annotations

# ============================================================
# SEARCH CATEGORIES
# ============================================================

# The mandatory categories every generated query set must include.
# These map directly to the category keys the LLM is instructed to
# produce, as defined in query_prompt.py's SYSTEM_PROMPT.
SEARCH_CATEGORIES: tuple[str, ...] = (
    "competitors",
    "market_size",
    "industry_trends",
    "customer_pain_points",
    "funding",
    "recent_news",
)

# Categories that are conditionally included based on the startup's
# industry. Currently only "regulations" — included when the industry is
# one where regulatory/legal/compliance concerns are typically material.
OPTIONAL_CATEGORIES: tuple[str, ...] = (
    "regulations",
)

# Industries for which the "regulations" category should be generated.
# Stored in lowercase for case-insensitive matching in
# is_regulation_required().
REGULATION_SENSITIVE_INDUSTRIES: frozenset[str] = frozenset(
    {
        "healthcare",
        "finance",
        "legal",
        "government",
        "insurance",
        "cybersecurity",
    }
)


# ============================================================
# SEARCH KEYWORDS
# ============================================================

# Commonly used optimization keywords that help generated queries surface
# current, relevant, research-oriented results (rather than generic or
# outdated content). query_strategist.py / query_prompt.py may reference
# these when constructing or reviewing query quality.
SEARCH_KEYWORDS: tuple[str, ...] = (
    "latest",
    "market size",
    "competitors",
    "industry trends",
    "startup",
    "statistics",
    "report",
    "analysis",
    "2026",
    "future",
)


# ============================================================
# EXCLUDED QUERY TYPES
# ============================================================

# Categories of queries the Query Strategist must NEVER generate. These are
# query *intents* that are irrelevant to startup validation research and
# would indicate the LLM has drifted from its assigned role (e.g., producing
# a tutorial search instead of a market research search).
EXCLUDED_QUERY_TYPES: tuple[str, ...] = (
    "definitions",
    "tutorials",
    "wikipedia-style searches",
    "general explanations",
    "how-to guides",
    "programming questions",
    "homework questions",
)


# ============================================================
# VALIDATION RULES
# ============================================================

# Minimum and maximum accepted length (in characters) for a startup idea
# submitted to the Query Strategist. These bounds exist to reject input
# that is too short to be meaningful, or too long to be a reasonable
# startup idea description (as opposed to, e.g., pasted document content).
MIN_STARTUP_IDEA_LENGTH: int = 10
MAX_STARTUP_IDEA_LENGTH: int = 2000


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_regulation_required(industry: str) -> bool:
    """
    Determine whether the "regulations" category should be generated for a
    given industry.

    Args:
        industry: The industry identified for the startup idea (e.g.,
            "Healthcare", "finance", "Cybersecurity").

    Returns:
        True if the industry is regulation-sensitive and the "regulations"
        category should be included; False otherwise.
    """
    if not industry or not industry.strip():
        return False

    normalized_industry = industry.strip().lower()

    # Substring matching (rather than exact equality) so that phrases like
    # "digital healthcare" or "fintech / finance" still correctly trigger
    # regulation-sensitivity, since the LLM's identified industry text may
    # not always be a single bare word.
    return any(
        sensitive_industry in normalized_industry
        for sensitive_industry in REGULATION_SENSITIVE_INDUSTRIES
    )


def get_search_categories(industry: str) -> tuple[str, ...]:
    """
    Build the full list of search categories that should be generated for
    a given industry: the mandatory categories, plus "regulations" if
    applicable.

    Args:
        industry: The industry identified for the startup idea.

    Returns:
        A tuple of category names to generate queries for. Mandatory
        categories always appear first, in their defined order, followed
        by any applicable optional categories.
    """
    categories = list(SEARCH_CATEGORIES)

    if is_regulation_required(industry):
        categories.extend(OPTIONAL_CATEGORIES)

    return tuple(categories)


def validate_startup_idea(text: str) -> None:
    """
    Validate a raw startup idea string against the configured validation
    rules. This is a pure validation function: it raises on invalid input
    and returns None on success, so callers can invoke it as a guard clause.

    Args:
        text: The raw startup idea string to validate.

    Raises:
        ValueError: If the input is empty, whitespace-only, or outside the
            configured length bounds. The message describes exactly which
            rule was violated so calling code (or logs) can surface a
            precise error to the user.
    """
    if text is None:
        raise ValueError("Startup idea must not be None.")

    if not text.strip():
        raise ValueError("Startup idea must not be empty or whitespace-only.")

    stripped_length = len(text.strip())

    if stripped_length < MIN_STARTUP_IDEA_LENGTH:
        raise ValueError(
            f"Startup idea is too short. Minimum length is "
            f"{MIN_STARTUP_IDEA_LENGTH} characters, got {stripped_length}."
        )

    if stripped_length > MAX_STARTUP_IDEA_LENGTH:
        raise ValueError(
            f"Startup idea is too long. Maximum length is "
            f"{MAX_STARTUP_IDEA_LENGTH} characters, got {stripped_length}."
        )
