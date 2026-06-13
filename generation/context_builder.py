from pathlib import Path
import asyncio
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def build_context(results,max_content_chars=1200):
    """Build a formatted context string from search results."""
    if not results:
        return ""
    
    context = []
    for i, result in enumerate(results, start=1):

        context.append(
            f"""
    [Source {i}]
    Title: {result.title}
    URL: {result.url}
    Provider: {result.provider}

    {result.content[:max_content_chars]}
    """
        )

    return "\n".join(context)
