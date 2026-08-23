import os

from dotenv import load_dotenv
load_dotenv()
api_key = os.environ.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

_import_error: str | None = None
try:
    from groq import Groq
except Exception as exc:  # pragma: no cover - environment dependent
    Groq = None
    _import_error = str(exc)


def get_groq_client():
    if Groq is None:
        raise RuntimeError(f"Groq SDK is unavailable: {_import_error}")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY for Groq client.")
    return Groq(api_key=api_key)


client = get_groq_client() if Groq is not None and api_key else None

