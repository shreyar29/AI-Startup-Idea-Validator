import asyncio
import json
import logging
from strategy.query_strategist import QueryStrategist
from llm.gemini_client import GeminiClient
from strategy.query_prompt import SYSTEM_PROMPT

logging.basicConfig(level=logging.DEBUG)

async def main():
    client = GeminiClient()
    res = await client.generate_response(SYSTEM_PROMPT, "<startup_idea>An AI platform for autonomous drones that deliver medical supplies to remote areas.</startup_idea>", {"type": "json_object"}, 0.0)
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
