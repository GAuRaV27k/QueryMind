import os

from dotenv import load_dotenv
from youdotcom import You

load_dotenv()

api_key = os.getenv("YOU_API_KEY") or os.getenv("YOU_PLATFORM")
if not api_key:
    raise ValueError(
        "Missing You.com API key. Set YOU_API_KEY (or YOU_PLATFORM) in your environment or .env file."
    )

you_client = You(api_key)

