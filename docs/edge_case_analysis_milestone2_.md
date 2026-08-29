# Edge Case Analysis --- Milestone 2

**Project:** AI Startup Idea Validator\
**Owner:** Neha --- Edge Case Analyst\
**Milestone:** 2 --- Agent Mesh Integration\
**Scope:** Market Agent, Customer Agent, Competitor Agent, Comparison
Agent, Shared Context, A2A communication, and runtime integration
findings.

------------------------------------------------------------------------

## 1. Objective

Milestone 1 focused primarily on failures around the Web Search Agent
and external APIs. Milestone 2 introduces a different failure surface
because multiple agents now exchange information through **Shared
Context** and **agent-to-agent (A2A) calls**.

The purpose of this analysis is to ensure that:

-   one failed agent does not unnecessarily crash the complete pipeline;
-   incomplete data is never represented as complete data;
-   malformed A2A responses are caught before downstream use;
-   Shared Context is read and written safely;
-   the Comparison Agent knows exactly how much upstream information is
    available;
-   runtime failures are surfaced using structured status information.

------------------------------------------------------------------------

## 2. Status Contract

The Milestone 2 utility layer uses the following canonical internal
statuses.

  -----------------------------------------------------------------------
  Status                  Meaning                 Downstream Use
  ----------------------- ----------------------- -----------------------
  `Success`               Agent completed with    Use normally
                          usable complete output  

  `Partial Success`       Agent produced usable   Use with reduced
                          but incomplete/degraded confidence
                          output                  

  `Failed`                Agent produced no       Do not treat as valid
                          usable output           evidence
  -----------------------------------------------------------------------

> **Important:** `Partial Success` must never be counted as a full
> `Success`.

If the public API uses a different casing convention, such as `success`
or `failed`, normalization should happen at the API boundary rather than
mixing conventions inside Shared Context.

------------------------------------------------------------------------

## 3. A2A Communication Edge Cases

  -----------------------------------------------------------------------------------------------
  ID             Failure Mode     Why It Can     Expected Behaviour   Mitigation
                                  Happen                              
  -------------- ---------------- -------------- -------------------- ---------------------------
  A2A-01         Peer tool raises Target agent   Calling agent must   Convert to `A2AToolError`,
                 an exception     fails          not crash the        retry, then degrade safely
                                  internally     complete mesh        

  A2A-02         Peer tool        Different      Reject response      `validate_a2a_response()`
                 returns a        agents may     before downstream    
                 non-dictionary   expose         access               
                 response         inconsistent                        
                                  response                            
                                  formats                             

  A2A-03         Expected         Producer and   Treat response as    Validate required keys
                 response key is  consumer       malformed            explicitly
                 missing          contracts                           
                                  differ                              

  A2A-04         Circular peer    Agent A waits  Avoid                Read Shared Context first
                 dependency       on B while B   deadlock/recursive   and maintain
                                  waits on A     dependency           one-directional
                                                                      orchestration

  A2A-05         Peer never       Timeout,       Pipeline must not    Use bounded waiting and
                 becomes ready    crash, or      wait forever         report missing sections
                                  incomplete                          
                                  execution                           
  -----------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 4. Shared Context Edge Cases

  --------------------------------------------------------------------------------------
  ID             Failure Mode   Risk           Expected       Mitigation
                                               Behaviour      
  -------------- -------------- -------------- -------------- --------------------------
  SC-01          Agent writes   Silent data    Reject the     `write_to_own_section()`
                 to another     corruption     write          
                 agent's                       immediately    
                 section                                      

  SC-02          Section key    Consumer reads Section is not Require a terminal
                 exists before  incomplete     considered     `status`
                 agent finishes data           ready          

  SC-03          One section    Comparison     Stop waiting   `wait_for_sections()`
                 never receives Agent can hang after          
                 a terminal                    configured     
                 status                        timeout        

  SC-04          Shared Context Data can leak  Each request   Scope context by
                 reused across  between        gets isolated  request/correlation ID
                 requests       startup        state          
                                validations                   

  SC-05          Mixed status   Exact          Use one        `Success`,
                 casing         comparisons    internal       `Partial Success`,
                                fail           status         `Failed`
                                unexpectedly   contract       
  --------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 5. Partial Pipeline and Confidence Edge Cases

  -----------------------------------------------------------------------------------------------
  ID             Scenario             Correct Aggregate   Confidence     Reason
                                      Status                             
  -------------- -------------------- ------------------- -------------- ------------------------
  PP-01          Market, Customer,    `Success`           High           Complete upstream
                 Competitor all                                          evidence
                 succeed                                                 

  PP-02          Two succeed, one     `Partial Success`   Medium         Useful evidence exists
                 fails                                                   but one source agent is
                                                                         unavailable

  PP-03          One succeeds, two    `Partial Success`   Low            Limited usable evidence
                 fail                                                    

  PP-04          One section is       `Partial Success`   Medium         Partial section must not
                 `Partial Success`,                                      be promoted to full
                 remaining sections                                      success
                 succeed                                                 

  PP-05          All sections         `Failed`            Low            No usable evidence
                 fail/missing                                            

  PP-06          Comparison Agent     `Partial Success`   Medium/Low     Report must expose
                 receives partial                                        missing/failed/partial
                 data                                                    sections
  -----------------------------------------------------------------------------------------------

