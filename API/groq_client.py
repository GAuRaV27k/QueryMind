import os

from dotenv import load_dotenv
from groq import Groq
load_dotenv()
api_key=os.environ.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") 
if not api_key:
    raise ValueError(
        "Missing Tavily API key. Set TAVILY_API_KEY in your environment or .env file."
    )
client = Groq(
    api_key= api_key,
)


