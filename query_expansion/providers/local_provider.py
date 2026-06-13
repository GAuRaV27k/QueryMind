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
class LocalLLMQueryExpander(QueryExpansionProvider):
    name = "local"
    priority = 40

    def is_available(self) -> bool:
        return bool(os.getenv("LOCAL_LLM_BASE_URL")) and bool(os.getenv("LOCAL_LLM_MODEL"))

    def _expand_sync(self, query: str) -> List[str]:
        base_url = os.getenv("LOCAL_LLM_BASE_URL")
        model = os.getenv("LOCAL_LLM_MODEL")
        if not base_url or not model:
            raise RuntimeError("Local LLM endpoint or model is missing")
        api_key = os.getenv("LOCAL_LLM_API_KEY")
        timeout_s = float(os.getenv("LOCAL_LLM_TIMEOUT_S", "30"))
        cleaned_base = base_url.rstrip("/")
        if cleaned_base.endswith("/v1"):
            endpoint = cleaned_base + "/chat/completions"
        else:
            endpoint = cleaned_base + "/v1/chat/completions"
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
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
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