### Correction Applied

The earlier aggregation approach treated `Partial Success` as if it were
`Success`. That could incorrectly produce:

``` text
Market Agent      = Success
Customer Agent    = Partial Success
Competitor Agent  = Success

Incorrect aggregate: Success / high
```

The corrected `mesh_integration.py` tracks `partial_sections`
separately. Overall `Success` is returned **only when every required
section is fully successful**.

------------------------------------------------------------------------

## 6. Agent-Specific Edge Cases

  -------------------------------------------------------------------------------------------
  ID                Agent             Failure Mode         Mitigation
  ----------------- ----------------- -------------------- ----------------------------------
  AG-01             Market Agent      Different sources    Preserve competing values and
                                      provide conflicting  source references instead of
                                      market-size/growth   silently choosing one
                                      figures              

  AG-02             Customer Agent    Startup idea is too  Return low confidence rather than
                                      vague to infer       fabricating personas
                                      defensible customer  
                                      segments             

  AG-03             Competitor Agent  No valid competitor  Return degraded output with
                                      research snippets    `no_competitor_data_found: true`
                                      are available        

  AG-04             Competitor Agent  LLM returns          Parse defensively, retry within
                                      malformed JSON       bounded timeout, then degrade

  AG-05             Comparison Agent  One or more upstream Use available Success/Partial
                                      sections are         Success sections and expose
                                      unavailable          aggregate completeness

  AG-06             Comparison Agent  LLM fails while      Retry/validate according to the
                                      generating final     existing LLM error-handling
                                      comparison           policy; never fabricate a complete
                                                           report
  -------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 7. Runtime-Verified Findings

These findings came from actually running the integration branch.

  -----------------------------------------------------------------------------------------------------------------
  ID             Runtime Finding     Observed Behaviour             Root Cause / Risk    Required Mitigation
  -------------- ------------------- ------------------------------ -------------------- --------------------------
  RT-01          Invalid OpenRouter  Placeholder credentials/model  Local environment    Document required
                 configuration       produced                       was not configured   environment variables and
                 prevents correct    authentication/configuration   with real developer  keep secrets local
                 LLM execution       failure                        credentials          

  RT-02          Environment setup   `.env` contained placeholder   No reliable          Provide `.env.example`
                 was unclear         OpenRouter/Tavily values       developer setup      with placeholders only
                                                                    contract             

  RT-03          Missing             Imported packages may be       Clean checkout may   Audit imports against
                 dependencies can    absent from project            not run              `requirements.txt` and
                 block startup       requirements                                        test a clean virtual
                                                                                         environment

  RT-04          `/search` can       Downstream pipeline can        No                   Use
                 falsely appear      receive empty research while   response-integrity   `response_validator.py`;
                 successful when Web metadata reports success       validation           mark `Failed` and
                 Search contains no                                                      `no_data_found: true`
                 data                                                                    

  RT-05          Query Strategist    Two malformed/incomplete       Retry count and      Introduce per-attempt
                 retries can exhaust responses consumed most of the overall timeout are  timeout/retry budget and
                 the outer Web       120-second budget; attempt 2   not coordinated      reserve time for later
                 Search timeout      was cancelled                                       attempts

  RT-06          Structured-output   Runtime test used              Router may select    Re-test using the team's
                 reliability may     `openrouter/free`              models with          approved fixed model
                 depend on selected                                 different            
                 OpenRouter model                                   schema-following     
                                                                    behaviour            

  RT-07          Authentication      HTTP 401 cannot recover by     Retrying permanent   Retry only transient
                 errors should fail  repeating the same credential  configuration errors failures such as timeout,
                 fast                                               wastes timeout       429, and selected 5xx
                                                                    budget               errors
  -----------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 8. Runtime Reproduction --- Empty Web Search / False Success

**Input**

``` text
AI-powered meal planning app for college students
```

**Previously observed behaviour**

1.  `/search` completed.
2.  Web Search result categories contained no meaningful data.
3.  Downstream agents received empty research.
4.  Top-level metadata could still indicate success.

**Correct behaviour**

