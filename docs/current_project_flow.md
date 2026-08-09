# Current Project Flow

This document outlines the end-to-end flow of the VentureLens AI Startup Validator platform, covering both the frontend user journey and the backend processing pipeline based on the current implementation.

## 1. Frontend Flow (User Interaction)

1. **User Input:** The user accesses the application and enters a startup idea on the main dashboard (`/dashboard` or home page).
2. **Submission:** Upon submission, the frontend generates a unique request ID and sends a request to the backend's `/search` endpoint with the query.
3. **Real-time Progress Tracking:** Immediately after submission, the frontend connects to the backend's SSE (Server-Sent Events) endpoint (`/api/progress/{request_id}`) to receive real-time granular updates about the validation process.
4. **Result Rendering:** Once the backend completes the processing and returns the final JSON response, the frontend parses the data and routes it to specific UI components (e.g., `MarketSection`, `CompetitorSection`, `WebSearchSection`) for display. Any errors or timeouts are gracefully handled by `ErrorState` components.

## 2. Backend Flow (Processing Pipeline)

1. **Request Interception:** The `RequestTrackingMiddleware` intercepts the incoming `/search` request, assigning or preserving the `X-Request-ID`, and logs the start time.
2. **Input Validation:** The `search` router uses `GuardrailManager.validate_input` to ensure the query meets the minimum length and constraints.
3. **Progress Initialization:** The `ProgressManager` creates a new session for the request to start broadcasting status updates via SSE.
4. **Orchestration:** The request is passed to the `StartupValidatorOrchestrator`, which manages the multi-agent pipeline using a **P2P Mesh Network Architecture**.
5. **Agent Execution:**
   - A `shared_context` dictionary is created containing the user's idea and empty slots for research data.
   - Five agents are instantiated: `WebSearchAgent`, `MarketOpportunityAgent`, `CustomerAgent`, `CompetitorAgent`, and `ComparisonAgent`.
   - The agents are wrapped in `MeshNodeWrapper` which handles individual timeouts and metrics.
   - **Data Fetching:** The `WebSearchAgent` is executed first to gather live data and populate `shared_context["research"]`.
   - **Parallel Analysis:** The other agents (`Market`, `Customer`, `Competitor`) process the research data in parallel, directly reading from and writing to their respective sections in the `shared_context`.
   - **Synthesis:** The `ComparisonAgent` is triggered last to evaluate and synthesize the findings.
6. **Guardrails & Hallucination Checks:**
   - The orchestrator passes each agent's output through `GuardrailManager.validate_agent_output` to ensure all required fields are present.
   - `GuardrailManager.verify_facts_and_hallucinations` is called to cross-reference the generated insights against the original web search data.
7. **Finalization:** The final payload is formatted and passed through `GuardrailManager.verify_final_response`. The orchestrator determines the overall success status (success, partial_success, or failed) based on individual agent metrics.
8. **Response:** The completed JSON payload is returned to the frontend, and the `ProgressManager` broadcasts the final "completed" event to close the SSE stream. A background task (`cleanup_task` in `app.py`) periodically cleans up stale progress sessions.

---

## Changes in Agent Architecture & Documentation

*(Based on review of current implementation vs. existing agent documentation)*

- **Removal of CrewAI:** The backend has completely moved away from CrewAI and LiteLLM tool-selection loops. The multi-agent workflow is now a pure Python asyncio implementation (P2P Mesh Network) orchestrated by `StartupValidatorOrchestrator`.
- **MeshNodeWrapper Introduction:** Agents are no longer executed raw; they are wrapped in `MeshNodeWrapper`. This wrapper enforces strict, granular timeouts for each agent (e.g., `WEB_SEARCH_TIMEOUT`, `MARKET_AGENT_TIMEOUT`) and handles partial failures, allowing the pipeline to degrade gracefully instead of crashing entirely.
- **Direct State Mutation:** Agents no longer rely on complex message-passing for state. Instead, they share a thread-safe `shared_context` dictionary (GIL-protected) and write their specific outputs directly to pre-defined keys (e.g., `market_analysis`, `competitor_analysis`).
- **Post-Execution Guardrails:** Fact-checking and hallucination detection are now explicitly handled by `GuardrailManager` *after* the agents complete their tasks, rather than relying solely on the LLM to self-correct during generation.
- **Progress Broadcasting:** Agents do not print to the console for progress. The `MeshNodeWrapper` and `StartupValidatorOrchestrator` publish distinct lifecycle events directly to `ProgressManager`, which routes them to the frontend via SSE.
