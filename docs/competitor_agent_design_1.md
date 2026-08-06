# Competitor Agent — Design Document
**Project:** AI Startup Idea Validator — Milestone 2
**Related implementation:** `backend/agents/competitor_agent.py`

---

## 1. Role

The Competitor Agent identifies existing competitors for a given startup idea, compares their offerings and pricing, and highlights feature gaps the idea could differentiate on. It performs no independent web search — it works entirely from research data already gathered by the Web Search Agent (Milestone 1) and made available in Shared Context.

---

## 2. Position in the Architecture

Follows the mesh architecture finalized by the team:

- **Reads first from Shared Context** — does not call another agent's tool unless the data it needs isn't already there.
- **Never performs its own search** — only the Web Search Agent talks to Tavily/OpenRouter for live data.
- **Writes only to its own section** of Shared Context: `competitor_analysis`. It never modifies `market_analysis`, `customer_analysis`, or any other agent's section.
- **Exposes A2A tools** other agents (e.g. Comparison Agent) can call directly instead of re-deriving competitor insights themselves.

```
Shared Context
   │
   ▼
research.competitors  ──►  Competitor Agent  ──►  competitor_analysis
```

---

## 3. Input Contract

Reads from `shared_context`:

| Field | Source | Type | Notes |
|---|---|---|---|
| `idea.proposed_features` | Set by Orchestrator from user input | Array\<String\> | Used for gap analysis and positioning |
| `research.competitors` | Set by Web Search Agent (Milestone 1) | Array\<Object\> | Each object: `{competitor_name, url, summary, pricing, published_date}` |

If `research.competitors` is empty, the agent does **not** attempt its own search — it returns a low-confidence result instead (see Section 5).

---

## 4. Output Schema — `competitor_analysis`

```json
{
  "competitors": [
    {
      "name": "String",
      "summary": "String",
      "features": ["String"],
      "pricing": "String | null",
      "sources": ["String (URLs)"],
      "stale": "Boolean"
    }
  ],
  "gap_analysis": ["String"],
  "confidence": "high | low",
  "no_competitor_data_found": "Boolean",
  "conflicting_data": "Boolean",
  "conflicting_data_details": [
    { "competitor": "String", "conflicting_pricing": ["String"] }
  ],
  "errors": ["String"],
  "generated_at": "ISO 8601 timestamp"
}
```

This is the only section of Shared Context this agent writes to.

---

## 5. Exposed A2A Tools

| Tool | Type | Description |
|---|---|---|
| `get_competitor_summary()` | Required | Returns competitor names + summaries |
| `get_competitor_features()` | Required | Returns feature list per competitor |
| `get_competitor_pricing_comparison()` | Added value | Side-by-side pricing; flags conflicting prices between sources |
| `get_market_positioning_map()` | Added value | Classifies each competitor as direct / indirect / adjacent based on feature overlap with the idea |
| `get_competitive_gap_analysis()` | Added value | Returns idea features no competitor currently offers — signals real differentiation |

---

## 6. Error Handling (reused from Milestone 1)

This agent imports and reuses mitigations already built in `backend/utils/error_handler.py`, rather than duplicating logic:

| Mitigation | Function Used | Applied When |
|---|---|---|
| Deduplicate competitor sources | `dedupe_results()` | Multiple sources cite the same competitor URL |
| Flag outdated sources | `is_stale()` | Source has no publish date or is older than 1 year |
| Weight trusted sources higher | `is_trusted_source()` | Ranking sources before summarization |
| Detect conflicting data | `detect_conflicting_data()` | Two sources report different pricing for the same competitor |
| Retry on LLM failure | `with_retry()` | LLM summarization call fails |
| Handle malformed LLM output | `safe_parse_llm_json()` | LLM call succeeds but returns broken JSON or missing fields |

If no competitor research data exists at all, the agent returns `confidence: "low"` and `no_competitor_data_found: true` rather than fabricating a competitor.

---

## 7. Testing Performed

Ran against a mock Shared Context with 3 competitor sources, including:
- Two sources for the same competitor with **conflicting pricing** (`$10/mo` vs `$15/mo`)
- One **stale** source (dated 2020)
- One **trusted-domain** source (Crunchbase/TechCrunch)

Result: correctly deduped by URL, flagged the stale source, and detected the pricing conflict — confirming the reused error-handling logic works end-to-end with this agent, not just in isolation.

---

## 8. Known Limitations / Next Steps

- Currently runs in fallback mode without a live LLM client — competitor summaries are placeholders until OpenRouter is wired in.
- Competitor grouping relies on `competitor_name` being consistently tagged by the Web Search Agent; if tagging is inconsistent, the same competitor could be split into duplicate entries. Worth aligning with Abhipsha on this field's consistency during integration.
- Ready for integration and mesh-connection testing.
