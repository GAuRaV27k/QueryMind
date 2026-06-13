from pathlib import Path
import asyncio
import sys

# from retrieval.retrieval_manager import retrivel_search
from pprint import pprint
# from postprocessing.fusion import fuse_result
def deduplicate(results):
    if not results:
        return []
    
    """
    Return unique results based on url.
    Comparison is case-insensitive and ignores surrounding whitespace.
    """
    def normalize(value):
        if value is None:
            return None
        text = str(value).strip()
        return text.lower() if text else None

    seen = set()
    unique = []

    for result in results:
        # Access url attribute directly since it's a dataclass
        url = normalize(getattr(result, "url", None))

        # Duplicate if the url has already been seen.
        if url and url in seen:
            continue

        if url:
            seen.add(url)

        unique.append(result)

    return unique
