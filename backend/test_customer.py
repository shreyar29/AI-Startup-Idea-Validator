import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agents.customer_agent import CustomerAgent

async def test_customer():
    context = {
        "idea": {"description": "FinTech app for micro-investing"},
        "research": {
            "search_results": {
                "customers": [
                    {"content": "The target audience includes retail investors who want to spend money efficiently."},
                    {"content": "A major pain point is the struggle to save money. Users who are younger often desire this."},
                    {"content": "They want to achieve financial freedom. The main feature demand is low fees."},
                ]
            }
        }
    }
    
    agent = CustomerAgent(context, llm_client=None)
    result = await agent.analyze()
    print("Segments:", len(result["target_customer_segments"]))
    print("Pain Points:", len(result["pain_points"]))
    print("Goals:", len(result["customer_goals"]))
    print("Personas:", len(result["customer_personas"]))
    print("Demands:", len(result["feature_demand"]))

if __name__ == "__main__":
    asyncio.run(test_customer())
