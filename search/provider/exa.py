from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from API.exa_client import exa_client

def search_exa(txt:str):
    response = exa_client.search(
        txt,
        type="auto",
        contents={"highlights": True},
    )
    return response