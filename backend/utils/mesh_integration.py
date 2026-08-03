"""
mesh_integration.py

Purpose:
Milestone 2 — implements the mesh-integration edge cases documented in
docs/edge_case_analysis_milestone2.md. While error_handler.py (Milestone 1)
handles failures for a single agent talking to one external API, this
module handles failures that only appear once multiple agents talk to
each other through Shared Context and A2A tool calls:

    1. A2A communication failures (tool call fails/times out/malformed)
    2. Shared Context conflicts (missing status, reading before write)
    3. Partial pipeline failures (one of several parallel agents fails)
    4. Per-agent confidence aggregation into a final combined status

Designed to be used by the Comparison Agent (which depends on Market,
Customer, and Competitor Agents all succeeding or partially succeeding)
and by the Orchestrator when coordinating the mesh.
"""

import logging
import time
from functools import wraps

from backend.utils.error_handler import (
    WebSearchAgentError,
    with_retry,
    safe_execute,
)

logger = logging.getLogger("mesh_integration")

REQUIRED_SECTION_KEYS = {
    "market_analysis": ["status"],
    "customer_analysis": ["status"],
    "competitor_analysis": ["status"],
    "comparison_analysis": ["status"],
}

AGENT_WAIT_TIMEOUT_SECONDS = 15
AGENT_WAIT_POLL_INTERVAL = 0.5


# ---------------------------------------------------------------------------
# 1. A2A communication failures
# ---------------------------------------------------------------------------

class A2AToolError(WebSearchAgentError):
    """Raised when an agent-to-agent (A2A) tool call fails outright."""
    pass


class MalformedA2AResponseError(WebSearchAgentError):
    """
    Raised when an A2A tool call succeeds but returns a response that
    doesn't match the shape the calling agent expects (mitigates 1.3 —
    each agent's tools were built somewhat independently).
    """
    pass


@with_retry(retry_on=(A2AToolError,))
def call_agent_tool(tool_func, *args, **kwargs):
    """
    Wraps any A2A tool call (e.g. another agent's get_market_summary())
    with retry logic. Converts unexpected exceptions into A2AToolError so
    the with_retry decorator can catch and retry them consistently,
    regardless of what the target agent's tool raises internally.
    """
    try:
        return tool_func(*args, **kwargs)
    except A2AToolError:
        raise
    except Exception as exc:
        raise A2AToolError(f"A2A call to {tool_func.__name__} failed: {exc}")


def validate_a2a_response(response, expected_keys, tool_name="unknown_tool"):
    """
    Mitigates 1.3 — validates that an A2A tool's response has the
    expected shape before the calling agent uses it. Raises
    MalformedA2AResponseError rather than letting a KeyError/TypeError
    surface deep inside the calling agent's logic.
    """
    if not isinstance(response, dict):
        raise MalformedA2AResponseError(
            f"{tool_name} returned {type(response).__name__}, expected dict"
        )

    missing = [key for key in expected_keys if key not in response]
    if missing:
        raise MalformedA2AResponseError(
            f"{tool_name} response missing expected keys: {missing}"
        )

    return response


def call_agent_tool_safely(tool_func, expected_keys=None, tool_name=None, *args, **kwargs):
    """
    Convenience wrapper combining retry + shape validation + graceful
    degradation. Returns (result, errors) — result is None on failure,
    matching the safe_execute() pattern from Milestone 1.
    """
    tool_name = tool_name or getattr(tool_func, "__name__", "unknown_tool")
    errors = []

    result, call_errors = safe_execute(
        call_agent_tool, tool_func, *args, fallback_errors=[], **kwargs
    )
    errors.extend(call_errors)

    if result is None:
        return None, errors

    if expected_keys:
        try:
            validate_a2a_response(result, expected_keys, tool_name=tool_name)
        except MalformedA2AResponseError as exc:
            logger.warning("Malformed A2A response from %s: %s", tool_name, exc)
            errors.append(f"malformed_a2a_response:{tool_name}:{exc}")
            return None, errors

    return result, errors


# ---------------------------------------------------------------------------
# 2. Shared Context conflicts — ownership + readiness checks
# ---------------------------------------------------------------------------

