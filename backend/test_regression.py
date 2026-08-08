import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.container import container
from crew.orchestrator import StartupValidatorOrchestrator

ideas = [
    "Pet Care Tech platform connecting vets and owners",
    "AI Resume Builder that optimizes for ATS",
    "FinTech app for micro-investing",
    "Food Delivery app optimized for local farmers",
    "EdTech platform for personalized learning paths",
    "Healthcare telemedicine for rural areas",
    "Agriculture drone monitoring system",
    "Cybersecurity threat detection for small businesses",
    "Logistics route optimization for last-mile delivery",
    "Real Estate VR property tour generator"
]

async def run_tests():
    llm_provider = container.get_llm_provider()
    search_service = container.get_search_service()
    result_processor = container.get_result_processor()
    
    orchestrator = StartupValidatorOrchestrator(
        llm_client=llm_provider,
        search_service=search_service,
        result_processor=result_processor
    )
    
    for i, idea in enumerate(ideas, 1):
        print(f"\n{'='*50}\nTesting Idea {i}: {idea}\n{'='*50}")
        try:
            result = await orchestrator.validate_idea(idea)
            market = result.get("market_agent", {})
            competitor = result.get("competitor_agent", {})
            customer = result.get("customer_agent", {})
            
            print(f"Market Size: {market.get('market_size')} | Growth Rate: {market.get('growth_rate')}")
            print(f"Competitors Found: {len(competitor.get('competitors', []))}")
            if competitor.get('competitors'):
                print(f"First Competitor: {competitor['competitors'][0].get('name')}")
            print(f"Target Segments: {len(customer.get('target_customer_segments', []))}")
            print(f"Customer Personas Generated: {len(customer.get('customer_personas', []))}")
            
            print(f"Status: {result.get('metadata', {}).get('status')}")
            
            assert "market_size" in market, "Missing market_size"
            assert "competitors" in competitor, "Missing competitors"
            assert "target_customer_segments" in customer, "Missing target_customer_segments"
            
        except Exception as e:
            print(f"Failed on idea {idea}: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
