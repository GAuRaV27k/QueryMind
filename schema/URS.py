from dataclasses import dataclass, field
from typing import Optional, Dict, List


@dataclass
class RetrievalResult:

    # Core Result
    title: str
    url: str
    snippet: str

    # Provider Info
    provider: str
    query: str

    # Ranking
    rank: int
    score: Optional[float] = None

    # Rich Content
    summary: Optional[str] = None
    highlights: List[str] = field(default_factory=list)

    # Crawling
    raw_content: Optional[str] = None
    crawled_content: Optional[str] = None

    # Metadata
    favicon: Optional[str] = None
    image: Optional[str] = None
    published_date: Optional[str] = None
    author: Optional[str] = None
    domain: Optional[str] = None

    # Entities
    entities: List[Dict] = field(default_factory=list)

    # Extra Metadata
    metadata: Dict = field(default_factory=dict)