from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RetrievalPlan:
    query: str
    intent: str
    tools: List[str]
    priority: str
    reasoning: str
