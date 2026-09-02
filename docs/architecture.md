# VentureLens Engineering Architecture

This document provides a deep, technical breakdown of the VentureLens platform architecture.

## 1. High-Level Data Flow Architecture

VentureLens is fundamentally an event-driven system built around a central mesh orchestrator. The data flow guarantees that raw inputs are sanitized, enriched, validated, and finally structured for downstream UI consumption and Vector DB storage.

```mermaid
sequenceDiagram
    participant U as User
    participant GW as API Gateway
    participant O as Orchestrator
    participant M as Agent Mesh
    participant DB as SQLite / State
    participant R as Qdrant RAG

    U->>GW: POST /api/analyze (Idea)
    GW->>DB: Initialize 'pending' report
    GW->>O: Spawn Background Task
    O->>M: Dispatch Web Search Agent
    M-->>O: Enriched Market Data Context
    O->>M: Dispatch Parallel Analysis Layer
    M-->>O: Structured Pydantic Contracts
    O->>M: Dispatch Parallel Synthesis Layer
    M-->>O: Final Validation JSON
    O->>R: Chunk & Embed JSON Report
    O->>DB: Update 'completed' report state
    O-->>GW: WebSocket Push (Success)
```

## 2. Frontend Architecture

The React SPA utilizes a decoupled Context API for state management, allowing isolated renders of heavy data components without blocking the main thread.

```mermaid
graph TD
    App --> Router[React Router DOM]
    
    Router --> Dashboard[Dashboard Hub]
    Router --> Workspace[Workspace Component]
    
    subgraph Workspace Hub
        Workspace --> ReportView[Report Visualization]
        Workspace --> VeraUI[Vera AI Chat Interface]
    end
    
    subgraph State Management
        ReportView --> Context[DashboardContext]
        Context --> Sections[Market, Risk, SWOT, MVP]
    end
```

## 3. Backend Architecture

FastAPI acts as the API Gateway, managing HTTP requests, background tasks, and WebSockets.

```mermaid
graph LR
    API[FastAPI Routes] --> Controllers[Request Handlers]
    Controllers --> Services[Business Services]
    Services --> Models[SQLAlchemy ORM]
    Services --> Orchestrator[Agent Orchestrator]
```

## 4. Agent Architecture (P2P Mesh)

Unlike traditional LLM chains (e.g., LangChain Sequential), VentureLens agents act as independent microservices passing strict Pydantic schemas.

```mermaid
graph TD
    subgraph Layer 1: Data Gathering
        WS[Web Search Agent]
    end
    
    subgraph Layer 2: Core Analysis
        MKT[Market Agent]
        CUST[Customer Agent]
        COMP[Competitor Agent]
    end
    
    subgraph Layer 3: Strategic Synthesis
        SWOT[SWOT Agent]
        MVP[MVP Agent]
        GTM[GTM Agent]
        RISK[Risk Agent]
    end
    
    WS --> MKT & CUST & COMP
    MKT --> SWOT & MVP & GTM & RISK
    CUST --> SWOT & MVP & GTM & RISK
    COMP --> SWOT & RISK
```

## 5. RAG (Retrieval-Augmented Generation) Architecture

To power the Vera AI system without overwhelming context windows, we use an in-memory Qdrant instance.

```mermaid
graph TD
    JSON[Completed Report JSON] --> Chunker[Document Chunker]
    Chunker --> Embedder[Embedding Model]
    Embedder --> VectorStore[(Qdrant Vector DB)]
    
    UserQuery[User Chat Query] --> EmbedQuery[Embed Query]
    EmbedQuery --> VectorStore
    VectorStore -->|Top K Results| ContextBuilder
    ContextBuilder --> LLM[Chat LLM]
    LLM --> Response[WebSocket Stream]
```

## 6. Guardrails & Validation Architecture

Every agent output passes through the Guardrail Manager before being accepted into the shared state.

```mermaid
graph LR
    Agent[Agent Output] --> Parser[JSON Parser]
    Parser --> Pydantic[Schema Validation]
    Pydantic --> Factual[Factual Consistency Check]
    Factual --> State[Shared Context State]
    Factual -.->|Retry on fail| Agent
```

## 7. Export Architecture

The Export service reads the final JSON state and uses specific render engines.

```mermaid
graph TD
    State[Final Report State] --> ExportService[Export Manager]
    
    ExportService --> PDF[PDF Engine]
    ExportService --> PPTX[PPTX Engine]
    
    PDF --> StreamPDF[Stream Response Blob]
    PPTX --> StreamPPTX[Stream Response Blob]
```

## 8. Vera AI Architecture

Vera is a WebSocket-driven conversational agent with direct access to the RAG pipeline.

```mermaid
graph TD
    User -->|WebSocket| VeraHandler[FastAPI WS Route]
    VeraHandler --> SessionManager[Chat Session Manager]
    SessionManager --> Retrieval[RAG Context Fetcher]
    Retrieval --> LLM[Streaming LLM Response]
    LLM --> VeraHandler
```

## 9. Workspace Architecture

The workspace handles the persistence and historical tracking of generated ideas.

```mermaid
graph LR
    DB[(SQLite DB)] --> Query[SQLAlchemy Queries]
    Query --> Cache[Memory Cache]
    Cache --> API[History API]
    API --> Client[Dashboard UI]
```
