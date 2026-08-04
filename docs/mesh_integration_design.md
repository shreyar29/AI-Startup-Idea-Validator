# Mesh Integration Utilities --- Design Document

**Project:** AI Startup Idea Validator\
**Milestone:** 2 --- Agent Mesh Integration\
**Implementation Files:** `backend/utils/mesh_integration.py`,
`backend/utils/response_validator.py`\
**Related Analysis:** `docs/edge_case_analysis_milestone2_2.md`

------------------------------------------------------------------------

## 1. Purpose

Milestone 2 introduces failures that do not exist in a single-agent
pipeline. Market, Customer, Competitor, and Comparison agents may
complete at different times, return incompatible data, fail
independently, or read/write Shared Context incorrectly.

The Milestone 2 utility layer is divided into two focused modules.

  -----------------------------------------------------------------------
  Module                              Primary Responsibility
  ----------------------------------- -----------------------------------
  `mesh_integration.py`               Protect A2A calls, Shared Context
                                      access, and multi-agent status
                                      aggregation

  `response_validator.py`             Prevent empty Web Search output
                                      from being presented as a
                                      successful `/search` run
  -----------------------------------------------------------------------

Keeping these concerns separate prevents one large error-handling module
from becoming responsible for unrelated pipeline stages.

------------------------------------------------------------------------

## 2. Architecture Overview

``` text
                         ┌──────────────────────┐
                         │   Web Search Agent   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Response validation  │
                         │ meaningful data?     │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
             ┌────────────┐  ┌─────────────┐  ┌──────────────┐
             │Market Agent│  │Customer Agent│  │Competitor Ag.│
             └─────┬──────┘  └──────┬──────┘  └──────┬───────┘
                   │                │                │
                   └──────────── Shared Context ────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ mesh_integration.py  │
                         │ status + readiness   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Comparison Agent    │
                         └──────────────────────┘
```

------------------------------------------------------------------------

## 3. Canonical Status Contract

The internal mesh utilities use exactly three terminal statuses.

  -----------------------------------------------------------------------
  Status                              Definition
  ----------------------------------- -----------------------------------
  `Success`                           Complete usable agent output

  `Partial Success`                   Usable output exists, but it is
                                      incomplete/degraded

  `Failed`                            No usable output
  -----------------------------------------------------------------------

### Critical Rule

`Partial Success` is **not** equivalent to `Success`.

Overall `Success` is allowed only when **every required upstream section
is fully successful**.

------------------------------------------------------------------------

## 4. `mesh_integration.py` API

### 4.1 `call_agent_tool()`

**Purpose:** Wrap a synchronous A2A call with the existing Milestone 1
retry mechanism.

**Behaviour**

  -----------------------------------------------------------------------
  Condition                           Result
  ----------------------------------- -----------------------------------
  Peer returns normally               Return peer response

  Peer raises `A2AToolError`          Retry according to `with_retry()`

  Peer raises another exception       Convert it to `A2AToolError`, then
                                      apply retry policy

  Retries exhausted                   Exception reaches `safe_execute()`
                                      when called through the safe
                                      wrapper
  -----------------------------------------------------------------------

------------------------------------------------------------------------

### 4.2 `validate_a2a_response()`

**Purpose:** Stop malformed peer responses before they cause unrelated
`KeyError`/`TypeError` failures downstream.

Validation rules:

1.  Response must be a `dict`.
2.  Every caller-specified required key must exist.

Example:

``` python
validate_a2a_response(
    response,
    expected_keys=["summary", "growth_rate"],
    tool_name="get_market_summary",
)
```

------------------------------------------------------------------------

### 4.3 `call_agent_tool_safely()`

**Purpose:** Recommended entry point for synchronous A2A tool calls.

It combines:

``` text
A2A call
   ↓
retry
   ↓
safe execution
   ↓
shape validation
   ↓
(result, errors)
```

Example:

