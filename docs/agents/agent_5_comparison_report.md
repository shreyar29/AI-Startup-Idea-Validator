# Comparison (Strategy) Agent

## 1. Purpose & Responsibilities
The Comparison Agent is the apex node in the MAS mesh network. It is responsible for synthesizing the distinct outputs of all peer agents (Market, Customer, Competitor) into a single, cohesive, final Executive Strategy Report. It decides the final "Go/No-Go" recommendation.

## 2. Inputs & Outputs
- **Inputs**: 
  - `market_data`: Output from the Market Agent.
  - `customer_data`: Output from the Customer Agent.
  - `competitor_data`: Output from the Competitor Agent.
- **Outputs**: 
  - A JSON object containing the Final Recommendation, Confidence Score, Validation Score, Innovation Score, Biggest Risk, Immediate Next Action, Long-Term Strategic Direction, and a comprehensive Feature Matrix mapping proposed features to customer needs and competitor gaps.

## 3. Internal Workflow & Decision-Making Process
1. **Barrier Synchronization**: Unlike peer agents, the Comparison Agent *must* await the successful completion of the Market, Customer, and Competitor agents.
2. **Cross-Pollination**: It analyzes intersections (e.g., Does the Customer's pain point align with the Competitor's weakness?).
3. **Verdict Generation**: It determines a quantitative Validation and Innovation score and dictates the immediate next action for the founder.
4. **Validation**: Output is strictly checked to ensure it synthesizes, rather than hallucinates, new data.

## 4. Models & Tools Used
- **LLM**: Gemini or OpenRouter. Uses the largest available context window and highest reasoning capabilities to handle the massive JSON payload of all peer agents combined.

## 5. Backend & Frontend Integration
- **Backend Flow**: Executes last in the Orchestrator pipeline. Its output signifies the end of the entire validation request.
- **Frontend Flow**: Rendered in `ComparisonSection.jsx` as the "Final Strategy" tab, displaying the verdict front-and-center.

## 6. Error Handling
If a peer agent fails and returns fallback data (e.g., Competitor agent fails to find competitors), the Comparison Agent is dynamically prompted to synthesize the strategy based *only* on the available data, preventing a cascading failure of the entire pipeline.

## 7. Future Improvements
- Add probabilistic modeling to predict the statistical likelihood of startup failure based on historical datasets.
