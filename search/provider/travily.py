from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from API.travily_client import tavily_client

def travily_search(txt):
    response = tavily_client.search(txt)
    return response

# print(travily_search("how is narendra modi"))


