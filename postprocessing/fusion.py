#  Fusion of deduplicated queries using Reciprocal Rank Fusion (RRF)
#  Formula: RRF(d) = Σ(1 / (k + ri(d))) 
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse, urlunparse

import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import asyncio 

def fusion_status(results):
    url_counts = {}
    for result in results:
        if not getattr(result, "url", None):
            continue
        url_counts[result.url] = url_counts.get(result.url, 0) + 1

    return url_counts


def fuse_results(results):
    def canonical(url: str | None) -> str | None:
        if not url:
            return None
        parsed = urlparse(url.strip())
        cleaned = parsed._replace(query="", fragment="")
        return urlunparse(cleaned).rstrip("/").lower()

    url_counts = Counter()

    for result in results:
        key = canonical(result.url)
        if key:
            url_counts[key] += 1

    for result in results:
        result.fusion_score = url_counts.get(canonical(result.url), 1)
    return sorted(
            results,
            key=lambda x: (x.fusion_score, x.score or 0.0),
            reverse=True
        )

def fuse_result(results):
    return fuse_results(results)