``` python
result, errors = call_agent_tool_safely(
    market_agent.get_market_summary,
    expected_keys=["summary", "growth_rate"],
    tool_name="get_market_summary",
)

if result is None:
    # Mark Market data unavailable and continue only if partial execution
    # is allowed by the orchestrator.
    ...
```

------------------------------------------------------------------------

### 4.4 `write_to_own_section()`

**Purpose:** Enforce Shared Context ownership.

Example:

``` python
write_to_own_section(
    shared_context,
    "competitor_analysis",
    analysis_result,
    owner_sections=["competitor_analysis"],
)
```

Attempting to write to an unowned section raises `ValueError`.

------------------------------------------------------------------------

### 4.5 `is_section_ready()`

A section is ready only when:

``` text
section exists
AND
section is a dictionary
AND
status ∈ {Success, Partial Success, Failed}
```

This is safer than checking only whether a key exists.

------------------------------------------------------------------------

### 4.6 `wait_for_sections()`

**Purpose:** Prevent indefinite waiting for upstream agents.

Returns:

``` python
(
    all_ready,
    ready_sections,
    missing_sections,
)
```

Default configuration:

  Setting                 Value
  --------------- -------------
  Wait timeout       15 seconds
  Poll interval     0.5 seconds

> This implementation is synchronous. It should not be used to block an
> async event loop.

------------------------------------------------------------------------

### 4.7 `aggregate_pipeline_status()`

This function separates upstream sections into four groups:

  Group                  Meaning
  ---------------------- ------------------------------------------
  `succeeded_sections`   Fully successful
  `partial_sections`     Usable but degraded
  `failed_sections`      Explicit failure
  `missing_sections`     Missing or no recognized terminal status

Aggregation rules:

  -----------------------------------------------------------------------
  Condition               Overall Status          Confidence
  ----------------------- ----------------------- -----------------------
  Every required section  `Success`               High
  is `Success`                                    

  No Success/Partial      `Failed`                Low
  Success section exists                          

  Otherwise               `Partial Success`       Medium or Low based on
                                                  effective coverage
  -----------------------------------------------------------------------

Partial sections receive reduced weight when calculating confidence.

------------------------------------------------------------------------

### 4.8 `build_downstream_input()`

**Purpose:** Prepare safe input for Comparison Agent.

Output structure:

``` python
{
    "data": {
        # Success and Partial Success sections only
    },
    "pipeline_status": "Partial Success",
    "confidence": "medium",
    "succeeded_sections": [...],
    "partial_sections": [...],
    "failed_sections": [...],
    "missing_sections": [...],
}
```

This allows Comparison Agent to use partial evidence without pretending
that the evidence is complete.

------------------------------------------------------------------------

## 5. `response_validator.py` API

### 5.1 `has_meaningful_data()`

Checks whether Web Search output contains at least one non-empty usable
value.

  Value                    Meaningful?
  ------------------------ -------------
  `[]`                     No
  `{}`                     No
  `""` / whitespace        No
  `None`                   No
  Non-empty list           Yes
  Non-empty dict           Yes
  Non-empty string         Yes
  Other non-`None` value   Yes

------------------------------------------------------------------------

### 5.2 `build_pipeline_metadata()`

Creates consistent metadata and validates the requested status.

Example:

``` python
metadata = build_pipeline_metadata(
    startup_idea=idea,
    status="Failed",
    no_data_found=True,
)
```

------------------------------------------------------------------------

### 5.3 `validate_and_annotate_pipeline_output()`

This is the final defensive guard for runtime finding RT-04.

``` text
assembled /search response
        ↓
extract Web Search results
        ↓
meaningful data?
      /     \
    yes      no
    │         │
 return    metadata.status = Failed
          no_data_found = true
```

The function preserves existing output for debugging while correcting
misleading metadata.

------------------------------------------------------------------------

