"""
Milestone 2 response-integrity validator.

Implements the runtime mitigation for the false-success case where /search
can otherwise appear successful even though the Web Search Agent returned no
meaningful research data.

This module intentionally does NOT:
- call Tavily or OpenRouter,
- retry Query Strategist,
- change agent orchestration,
- handle the 120-second Web Search timeout.

Those responsibilities belong to the Web Search/orchestration layer.
"""

from datetime import datetime, timezone
from typing import Any

VALID_PIPELINE_STATUSES = {"Success", "Partial Success", "Failed"}


def has_meaningful_data(search_results: Any) -> bool:
    """
    Return True only when a search-results dictionary contains usable data.

    Empty dictionaries/lists, None, and blank strings do not count as
    meaningful research.
    """
    if not isinstance(search_results, dict) or not search_results:
        return False

    for value in search_results.values():
        if isinstance(value, str):
            if value.strip():
                return True

        elif isinstance(value, (list, tuple, set, dict)):
            if len(value) > 0:
                return True

        elif value is not None:
            return True

    return False


def build_pipeline_metadata(
    startup_idea: str,
    status: str,
    execution_time_seconds: float | None = None,
    no_data_found: bool = False,
    extra: dict | None = None,
) -> dict:
    """
    Build consistent pipeline metadata using the canonical internal statuses:
    Success, Partial Success, and Failed.
    """
    if status not in VALID_PIPELINE_STATUSES:
        raise ValueError(
            f"Invalid pipeline status '{status}'. "
            f"Expected one of {sorted(VALID_PIPELINE_STATUSES)}."
        )

    metadata: dict[str, Any] = {
        "startup_idea": startup_idea,
        "status": status,
        "no_data_found": no_data_found,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if execution_time_seconds is not None:
        metadata["execution_time_seconds"] = execution_time_seconds

    if extra:
        metadata.update(extra)

    return metadata


def _extract_web_search_results(pipeline_output: dict) -> dict:
    """
    Extract Web Search results from the currently observed response shapes.
    """
    web_section = pipeline_output.get("web_search_agent")

    if not isinstance(web_section, dict):
        agents = pipeline_output.get("agents", {})

        if isinstance(agents, dict):
            web_section = (
                agents.get("Web Search Agent")
                or agents.get("web_search_agent")
            )

    if not isinstance(web_section, dict):
        return {}

    search_results = web_section.get("search_results", {})

    return (
        search_results
        if isinstance(search_results, dict)
        else {}
    )


def validate_and_annotate_pipeline_output(
    pipeline_output: dict,
) -> dict:
    """
    Final defensive check before returning the /search response.

    If Web Search contains no meaningful data:
    - metadata.status becomes Failed
    - metadata.no_data_found becomes True

    Existing downstream data is left intact for debugging and observability.
    """
    if not isinstance(pipeline_output, dict):
        raise TypeError("pipeline_output must be a dict")

    search_results = _extract_web_search_results(
        pipeline_output
    )

    if not has_meaningful_data(search_results):
        metadata = pipeline_output.setdefault(
            "metadata",
            {},
        )
        metadata["status"] = "Failed"
        metadata["no_data_found"] = True

    return pipeline_output