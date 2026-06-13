from __future__ import annotations

import asyncio
import os
from typing import List

from query_expansion.providers import register_provider
from query_expansion.types import QueryExpansionProvider
from query_expansion.utils import parse_query_list
from translate_chunk.multi_query import generate_multiquery
from translate_chunk.step_back import stepback


@register_provider
class GeminiQueryExpander(QueryExpansionProvider):
    name = "gemini"
    priority = 10

    def is_available(self) -> bool:
        return bool(os.getenv("GEMINI_API_KEY"))

    async def expand(self, query: str) -> List[str]:
        loop = asyncio.get_running_loop()
        multi_text = await loop.run_in_executor(None, generate_multiquery, query)
        step_text = await loop.run_in_executor(None, stepback, query)
        expanded = parse_query_list(multi_text) + parse_query_list(step_text)
        return expanded
