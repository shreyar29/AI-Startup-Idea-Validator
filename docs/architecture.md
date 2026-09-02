# VentureLens System Architecture

## 1. High-Level System Architecture

VentureLens operates as an asynchronous, event-driven mesh network. The backend is powered by FastAPI, leveraging a decentralized multi-agent system built on asyncio. The frontend is a React SPA built with Vite, communicating over REST and WebSockets.

```mermaid
graph TD
    Client[React Frontend] <-->|REST API| API_GW[FastAPI Gateway]
    Client <-->|WebSockets| Vera[Vera Chat Agent]
    
    API_GW --> DB[(SQLite Database)]
    API_GW --> Orch[Agent Orchestrator]
    
    Orch --> Guard[Guardrail Manager]
    Orch --> Mesh[P2P Agent Mesh]
    
    subgraph P2P Agent Mesh
        WS[Web Search Agent]
        MKT[Market Agent]
        CUST[Customer Agent]
        COMP[Competitor Agent]
        RISK[Risk Agent]
        SWOT[SWOT Agent]
        MVP[MVP Agent]
        GTM[GTM Agent]
        
        WS --> MKT & CUST & COMP
        MKT --> SWOT & MVP & GTM & RISK
        CUST --> SWOT & MVP & GTM & RISK
        COMP --> SWOT & RISK
    end
    
    Mesh <--> LLM[LLM Provider]
    WS <--> Search[Tavily Search API]
```

## 2. Frontend Architecture

The frontend is a component-driven React application utilizing Context API for state management and Framer Motion for animations.

```mermaid
graph TD
    App --> Router[React Router]
    
    Router --> Dashboard[Dashboard Hub]
    Router --> Workspace[Workspace Wrapper]
    Router --> ReportView[Report View]
    
    ReportView --> Context[DashboardContext]
    Context --> Sections[Report Sections]
    
    subgraph Report Sections
        Market[MarketSection.jsx]
        Customer[CustomerSection.jsx]
        Competitor[CompetitorSection.jsx]
        Comparison[ComparisonSection.jsx]
        SWOT[SWOTSection.jsx]
        MVP[MVPSection.jsx]
        GTM[GTMSection.jsx]
        Risk[RiskSection.jsx]
    end
    
    Workspace --> VeraUI[Vera Chat UI]
```

## 3. Backend Architecture

The backend follows a service-oriented architecture, heavily leveraging dependency injection and asynchronous tasks.

```mermaid
graph TD
    Routes[FastAPI Routes] --> Controllers[Controllers/Handlers]
    Controllers --> Services[Business Services]
    Services --> DB[SQLAlchemy Models]
    Services --> Orchestrator[Crew Orchestrator]
    
    Orchestrator --> Context[Shared Memory Context]
    Orchestrator --> Validator[Pydantic Validators]
    Orchestrator --> Agents[Specialized Agents]
```

## 4. Agent Orchestration Architecture

The orchestration engine uses a Peer-to-Peer (P2P) mesh model where agents directly consume outputs from upstream agents rather than relying on a rigid central controller.

```mermaid
sequenceDiagram
    participant User
    participant Orch as Orchestrator
    participant WS as Web Search
    participant Layer1 as Market/Customer/Competitor
    participant Layer2 as SWOT/MVP/GTM/Risk
    participant Score as Scoring Engine
    
    User->>Orch: Submit Idea
    Orch->>WS: Initiate Search
    WS-->>Orch: Research Context
    
    Orch->>Layer1: Execute Parallel (Research Context)
    Layer1-->>Orch: Phase 1 Validated Contracts
    
    Orch->>Layer2: Execute Parallel (Phase 1 Context)
    Layer2-->>Orch: Phase 2 Validated Contracts
    
    Orch->>Score: Calculate Final Score
    Score-->>Orch: Scorecard
    
    Orch-->>User: Final Finalized Report
```

## 5. RAG Pipeline Architecture

The Retrieval-Augmented Generation (RAG) pipeline is utilized exclusively by the Vera Chat agent for context-aware Q&A against the generated report.

```mermaid
graph LR
    Report[JSON Report Data] --> Chunk[Text Chunker]
    Chunk --> Embed[Embedding Model]
    Embed --> VectorStore[(In-Memory Qdrant)]
    
    UserQuery[User Chat Message] --> EmbedQuery[Embed Query]
    EmbedQuery --> VectorStore
    VectorStore -->|Top K Matches| ContextBuilder[Context Builder]
    ContextBuilder --> LLM[LLM Generation]
    LLM --> Response[Vera Response]
```

## 6. Export Architecture

```mermaid
graph TD
    ReportData[Aggregated JSON] --> ExportManager[Export Service]
    
    ExportManager --> PDF[PDF Generator]
    ExportManager --> PPT[PPTX Generator]
    
    PDF --> PDF_API[FPDF / WeasyPrint]
    PPT --> PPT_API[python-pptx]
    
    PDF_API --> OutputFile[Downloadable Blob]
    PPT_API --> OutputFile
```
