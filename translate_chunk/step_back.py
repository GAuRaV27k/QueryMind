from pathlib import Path

import sys
from API.gemini_client import client

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def stepback(context :str) ->str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
    Generate 3 broader conceptual question
    for this user query:
    User query
    {context}

    Return only the queries.
    """    )
    text = response.text
    if text is None:
        raise ValueError("No text returned from generate_content")
    return text


