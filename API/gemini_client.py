import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

_import_error: str | None = None
try:
    from google import genai
except Exception as exc:  # pragma: no cover - environment dependent
    genai = None
    _import_error = str(exc)


def get_gemini_client():
    if genai is None:
        raise RuntimeError(f"Gemini SDK is unavailable: {_import_error}")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY for Gemini client.")
    return genai.Client(api_key=api_key)


client = get_gemini_client() if genai is not None and api_key else None

# response = client.models.generate_content(
#     model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
# )
# print(response.text)