``` text
Web Search has no meaningful data
        ↓
response_validator detects empty output
        ↓
metadata.status = Failed
metadata.no_data_found = true
        ↓
downstream pipeline stops or explicitly degrades
```

**Implementation:** `backend/utils/response_validator.py`

------------------------------------------------------------------------

## 9. Runtime Reproduction --- Query Strategist Retry Timeout

**Input**

``` text
AI-powered meal planning app for college students
```

**Observed sequence**

  -----------------------------------------------------------------------
  Attempt                             Result
  ----------------------------------- -----------------------------------
  Attempt 0                           JSON decode/repair path triggered;
                                      required `identified_context` /
                                      `queries` missing

  Attempt 1                           Response validation failed because
                                      query category `competitors` was
                                      missing

  Attempt 2                           Started, but the outer Web Search
                                      Agent reached its 120-second
                                      timeout

  Final result                        In-progress OpenRouter request was
                                      cancelled; Web Search Agent
                                      degraded with timeout status
  -----------------------------------------------------------------------

The final pipeline correctly avoided the previous false-success
behaviour.

### Environment Note

The reproduction used:

``` env
OPENROUTER_MODEL=openrouter/free
```

Because this is a routing model, the team should reproduce the same case
using its approved fixed OpenRouter model before concluding that the
problem is exclusively caused by Query Strategist logic.

### Recommended Design

``` text
Outer Web Search timeout: 120 seconds
        │
        ├── Attempt 1: bounded timeout
        ├── validation
        ├── Attempt 2: bounded timeout
        ├── validation
        └── optional final attempt only if enough time remains
```

The exact timeout values should be decided by the integration owner
after profiling the approved model.

------------------------------------------------------------------------

## 10. Testing Checklist

  ----------------------------------------------------------------------------
  \#                Test                Expected Result      Status
  ----------------- ------------------- -------------------- -----------------
  1                 Force Competitor    `Partial Success`;   ☐
                    Agent to fail while failed section       
                    Market and Customer explicitly listed    
                    succeed                                  

  2                 Make one upstream   Aggregate must       ☐
                    section             remain               
                    `Partial Success`   `Partial Success`,   
                                        never `Success`      

  3                 Fail/miss every     `Failed`, low        ☐
                    upstream section    confidence           

  4                 Return a list       Malformed response   ☐
                    instead of dict     rejected gracefully  
                    from an A2A tool                         

  5                 Remove a required   Missing-key error    ☐
                    A2A response key    captured; no         
                                        downstream           
                                        `KeyError`           

  6                 Attempt             `ValueError`; write  ☐
                    cross-section       blocked              
                    Shared Context                           
                    write                                    

  7                 Delay one required  Wait exits at        ☐
                    Shared Context      timeout and reports  
                    section             missing section      

  8                 Run all analysis    Every required       ☐
                    agents successfully section has terminal 
                                        status               

  9                 Return empty Web    False success        ☑ Runtime
                    Search data         prevented; no-data   verified
                                        flag set             

  10                Produce malformed   Retry occurs and     ☑ Runtime
                    Query Strategist    outer timeout        verified
                    output              degrades safely      

  11                Repeat Query        Behaviour recorded   ☐
                    Strategist test     and compared with    
                    using team's        router result        
                    approved fixed                           
                    model                                    

  12                Verify internal     Only `Success`,      ☐
                    status values       `Partial Success`,   
                                        `Failed` used in     
                                        mesh utilities       
  ----------------------------------------------------------------------------

------------------------------------------------------------------------

## 11. Implementation Mapping

  -------------------------------------------------------------------------------
  File                                        Responsibility
  ------------------------------------------- -----------------------------------
  `backend/utils/error_handler.py`            Existing Milestone 1 retry,
                                              parsing, API/result safeguards

  `backend/utils/mesh_integration.py`         A2A safety, Shared Context
                                              readiness/ownership, partial-state
                                              aggregation

  `backend/utils/response_validator.py`       Prevent false-success when Web
                                              Search output has no meaningful
                                              data

  `docs/edge_case_analysis_milestone2_2.md`   Failure analysis, runtime findings,
                                              reproduction, testing checklist

  `docs/mesh_integration_design.md`           Technical contract explaining how
                                              Milestone 2 utilities should be
                                              integrated
  -------------------------------------------------------------------------------

------------------------------------------------------------------------

## 12. Scope Boundary

These utilities are intentionally defensive building blocks. They do not
automatically modify the Market, Customer, Competitor, Comparison, or
Orchestrator implementations.

The integration owner must call them at the correct points in the
pipeline. In particular, the Query Strategist retry-budget problem
belongs to the **Web Search/Query Strategist orchestration layer**, not
`mesh_integration.py` or `response_validator.py`.
