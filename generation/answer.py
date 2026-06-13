from pathlib import Path
import asyncio
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from API.gemini_client import client

async def generate_answer(prompt):
    print("inside generate_answer")

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    print("gemini response received")

    return response.text

# if __name__ == "__main__":

# print(asyncio.run(generate_answer("hello")))