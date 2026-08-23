import os

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("YOU_API_KEY") or os.getenv("YOU_PLATFORM")

_import_error: str | None = None
try:
    from youdotcom import You
except Exception as exc:  # pragma: no cover - environment dependent
    You = None
    _import_error = str(exc)


def get_you_client():
    if You is None:
        raise RuntimeError(f"You.com SDK is unavailable: {_import_error}")
    if not api_key:
        raise RuntimeError("Missing You.com API key. Set YOU_API_KEY (or YOU_PLATFORM).")
    return You(api_key)


you_client = get_you_client() if You is not None and api_key else None