## 6. Recommended Integration Points

  ---------------------------------------------------------------------------------------------
  Pipeline Point          Utility                                     Why
  ----------------------- ------------------------------------------- -------------------------
  Immediately after Web   `has_meaningful_data()`                     Avoid starting downstream
  Search                                                              agents with empty
                                                                      research

  Before returning        `validate_and_annotate_pipeline_output()`   Final protection against
  `/search`                                                           false success

  Before consuming a peer `call_agent_tool_safely()`                  Retry + validation +
  A2A response                                                        graceful degradation

  When writing agent      `write_to_own_section()`                    Enforce section ownership
  output                                                              

  Before Comparison Agent `wait_for_sections()`                       Bound waiting for
  starts                                                              upstream completion

  When constructing       `build_downstream_input()`                  Carry
  Comparison input                                                    completeness/confidence
                                                                      into final comparison
  ---------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 7. Query Strategist Timeout --- Scope Boundary

The runtime-verified Query Strategist timeout is **not** a
`mesh_integration.py` problem.

Observed sequence:

``` text
Query Strategist
    ↓
OpenRouter response
    ↓
malformed/incomplete structured output
    ↓
retry
    ↓
another invalid response
    ↓
retry
    ↓
120-second Web Search timeout
    ↓
OpenRouter request cancelled
```

The appropriate fix belongs in Query Strategist/Web Search
orchestration.

### Recommended principles

  -----------------------------------------------------------------------
  Principle                           Reason
  ----------------------------------- -----------------------------------
  Per-attempt LLM timeout             One attempt must not consume the
                                      entire outer budget

  Overall deadline awareness          Do not start a retry that cannot
                                      finish before the outer timeout

  Structured-output validation        Detect incomplete responses
                                      immediately

  Corrective retry prompt             Tell the model exactly what
                                      validation failed

  Fail fast on 401/config errors      Permanent errors cannot recover
                                      through retry

  Retry transient failures only       Timeouts, 429, and selected 5xx
                                      failures may recover

  Test approved fixed model           Avoid attributing router/model
                                      variability to application logic
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 8. Dependencies

`mesh_integration.py` depends on the following existing names from
`backend/utils/error_handler.py`:

  Dependency              Purpose
  ----------------------- ---------------------------------------------------
  `WebSearchAgentError`   Base exception
  `with_retry()`          Existing retry/backoff policy
  `safe_execute()`        Convert exhausted failures into structured errors

Before merging, confirm those names exist on the target integration
branch.

`response_validator.py` has no dependency on agent classes.

------------------------------------------------------------------------

## 9. Known Limitations

  -----------------------------------------------------------------------
  Limitation              Impact                  Future Improvement
  ----------------------- ----------------------- -----------------------
  `wait_for_sections()`   Blocks the current      Add an async variant if
  uses `time.sleep()`     thread                  orchestration becomes
                                                  fully async

  `call_agent_tool()`     Cannot directly await   Handle async peer calls
  targets synchronous     async peer methods      in the async
  functions                                       orchestrator or create
                                                  a separate async
                                                  utility

  Status strings are      Mixed casing can be     Normalize statuses at
  exact                   treated as missing      API/integration
                                                  boundaries

  Utility functions are   Adding the files alone  Integrate them
  not automatically wired does not change runtime explicitly at the
                          behaviour               pipeline points listed
                                                  above
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 10. Acceptance Criteria

Milestone 2 integration handling is considered correct when all of the
following hold:

  -----------------------------------------------------------------------
  \#                                  Acceptance Criterion
  ----------------------------------- -----------------------------------
  1                                   Malformed A2A responses do not
                                      crash downstream agents

  2                                   Cross-section Shared Context writes
                                      are blocked

  3                                   Waiting for upstream agents is
                                      bounded

  4                                   All-success upstream data produces
                                      `Success`

  5                                   Any partial upstream section
                                      prevents aggregate `Success`

  6                                   No usable upstream data produces
                                      `Failed`

  7                                   Partial data remains usable with
                                      explicit confidence/completeness
                                      metadata

  8                                   Empty Web Search data cannot be
                                      returned as successful pipeline
                                      output

  9                                   Query Strategist retry budgeting is
                                      handled outside the mesh utilities

  10                                  Internal statuses are consistent
                                      across the mesh
  -----------------------------------------------------------------------
