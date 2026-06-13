from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from query_expansion.manager.query_expansion_manager import QueryExpansionManager
from query_expansion.types import QueryExpansionResult


# Example input format:
# [
#     'Google I/O 2026 AI highlights and key takeaways\nWhat were the significant machine learning innovations unveiled at Google I/O 2026?\nGoogle I/O 2026 new AI product announcements and developer platform updates\nStrategic AI initiatives from Google I/O 2026, including generative AI and large language model updates',
#     '1.  How do major AI announcements from events like Google I/O reflect and influence the overarching strategic direction and competitive landscape of artificial intelligence development globally?\n2.  What fundamental shifts in AI integration, accessibility, and user interaction are anticipated or enabled by breakthroughs unveiled at leading technology conferences?\n3.  Beyond immediate product applications, what critical societal, ethical, and research challenges are brought to the forefront by the latest generation of AI advancements, and how might they shape the next frontier of human-AI collaboration?'
# ]


import asyncio

_manager = QueryExpansionManager()


async def get_extended_query(query: str) -> list:
    """Expand a query with provider fallback."""
    return await _manager.expand(query)


async def get_extended_query_with_metadata(query: str) -> QueryExpansionResult:
    """Expand a query and return execution metadata."""
    return await _manager.expand_with_metadata(query)


'''
if __name__ == "__main__":
    try:
        result = asyncio.run(
            get_extended_query(
                "What are the key announcements in Google IO 2026 in the field of AI?"
            )
        )
        print("Extended Queries:")
        for i, q in enumerate(result, 1):
            print(f"  {i}. {q}")
    except Exception as e:
        print(f"Error: {e}")
'''