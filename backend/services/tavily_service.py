from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query):
    return client.search(query)
class TavilySearchService:
    """Placeholder for future Tavily search logic."""
    pass
