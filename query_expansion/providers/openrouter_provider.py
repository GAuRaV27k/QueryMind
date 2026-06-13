from __future__ import annotations

import asyncio
import json
import os
import urllib.request
from typing import List

from query_expansion.providers import register_provider
from query_expansion.types import QueryExpansionProvider
from query_expansion.utils import parse_query_list


@register_provider
class OpenRouterQueryExpander(QueryExpansionProvider):
    name = "openrouter"
    priority = 30

    def is_available(self) -> bool:
        return bool(os.getenv("OPENROUTER_API_KEY"))

    def _expand_sync(self, query: str) -> List[str]:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OpenRouter API key is missing")
        model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")
        endpoint = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
        timeout_s = float(os.getenv("OPENROUTER_TIMEOUT_S", "30"))
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return ONLY a JSON array of strings with: "
                        "1 original query, 4 paraphrased expansions, and 3 step-back queries."
                    ),
                },
                {"role": "user", "content": f"Original query: {query}"},
            ],
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            raw = response.read().decode("utf-8")
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
        return parse_query_list(content)

    async def expand(self, query: str) -> List[str]:
        return await asyncio.to_thread(self._expand_sync, query)
