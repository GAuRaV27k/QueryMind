import os

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY") or os.getenv("TRAVILY_API")

_import_error: str | None = None
try:
    from tavily import TavilyClient
except Exception as exc:  # pragma: no cover - environment dependent
    TavilyClient = None
    _import_error = str(exc)


def get_tavily_client():
    if TavilyClient is None:
        raise RuntimeError(f"Tavily SDK is unavailable: {_import_error}")
    if not api_key:
        raise RuntimeError("Missing Tavily API key. Set TAVILY_API_KEY (or TRAVILY_API).")
    return TavilyClient(api_key=api_key)


tavily_client = get_tavily_client() if TavilyClient is not None and api_key else None
