# Edge Case Analysis — Web Search Agent
**Owner:** Neha (Edge Case Analyst)
**Related implementation:** `backend/utils/error_handler.py`
**Project:** AI Startup Idea Validator — Milestone 1

---

## Master Failure Mode Table

| # | Category | Failure Mode | Why It Happens | Mitigation | Implemented In |
|---|---|---|---|---|---|
| 1.1 | API / Infrastructure | Search API times out or is down | Tavily outage, network issues, provider throttling | Timeout (10s) + retry with exponential backoff; fall back to cached result flagged `stale: true` | `with_retry()`, `REQUEST_TIMEOUT_SECONDS`, `SearchAPIError` |
| 1.2 | API / Infrastructure | Rate limit hit | Too many queries per idea or concurrent users | Cap queries per request (max 5); exponential backoff + retry (max 2) | `enforce_query_cap()`, `with_retry()`, `RateLimitError` |
| 1.3 | API / Infrastructure | OpenRouter/LLM call fails mid-pipeline | Provider downtime, malformed request, token limit exceeded | Retry once, then degrade to partial results instead of crashing | `with_retry()`, `LLMCallError`, `safe_execute()` |
| 1.4 | API / Infrastructure | LLM call succeeds but returns malformed/unusable output | During structured idea extraction or query decomposition, LLM may return broken JSON or omit fields, even though the call itself succeeded | Parse defensively, strip markdown fences, validate required keys; raise a distinct error to trigger retry or fallback | `safe_parse_llm_json()`, `MalformedLLMOutputError` |
| 2.1 | Bad or Empty Results | Zero search results returned | Idea is extremely niche or query too narrow | Broaden query and retry; if still empty, return `no_market_data_found: true` | `broaden_query()`, `build_response()` |
| 2.2 | Bad or Empty Results | Irrelevant/low-quality results (spam, generic blogs) | Search engine ranks SEO content over substance | Weight authoritative domains higher; require source attribution downstream | `is_trusted_source()`, `TRUSTED_DOMAINS` |
| 2.3 | Bad or Empty Results | Duplicate/near-identical sources | Many outlets republish the same press release | Dedupe by domain before summarization | `dedupe_results()` |
| 3.1 | Input Problems | Startup idea is vague | User submits something generic (e.g. "an app for productivity") | Detect short/generic input; set `confidence: low` | `flag_low_confidence_if_vague()`, `build_response()` |
| 3.2 | Input Problems | Idea targets a non-English-speaking market | Competitor/market data may only exist locally | Resolve a search-language hint per geography; fall back to translated query if results are thin | `resolve_search_language()` |
| 4.1 | Cost / Scope Control | Query decomposition explodes (e.g. 15 queries instead of 3–5) | Loosely bounded prompt or complex multi-part idea | Hard cap at 5 queries per request, keep highest priority | `enforce_query_cap()`, `MAX_QUERIES_PER_REQUEST` |
| 4.2 | Cost / Scope Control | Agent searches for things it shouldn't | No "don't search" rules (e.g. definitions, timeless facts) | Keyword-based exclusion check before any query is sent | `should_skip_search()`, `NO_SEARCH_KEYWORDS` |
| 5.1 | Data Quality / Trust | Source is outdated but ranks highly | Old articles can outrank recent ones via domain authority | Flag results with missing/old publish dates as `stale: true` | `is_stale()` |
| 5.2 | Data Quality / Trust | Source is unreliable (forum post, opinion piece) | Results mix authoritative and low-trust sources | Weight curated trusted domains higher during ranking | `is_trusted_source()` |
| 5.3 | Data Quality / Trust | Conflicting data between sources | Two sources disagree on market size/funding/competitor counts | Surface both values instead of silently picking one; flag `conflicting_data: true` | `detect_conflicting_data()` |

---

## Output Schema Impact

Every mitigation needs to be *visible* to the Market Analysis Agent, not just handled silently inside the Web Search Agent. These top-level fields were added to the agreed output schema:

| Field | Type | Set When |
|---|---|---|
| `status` | String (`Success` / `Partial Success` / `Failed`) | Always — reflects overall run outcome |
| `errors` | Array\<String\> | Any retry-exhausted failure (1.1–1.4) |
| `confidence` | String (`high` / `low`) | Idea was vague (3.1) |
| `stale` | Boolean | Cached fallback used, or source undated/old (1.1, 5.1) |
| `no_market_data_found` | Boolean | Zero results even after broadening (2.1) |
| `conflicting_data` | Boolean | Sources disagreed on a key figure (5.3) |

These are assembled centrally by `build_response()` in `error_handler.py` so no pipeline step can accidentally omit them.

---

## Testing Checklist (Day 3 — Validation)

| # | Test | Expected Result |
|---|---|---|
| 1 | Simulate Tavily API timeout | Retry + backoff fires, then graceful fallback |
| 2 | Simulate rate-limit response | Cap and backoff prevent repeated hammering |
| 3 | Submit malformed/broken LLM JSON output | `MalformedLLMOutputError` raised, retry triggered |
| 4 | Submit a deliberately vague idea ("an app") | `confidence: low` |
| 5 | Submit a hyper-niche idea | Query broadened; `no_market_data_found: true` if still empty |
| 6 | Submit an idea generating 10+ queries | Trimmed to top 5 by priority |
| 7 | Feed duplicate URLs from different queries | Deduped in final results |
| 8 | Feed two sources with different market-size figures | `conflicting_data: true`, both values surfaced |
| 9 | Feed an undated source | Flagged `stale: true` |