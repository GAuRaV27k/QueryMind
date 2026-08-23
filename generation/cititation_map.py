from pathlib import Path
from collections import Counter
import re
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
    answer = sanitize_citations(answer, citation_map)

    references = "\n\nReferences:\n"

    for source_id, data in citation_map.items():
        references += (
            f"[{source_id}] {data['title']} - {data['url']}\n"
        )

    return answer + references


def sanitize_citations(answer: str, citation_map: dict) -> str:
    valid_ids = set(citation_map.keys())

    def _replace(match: re.Match[str]) -> str:
        source_id = match.group(1)
        if source_id in valid_ids:
            return f"[{source_id}]"
        return "[citation unavailable]"

    return re.sub(r"\[(S\d+)\]", _replace, answer or "")


def find_invalid_citations(answer: str, citation_map: dict) -> list[str]:
    valid_ids = set(citation_map.keys())
    seen: list[str] = []
    for source_id in re.findall(r"\[(S\d+)\]", answer or ""):
        if source_id not in valid_ids and source_id not in seen:
            seen.append(source_id)
    return seen