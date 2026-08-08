import asyncio
import json
import logging
from strategy.query_strategist import QueryStrategist
from llm.gemini_client import GeminiClient

logging.basicConfig(level=logging.DEBUG)

async def main():
    client = GeminiClient()
    strategist = QueryStrategist(client)
    res = await strategist.run({"startup_idea": "An AI platform for autonomous drones that deliver medical supplies to remote areas."})
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
