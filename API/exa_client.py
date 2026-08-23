import os 
from dotenv import load_dotenv
load_dotenv()

exa_api_key = os.getenv("EXA_API") or os.getenv("EXA_API_KEY")

_import_error: str | None = None
try:
    from exa_py import Exa
except Exception as exc:  # pragma: no cover - environment dependent
    Exa = None
    _import_error = str(exc)


def get_exa_client():
    if Exa is None:
        raise RuntimeError(f"Exa SDK is unavailable: {_import_error}")
    if not exa_api_key:
        raise RuntimeError("Missing Exa API key. Set EXA_API_KEY (or EXA_API).")
    return Exa(api_key=exa_api_key)


exa_client = get_exa_client() if Exa is not None and exa_api_key else None
