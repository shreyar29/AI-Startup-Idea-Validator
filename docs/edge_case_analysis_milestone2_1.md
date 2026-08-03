# Edge Case Analysis — Milestone 2 (Agent Mesh Integration)
**Prepared by:** Neha
**Project:** AI Startup Idea Validator — Milestone 2
**Scope:** Market Agent, Customer Agent, Competitor Agent, Comparison Agent, and their mesh integration via Shared Context + A2A tool calls

---

## Why This Is Different From Milestone 1

Milestone 1's edge cases covered a single agent (Web Search Agent) talking to one external API (Tavily). Milestone 2 introduces **four agents talking to each other** through Shared Context and A2A tool calls, plus a Comparison Agent that depends on all three analysis agents succeeding. New categories of failure appear here that didn't exist before: partial agent failures, shared-state conflicts, and cross-agent dependency chains.

---

## 1. Agent-to-Agent (A2A) Communication Failures

| # | Failure Mode | Why It Happens | Mitigation |
|---|---|---|---|
| 1.1 | One agent's exposed tool call fails or times out | Market/Customer/Competitor Agent's tool (e.g. `get_market_summary()`) errors out when Comparison Agent calls it | Wrap every A2A tool call in retry logic (reuse `with_retry()` from `error_handler.py`); if still failing, Comparison Agent proceeds with partial data and flags which agent's data is missing |
| 1.2 | Circular A2A calls | Agent A calls Agent B's tool, which internally calls Agent A's tool, creating a loop | Enforce the agreed rule: "read from Shared Context first, only invoke another agent's tool if data isn't available" — no agent should need to call back the agent that called it |
| 1.3 | A2A tool returns data in an unexpected shape | Each agent's tool functions were built somewhat independently (different developers), so return formats may not perfectly match what a consuming agent expects | Validate the shape of any A2A response before using it; if malformed, treat like Milestone 1's `MalformedLLMOutputError` pattern — log it, degrade gracefully, don't crash |

---

## 2. Shared Context Conflicts

| # | Failure Mode | Why It Happens | Mitigation |
|---|---|---|---|
| 2.1 | Two agents write to Shared Context at the same time | Market Agent, Customer Agent, and Competitor Agent may run in parallel and all try to update Shared Context near-simultaneously | Each agent writes only to its own named section (`market_analysis`, `customer_analysis`, `competitor_analysis`) — never a shared key — so concurrent writes don't overwrite each other |
| 2.2 | An agent reads Shared Context before another agent has finished writing to it | Comparison Agent starts before Market Agent has completed, if orchestration doesn't wait properly | Comparison Agent should check for a `status` field (e.g. `"Success"` / `"Partial Success"` / `"Failed"`) in each section before consuming it, not just assume presence of data means completion |
| 2.3 | Shared Context grows unbounded across a long session | Every agent appends to context without ever clearing old data | Scope Shared Context per request/session (keyed by something like `request_id`), not global — matches the schema Abhipsha proposed in Milestone 1 |

---

## 3. Partial Pipeline Failures

| # | Failure Mode | Why It Happens | Mitigation |
|---|---|---|---|
| 3.1 | One of the three parallel agents fails entirely (e.g. Competitor Agent errors out) | API failure, malformed data, or an unhandled exception in that agent's code | Comparison Agent should treat this as `Partial Success`, not a hard failure — generate validation output using the two agents that succeeded, and clearly flag which section is missing |
| 3.2 | Comparison Agent runs with incomplete data and produces a misleadingly confident final report | If missing-data flags aren't checked, Comparison Agent might present a validation score as if it had full information | Comparison Agent's final report must carry forward a `confidence` field reflecting how many of the three source agents actually succeeded |
| 3.3 | Orchestrator doesn't know when all three parallel agents are actually done | No clear "all agents finished" signal in the current diagram | Each agent should set its own `status` field on completion in Shared Context; Orchestrator/Comparison Agent polls or waits for all three statuses before proceeding |

---

## 4. Per-Agent Specific Edge Cases

| # | Agent | Failure Mode | Mitigation |
|---|---|---|---|
| 4.1 | Market Agent | Market size/growth data conflicts between sources (e.g. two different TAM figures) | Reuse `detect_conflicting_data()` from Milestone 1; surface both figures rather than picking one |
| 4.2 | Customer Agent | Idea is too vague to identify meaningful customer segments | Reuse `flag_low_confidence_if_vague()` pattern; return `confidence: low` rather than fabricating personas |
| 4.3 | Competitor Agent | No competitors found for a very niche idea | Already handled — returns `no_competitor_data_found: true` (see `competitor_agent_design.md`) |
| 4.4 | Comparison Agent | SWOT/validation score generation depends on an LLM call that could fail or return malformed output | Reuse `with_retry()` and `safe_parse_llm_json()` / `MalformedLLMOutputError` pattern from Milestone 1 |

---

## 5. Integration & Testing Checklist

- [ ] Kill one agent mid-run (e.g. force Competitor Agent to fail) → confirm Comparison Agent still returns a `Partial Success` report, not a crash
- [ ] Feed conflicting market-size data from two sources → confirm both figures surface instead of one being silently chosen
- [ ] Submit a vague idea → confirm Customer Agent returns `confidence: low` rather than invented personas
- [ ] Call an agent's A2A tool with a malformed/missing response → confirm the calling agent degrades gracefully
- [ ] Run all four agents in sequence end-to-end on a normal idea → confirm every section of Shared Context (`market_analysis`, `customer_analysis`, `competitor_analysis`, `comparison_analysis`) is populated with a `status` field
- [ ] Check that no agent writes outside its own Shared Context section

---

## Notes

Everything here builds directly on the mitigations already implemented in `backend/utils/error_handler.py` (Milestone 1) and `backend/agents/competitor_agent.py` (Milestone 2) — this document identifies where those same patterns need to extend to Market, Customer, and Comparison Agents, and where new integration-level failure modes appear that didn't exist when there was only one agent.