def write_to_own_section(shared_context, section_name, data, owner_sections=None):
    """
    Mitigates 2.1 — enforces that an agent only writes to its own named
    section of Shared Context, never a shared/global key. Raises if a
    caller tries to write outside its assigned section.
    """
    if owner_sections and section_name not in owner_sections:
        raise ValueError(
            f"Attempted to write to '{section_name}', which is not in "
            f"this agent's allowed sections: {owner_sections}"
        )
    shared_context[section_name] = data
    return shared_context


def is_section_ready(shared_context, section_name):
    """
    Mitigates 2.2 — checks whether a Shared Context section has actually
    finished being written (has a status field), rather than assuming
    presence of the key means it's complete.
    """
    section = shared_context.get(section_name)
    if not section or not isinstance(section, dict):
        return False
    return section.get("status") in ("Success", "Partial Success", "Failed")


def wait_for_sections(shared_context, section_names,
                       timeout=AGENT_WAIT_TIMEOUT_SECONDS,
                       poll_interval=AGENT_WAIT_POLL_INTERVAL):
    """
    Mitigates 3.3 — polls Shared Context until all required sections
    report a status, or until timeout. Returns (all_ready: bool,
    ready_sections: list, missing_sections: list) so the caller (e.g.
    Comparison Agent) can proceed with partial data if some agents
    never finish in time.
    """
    start = time.time()
    while time.time() - start < timeout:
        ready = [s for s in section_names if is_section_ready(shared_context, s)]
        missing = [s for s in section_names if s not in ready]
        if not missing:
            return True, ready, []
        time.sleep(poll_interval)

    ready = [s for s in section_names if is_section_ready(shared_context, s)]
    missing = [s for s in section_names if s not in ready]
    if missing:
        logger.warning(
            "Timed out waiting for sections: %s (ready: %s)", missing, ready
        )
    return (not missing), ready, missing


# ---------------------------------------------------------------------------
# 3 & 4. Partial pipeline failures + confidence aggregation
# ---------------------------------------------------------------------------

def aggregate_pipeline_status(shared_context, section_names):
    """
    Mitigates 3.1 / 3.2 — combines the status of multiple upstream agent
    sections into one overall status + confidence, so a downstream agent
    (e.g. Comparison Agent) never silently presents partial data as if it
    were complete.

    Returns a dict:
        {
            "status": "Success" | "Partial Success" | "Failed",
            "confidence": "high" | "medium" | "low",
            "missing_sections": [...],
            "failed_sections": [...],
        }
    """
    missing_sections = []
    failed_sections = []
    succeeded_sections = []

    for section_name in section_names:
        section = shared_context.get(section_name)
        if not section or not isinstance(section, dict):
            missing_sections.append(section_name)
            continue

        section_status = section.get("status")
        if section_status == "Success":
            succeeded_sections.append(section_name)
        elif section_status == "Partial Success":
            succeeded_sections.append(section_name)
        elif section_status == "Failed":
            failed_sections.append(section_name)
        else:
            missing_sections.append(section_name)

    total = len(section_names)
    succeeded = len(succeeded_sections)

    if succeeded == total:
        status = "Success"
        confidence = "high"
    elif succeeded == 0:
        status = "Failed"
        confidence = "low"
    else:
        status = "Partial Success"
        confidence = "medium" if succeeded >= total / 2 else "low"

    return {
        "status": status,
        "confidence": confidence,
        "missing_sections": missing_sections,
        "failed_sections": failed_sections,
        "succeeded_sections": succeeded_sections,
    }


def build_downstream_input(shared_context, section_names):
    """
    Convenience helper for an agent like Comparison Agent: pulls together
    whatever upstream sections are actually available, plus an aggregated
    status/confidence, so downstream logic never has to guess whether the
    data it's using is complete.
    """
    aggregation = aggregate_pipeline_status(shared_context, section_names)
    available_data = {
        name: shared_context.get(name)
        for name in aggregation["succeeded_sections"]
    }
    return {
        "data": available_data,
        "pipeline_status": aggregation["status"],
        "confidence": aggregation["confidence"],
        "missing_sections": aggregation["missing_sections"],
        "failed_sections": aggregation["failed_sections"],
    }
