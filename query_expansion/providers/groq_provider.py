from __future__ import annotations

import asyncio
import os
from typing import List

from groq import Groq

from query_expansion.providers import register_provider
from query_expansion.types import QueryExpansionProvider
from query_expansion.utils import parse_query_list


@register_provider
class GroqQueryExpander(QueryExpansionProvider):
    name = "groq"
    priority = 20

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        self._client = Groq(api_key=api_key) if api_key else None

    def is_available(self) -> bool:
        return self._client is not None

    def _expand_sync(self, query: str) -> List[str]:
        if not self._client:
            raise RuntimeError("Groq API key is missing")
        model = os.getenv("GROQ_QUERY_EXPANDER_MODEL") or os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant"
        system_prompt = (
            "You generate query expansions for retrieval. "
            "Return ONLY a JSON array of strings with: "
            "1 original query, 4 paraphrased expansions, and 3 step-back queries."
        )
        user_prompt = f"Original query: {query}"
        response = self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise RuntimeError("Groq query expander returned an empty response")
        return parse_query_list(content)

    async def expand(self, query: str) -> List[str]:
        return await asyncio.to_thread(self._expand_sync, query)
