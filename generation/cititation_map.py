from pathlib import Path
from collections import Counter
import asyncio
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def build_citation_map(results):
    citation_map = {}

    for idx, result in enumerate(results, start=1):
        citation_map[f"S{idx}"] = {
            "title": result.title,
            "url": result.url
        }

    return citation_map

def append_references(answer, citation_map):

    references = "\n\nReferences:\n"

    for source_id, data in citation_map.items():
        references += (
            f"[{source_id}] {data['title']} - {data['url']}\n"
        )

    return answer + references