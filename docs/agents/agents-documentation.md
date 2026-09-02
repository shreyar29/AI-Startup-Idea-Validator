# Agents Documentation

VentureLens is powered by a decentralized **Agent Mesh** rather than a traditional monolithic application. Each agent acts as an independent specialist, executing asynchronously and emitting structured contracts.

## 1. Web Search Agent (`web_search_agent.py`)
- **Role**: Data Gatherer.
- **Responsibility**: Translates the user's startup idea into highly optimized search queries (e.g., market reports, competitor names). Interfaces directly with the **Tavily API** to scrape real-world evidence.
- **Output**: Generates the `research` context blob that all other agents consume.

## 2. Market Agent (`market_agent.py`)
- **Role**: Analyst.
- **Responsibility**: Analyzes the Tavily research to calculate market size (TAM/SAM/SOM), identify macro-economic growth drivers, list regulatory hurdles, and determine market maturity.
- **Contract**: `MarketContract`

## 3. Customer Agent (`customer_agent.py`)
- **Role**: Product Marketer.
- **Responsibility**: Identifies ideal customer profiles (ICPs), deep pain points, feature demands, and estimates willingness-to-pay.
- **Contract**: `CustomerContract`

## 4. Competitor Agent (`competitor_agent.py`)
- **Role**: Competitive Strategist.
- **Responsibility**: Extracts real-world competitors from the research, scores their threat levels, calculates differentiation moats, and maps them on an X/Y positioning matrix.
- **Contract**: `CompetitorContract`

## 5. SWOT Agent (`swot_agent.py`)
- **Role**: Business Consultant.
- **Responsibility**: Synthesizes Market, Customer, and Competitor data into a standard Strengths, Weaknesses, Opportunities, and Threats matrix. Furthermore, it creates a **TOWS Action Matrix** to generate actionable strategies.
- **Contract**: `SWOTContract`

## 6. MVP & GTM Agents (`mvp_agent.py`, `gtm_agent.py`)
- **Role**: Execution Planners.
- **Responsibility**: 
  - MVP: Defines Core vs. Optional features and estimates technical complexity.
  - GTM: Builds a 90-day launch roadmap, defines acquisition channels, and estimates CAC vs LTV risk.
- **Contract**: `MVPAnalysis`, `GTMAnalysis`

## 7. Risk Agent (`risk_agent.py`)
- **Role**: Auditor.
- **Responsibility**: Identifies Top 3 critical risks, assesses overall risk level (Critical, High, Medium, Low), and provides mitigation recommendations.
- **Contract**: `RiskAnalysis`

## 8. Comparison Agent (`comparison_agent.py`)
- **Role**: Executive Summarizer.
- **Responsibility**: Reviews the entire output of the Agent Mesh and writes the final cohesive narrative, including the "Final Strategy" and "Biggest Risk".

## 9. Vera Agent (`vera_agent.py`)
- **Role**: Interactive Co-Founder.
- **Responsibility**: Unlike the mesh agents which run once, Vera is persistent. She uses a **RAG (Retrieval-Augmented Generation)** pipeline to chunk the final JSON report into a vector store. When the user asks a question in the Workspace, she retrieves the relevant semantic chunks and streams a contextual response via WebSockets.
