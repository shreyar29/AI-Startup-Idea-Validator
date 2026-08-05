"""
Milestone 2 mesh-integration utilities.
"""

import logging
import time
from typing import Any, Callable, Iterable

from backend.utils.error_handler import (
    WebSearchAgentError,
    safe_execute,
    with_retry,
)

logger = logging.getLogger("mesh_integration")

VALID_STATUSES = {"Success", "Partial Success", "Failed"}

# Maps raw status strings actually observed from running agents (lowercase,
# inconsistent casing) to the canonical internal statuses this module uses.
# NOTE: "started" is currently mapped to "Partial Success" as a conservative
# default — it was observed on agents that had already finished executing
# (agent_metrics showed an end_time) but never updated their own status
# field to a terminal value. This is a guess, not a confirmed design
# decision — flag to the team whether "started" should mean "still running
# / not ready" instead, and fix at the source (the agent itself) rather
# than relying on this mapping long-term.
STATUS_ALIASES = {
    "success": "Success",
    "partial success": "Partial Success",
    "partial_success": "Partial Success",
    "failed": "Failed",
    "failure": "Failed",
    "started": "Partial Success",  # see note above — needs team confirmation
}


def normalize_status(raw_status) -> str | None:
    """
    Normalize a raw status string (any casing, from any agent) into one of
    the three canonical internal statuses. Returns None if the status is
    unrecognized, so callers can treat it as "missing" rather than guessing.
    """
    if not isinstance(raw_status, str):
        return None
    return STATUS_ALIASES.get(raw_status.strip().lower())


AGENT_WAIT_TIMEOUT_SECONDS = 15
AGENT_WAIT_POLL_INTERVAL = 0.5


class A2AToolError(WebSearchAgentError):
    """Raised when an agent-to-agent tool call fails."""


class MalformedA2AResponseError(WebSearchAgentError):
    """Raised when an A2A tool returns an unexpected response shape."""


@with_retry(retry_on=(A2AToolError,))
def call_agent_tool(tool_func: Callable, *args, **kwargs):
    try:
        return tool_func(*args, **kwargs)
    except A2AToolError:
        raise
    except Exception as exc:
        tool_name = getattr(tool_func, "__name__", "unknown_tool")
        raise A2AToolError(f"A2A call to {tool_name} failed: {exc}") from exc


def validate_a2a_response(response: Any, expected_keys: Iterable[str], tool_name: str = "unknown_tool") -> dict:
    if not isinstance(response, dict):
        raise MalformedA2AResponseError(
            f"{tool_name} returned {type(response).__name__}; expected dict"
        )
    missing_keys = [key for key in expected_keys if key not in response]
    if missing_keys:
        raise MalformedA2AResponseError(
            f"{tool_name} response missing expected keys: {missing_keys}"
        )
    return response


def call_agent_tool_safely(
    tool_func: Callable,
    *args,
    expected_keys: Iterable[str] | None = None,
    tool_name: str | None = None,
    **kwargs,
):
    resolved_name = tool_name or getattr(tool_func, "__name__", "unknown_tool")
    result, errors = safe_execute(call_agent_tool, tool_func, *args, fallback_errors=[], **kwargs)
    if result is None:
        return None, errors
    if expected_keys:
        try:
            validate_a2a_response(result, expected_keys, tool_name=resolved_name)
        except MalformedA2AResponseError as exc:
            logger.warning("Malformed A2A response from %s: %s", resolved_name, exc)
            errors.append(f"malformed_a2a_response:{resolved_name}:{exc}")
            return None, errors
    return result, errors


def write_to_own_section(
    shared_context: dict,
    section_name: str,
    data: dict,
    owner_sections: Iterable[str] | None = None,
) -> dict:
    if owner_sections is not None:
        allowed_sections = set(owner_sections)
        if section_name not in allowed_sections:
            raise ValueError(
                f"Attempted to write to '{section_name}'. Allowed sections: {sorted(allowed_sections)}"
            )
    shared_context[section_name] = data
    return shared_context


def is_section_ready(shared_context: dict, section_name: str) -> bool:
    section = shared_context.get(section_name)
    if not isinstance(section, dict):
        return False
    return normalize_status(section.get("status")) in VALID_STATUSES


def wait_for_sections(
    shared_context: dict,
    section_names: Iterable[str],
    timeout: float = AGENT_WAIT_TIMEOUT_SECONDS,
    poll_interval: float = AGENT_WAIT_POLL_INTERVAL,
):
    names = list(section_names)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        ready = [name for name in names if is_section_ready(shared_context, name)]
        missing = [name for name in names if name not in ready]
        if not missing:
            return True, ready, []
        time.sleep(poll_interval)
    ready = [name for name in names if is_section_ready(shared_context, name)]
    missing = [name for name in names if name not in ready]
    if missing:
        logger.warning("Timed out waiting for sections: %s (ready: %s)", missing, ready)
    return not missing, ready, missing


def aggregate_pipeline_status(shared_context: dict, section_names: Iterable[str]) -> dict:
    names = list(section_names)
    succeeded_sections = []
    partial_sections = []
    failed_sections = []
    missing_sections = []

    for section_name in names:
        section = shared_context.get(section_name)
        if not isinstance(section, dict):
            missing_sections.append(section_name)
            continue
        status = normalize_status(section.get("status"))
        if status == "Success":
            succeeded_sections.append(section_name)
        elif status == "Partial Success":
            partial_sections.append(section_name)
        elif status == "Failed":
            failed_sections.append(section_name)
        else:
            missing_sections.append(section_name)

    total = len(names)
    usable_count = len(succeeded_sections) + len(partial_sections)

    if total > 0 and len(succeeded_sections) == total:
        overall_status = "Success"
        confidence = "high"
    elif usable_count == 0:
        overall_status = "Failed"
        confidence = "low"
    else:
        overall_status = "Partial Success"
        effective_coverage = (
            len(succeeded_sections) + (0.5 * len(partial_sections))
        ) / total if total else 0
        confidence = "medium" if effective_coverage >= 0.5 else "low"

    return {
        "status": overall_status,
        "confidence": confidence,
        "succeeded_sections": succeeded_sections,
        "partial_sections": partial_sections,
        "failed_sections": failed_sections,
        "missing_sections": missing_sections,
    }


def build_downstream_input(shared_context: dict, section_names: Iterable[str]) -> dict:
    aggregation = aggregate_pipeline_status(shared_context, section_names)
    usable_sections = aggregation["succeeded_sections"] + aggregation["partial_sections"]
    available_data = {name: shared_context[name] for name in usable_sections if name in shared_context}
    return {
        "data": available_data,
        "pipeline_status": aggregation["status"],
        "confidence": aggregation["confidence"],
        "succeeded_sections": aggregation["succeeded_sections"],
        "partial_sections": aggregation["partial_sections"],
        "failed_sections": aggregation["failed_sections"],
        "missing_sections": aggregation["missing_sections"],
    }