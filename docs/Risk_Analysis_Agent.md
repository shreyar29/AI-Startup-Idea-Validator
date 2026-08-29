# Milestone 3 --- Risk Analysis Agent

## 1. Milestone Overview

Milestone 3 implements the **Risk Analysis Agent** for the AI Startup
Idea Validator.

The agent evaluates startup risks using evidence already produced by
other analysis agents. It is designed as a decentralized node in the
**A2A Mesh Network**.

### Main objectives

-   Collect existing market, customer, competitor, and comparison
    analysis.
-   Ask an LLM to identify and structure startup risks.
-   Validate and normalize the returned risk data.
-   Calculate an overall risk score and risk level.
-   Produce practical mitigation recommendations.
-   Handle invalid LLM output, timeouts, and failures safely.

## 2. Implemented File

**File:** `backend/agents/risk_agent.py`

The file defines the `RiskAgent` class and the supporting
`RiskAnalysisError` exception.

## 3. RiskAgent Initialization

The agent receives: - `shared_context` - an optional `llm_client`

It maintains: - shared context; - peer-agent connections; - an
asynchronous analysis task; - an execution status.

The status can be `idle`, `started`, `success`, `failed`, or `timeout`.

## 4. A2A Mesh Integration

### `connect_peers(peers)`

Connects the Risk Agent to the other agents in the mesh by storing the
peer dictionary.

### `get_analysis()`

Acts as the mesh endpoint for risk analysis. It reuses an existing
asynchronous task when possible and creates a new task when required.
Failed or timed-out tasks can be reset for another attempt.

## 5. Evidence Collection

The Risk Agent does **not perform duplicate web research**.

It reads existing structured results from the shared context: -
`market_analysis` - `customer_analysis` - `competitor_analysis` -
`comparison_analysis`

It also reads the startup idea from the shared context.

These values are converted into a compact JSON evidence context for the
LLM.

## 6. Risk Categories

The LLM is instructed to identify relevant risks across:

1.  Market
2.  Competition
3.  Customer Adoption
4.  Technical Feasibility
5.  Business
6.  Financial
7.  Operational
8.  Regulatory
9.  AI/LLM

The prompt explicitly tells the LLM to use only the supplied evidence
and not invent unsupported facts.

## 7. Risk Structure and Validation

Each risk is expected to contain: - `category` - `risk` - `severity` -
`likelihood` - `impact` - `evidence` - `mitigation`

Severity, likelihood, and impact are normalized to: - Low - Medium -
High - Critical

The `_validate_risk()` method removes invalid risk entries, supplies
safe defaults, and normalizes the risk levels.

## 8. LLM Integration

The `analyze()` method sends the evidence and instructions to the
configured LLM client.

The system prompt requires **valid JSON only**.

The implementation supports configurable: - maximum retries; - LLM
timeout.

If the LLM returns invalid JSON, a retry includes the previous error and
asks the model to correct the JSON formatting.

The implementation uses `safe_parse_llm_json()` and handles
`MalformedLLMOutputError`.

## 9. Risk Score Calculation

The `_calculate_score()` method assigns numerical weights:

  Level        Weight
  ---------- --------
  Low               1
  Medium            2
  High              3
  Critical          4

For every risk:

`risk contribution = severity + likelihood + impact`

The total is normalized against the maximum possible score and converted
into a percentage.

### Overall risk classification

      Score Overall Risk Level
  --------- --------------------
      0--24 Low
     25--49 Medium
     50--74 High
    75--100 Critical

If there are no valid risks, the score is `0` and the overall level is
`Low`.

## 10. Final Risk Analysis Output

The final structured result contains: - `overall_risk_level` -
`overall_risk_score` - `risks` - `top_risks` - `recommendations` -
`confidence` - `failure_reason` - `status` - `generated_at`

The result is stored in:

`shared_context["risk_analysis"]`

The implementation limits the output to the top 5 risks and top 10
recommendations.

## 11. Error Handling and Degraded Mode

The agent includes safe fallback behavior.

### LLM unavailable

If an LLM client is not available, the agent returns a degraded response
instead of crashing.

### Timeout

If the LLM request times out, the agent marks the status as `timeout`
and returns a safe degraded response.

### Unexpected failure

Unexpected exceptions are logged, the status becomes `failed`, and a
degraded response is returned.

### Invalid JSON

Malformed LLM output is detected and retried. If parsing still fails,
the agent returns a safe degraded result.

## 12. Logging and Traceability

The implementation records: - correlation ID; - analysis start and
completion; - execution duration; - LLM attempts; - timeout events; -
parsing failures; - final risk level and score; - final structured
analysis.

The correlation ID comes from the shared context and is included in log
messages.

## 13. Milestone 3 Workflow

``` text
Existing Agent Outputs
        |
        v
Market Analysis
Customer Analysis
Competitor Analysis
Comparison Analysis
        |
        v
   Shared Context
        |
        v
     Risk Agent
        |
        v
   Build Evidence
        |
        v
       LLM
        |
        v
   Structured JSON
        |
        v
 Validate Risks
        |
        v
 Calculate Score
        |
        v
 Overall Risk Level
        |
        v
 Recommendations
        |
        v
 shared_context["risk_analysis"]
```

## 14. Milestone 3 Outcome

Milestone 3 provides a structured and fault-tolerant way to evaluate
startup risks from the outputs of the existing analysis agents.

### Technical contributions

-   A2A mesh-compatible Risk Agent.
-   Shared-context based evidence aggregation.
-   LLM-powered risk identification.
-   Structured JSON output requirements.
-   Risk validation and normalization.
-   Quantitative risk scoring.
-   Overall risk classification.
-   Top-risk extraction.
-   Mitigation recommendations.
-   Retry and timeout handling.
-   Degraded-mode failure handling.
-   Logging and execution traceability.

## 15. Source Basis

This document describes the implementation present in
`backend/agents/risk_agent.py`. It does not claim additional Milestone 3
functionality beyond what is implemented in that file.
