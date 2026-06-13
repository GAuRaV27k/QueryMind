import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY") or os.getenv("TRAVILY_API")
if not api_key:
    raise ValueError(
        "Missing Tavily API key. Set TAVILY_API_KEY in your environment or .env file."
    )

tavily_client = TavilyClient(api_key=api_key)
