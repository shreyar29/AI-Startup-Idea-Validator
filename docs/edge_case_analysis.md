# Edge Case Analysis — Web Search Agent
**Owner:** Neha (Edge Case Analyst)
**Related implementation:** `backend/utils/error_handler.py`
**Project:** AI Startup Idea Validator — Milestone 1

---

## 1. API / Infrastructure Failures

| # | Failure Mode | Why It Happens | Mitigation | Implemented In |
|---|---|---|---|---|
| 1.1 | Search API times out or is down | Tavily outage, network issues, provider throttling | Timeout (10s) + retry with exponential backoff; fall back to cached result flagged `stale: true` | `with_retry()`, `REQUEST_TIMEOUT_SECONDS`, `SearchAPIError` |
| 1.2 | Rate limit hit | Too many queries per idea or concurrent users | Cap queries per request (max 5); exponential backoff + retry (max 2) | `enforce_query_cap()`, `with_retry()`, `RateLimitError` |
| 1.3 | OpenRouter/LLM call fails mid-pipeline | Provider downtime, malformed request, token limit exceeded | Retry once, then degrade to partial results instead of crashing | `with_retry()`, `LLMCallError`, `safe_execute()` |
| 1.4 | LLM call succeeds but returns malformed/unusable output | During structured startup-idea extraction or query decomposition, the LLM may return broken JSON or omit required fields, even though the API call itself succeeded | Parse defensively, strip markdown fences, validate required keys; raise a distinct error so caller can retry with a stricter prompt or fall back to partial structure | `safe_parse_llm_json()`, `MalformedLLMOutputError` |

## 2. Bad or Empty Results

| # | Failure Mode | Why It Happens | Mitigation | Implemented In |
|---|---|---|---|---|
| 2.1 | Zero search results returned | Idea is extremely niche or query too narrow | Broaden query and retry; if still empty return `no_market_data_found: true` | `broaden_query()`, `build_response()` |
| 2.2 | Irrelevant/low-quality results (spam, generic blogs) | Search engine ranks SEO content over substance | Weight authoritative domains higher; require source attribution downstream | `is_trusted_source()`, `TRUSTED_DOMAINS` |
| 2.3 | Duplicate/near-identical sources | Many outlets republish the same press release | Dedupe by domain before summarization | `dedupe_results()` |

## 3. Input Problems

| # | Failure Mode | Why It Happens | Mitigation | Implemented In |
|---|---|---|---|---|
| 3.1 | Startup idea is vague | User submits something generic (e.g. "an app for productivity") | Detect short/generic input; set `confidence: low` | `flag_low_confidence_if_vague()`, `build_response()` |
| 3.2 | Idea targets a non-English-speaking market | Competitor/market data may only exist locally | Resolve a search-language hint per geography; fall back to translated query if results are thin | `resolve_search_language()` |

## 4. Cost / Scope Control

| # | Failure Mode | Why It Happens | Mitigation | Implemented In |
|---|---|---|---|---|
| 4.1 | Query decomposition explodes (e.g. 15 queries instead of 3–5) | Loosely bounded prompt or complex multi-part idea | Hard cap at 5 queries per request, keep highest priority | `enforce_query_cap()`, `MAX_QUERIES_PER_REQUEST` |
| 4.2 | Agent searches for things it shouldn't | No "don't search" rules (e.g. definitions, timeless facts) | Keyword-based exclusion check before any query is sent | `should_skip_search()`, `NO_SEARCH_KEYWORDS` |

## 5. Data Quality / Trust

| # | Failure Mode | Why It Happens | Mitigation | Implemented In |
|---|---|---|---|---|
| 5.1 | Source is outdated but ranks highly | Old articles can outrank recent ones via domain authority | Flag results with missing/old publish dates as `stale: true` | `is_stale()` |
| 5.2 | Source is unreliable (forum post, opinion piece) | Results mix authoritative and low-trust sources | Weight curated trusted domains higher during ranking | `is_trusted_source()` |
| 5.3 | Conflicting data between sources | Two sources disagree on market size/funding/competitor counts | Surface both values instead of silently picking one; flag `conflicting_data: true` | `detect_conflicting_data()` |

---

## Output Schema Impact

Every one of these mitigations needs to be *visible* to the Market Analysis Agent, not just handled silently inside the Web Search Agent. The following top-level fields were added to the agreed output schema for this purpose:

| Field | Type | Set When |
|---|---|---|
| `status` | String (`Success` / `Partial Success` / `Failed`) | Always — reflects overall run outcome |
| `errors` | Array\<String\> | Any retry-exhausted failure (1.1–1.3) |
| `confidence` | String (`high` / `low`) | Idea was vague (3.1) |
| `stale` | Boolean | Cached fallback used, or source undated/old (1.1, 5.1) |
| `no_market_data_found` | Boolean | Zero results even after broadening (2.1) |
| `conflicting_data` | Boolean | Sources disagreed on a key figure (5.3) |

These are assembled centrally by `build_response()` in `error_handler.py` so no pipeline step can accidentally omit them.

---

## Testing Checklist (Day 3 — Validation)

- [ ] Simulate Tavily API timeout → confirm retry + backoff fires, then graceful fallback
- [ ] Simulate rate-limit response → confirm cap and backoff prevent repeated hammering
- [ ] Submit a deliberately vague idea ("an app") → confirm `confidence: low`
- [ ] Submit a hyper-niche idea → confirm query broadening, then `no_market_data_found: true` if still empty
- [ ] Submit an idea generating 10+ queries → confirm trimmed to top 5 by priority
- [ ] Feed duplicate URLs from different queries → confirm deduped in final results
- [ ] Feed two sources with different market-size figures → confirm `conflicting_data: true` and both values surfaced
- [ ] Feed an undated source → confirm flagged `stale: true`