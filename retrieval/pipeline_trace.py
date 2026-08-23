from __future__ import annotations

import asyncio
import time
from typing import Any

from generation.answer import generate_answer
from generation.cititation_map import (
    append_references,
    build_citation_map,
    find_invalid_citations,
)
from generation.context_builder import build_context
from generation.prompt_builder import build_prompt
from postprocessing.deduplication import deduplicate
from postprocessing.fusion import fuse_result
from postprocessing.reranking_v2 import reranker
from retrieval.Unified_retrieval_manager import normalize_provider_bundle
from retrieval.retrieval_decision_maker import plan_retrieval_async
from retrieval.retrieval_manager import _call_exa, _call_tavily, _call_you
from translate_chunk.extended_queries import get_extended_query_with_metadata


def _result_row(result: Any, rank: int) -> dict:
    return {
        "rank": rank,
        "title": getattr(result, "title", ""),
        "url": getattr(result, "url", ""),
        "provider": getattr(result, "provider", ""),
        "score": getattr(result, "score", None),
        "fusion_score": getattr(result, "fusion_score", None),
        "rerank_score": getattr(result, "rerank_score", None),
        "content_len": len(getattr(result, "content", "") or ""),
    }


async def trace_pipeline(request_id: str, query: str, intent: str = "research") -> dict:
    trace: dict[str, Any] = {
        "request_id": request_id,
        "query": query,
        "intent": intent,
        "stages": {},
    }

    t0 = time.perf_counter()
    expansion = await get_extended_query_with_metadata(query)
    trace["stages"]["query_expansion"] = {
        "input": query,
        "output": expansion.queries,
        "count": len(expansion.queries),
        "provider": expansion.provider,
        "fallback_used": expansion.fallback_used,
        "failures": [vars(item) for item in expansion.failures],
        "latency_ms": expansion.latency_ms,
    }

    p0 = time.perf_counter()
    plans = await plan_retrieval_async(query, expanded_queries=expansion.queries)
    trace["stages"]["retrieval_planner"] = {
        "input_queries": expansion.queries,
        "output": [vars(plan) for plan in plans],
        "count": len(plans),
        "latency_ms": (time.perf_counter() - p0) * 1000,
    }

    routing = []
    tasks = []
    for plan in plans:
        for tool in plan.tools:
            routing.append(
                {
                    "query": plan.query,
                    "intent": plan.intent,
                    "priority": plan.priority,
                    "provider": tool,
                }
            )
            if tool == "tavily":
                tasks.append(_call_tavily(plan.query, plan.intent, plan.priority))
            elif tool == "exa":
                tasks.append(_call_exa(plan.query, plan.intent, plan.priority))
            elif tool == "you":
                tasks.append(_call_you(plan.query, plan.intent, plan.priority))

    trace["stages"]["provider_routing"] = {"output": routing, "count": len(routing)}

    r0 = time.perf_counter()
    bundles = await asyncio.gather(*tasks, return_exceptions=True) if tasks else []
    provider_ms = (time.perf_counter() - r0) * 1000

    raw_provider = []
    failures = []
    normalized = []
    for bundle in bundles:
        if isinstance(bundle, Exception):
            failures.append({"provider": "unknown", "error": str(bundle)})
            continue
        raw_provider.append(
            {
                "provider": bundle.get("provider"),
                "query": bundle.get("query"),
                "status": bundle.get("status"),
                "error": bundle.get("error"),
                "raw_type": type(bundle.get("response")).__name__,
            }
        )
        if bundle.get("status") != "success":
            failures.append(bundle)
            continue
        normalized.extend(normalize_provider_bundle(bundle))

    trace["stages"]["provider_results"] = {
        "output": raw_provider,
        "count": len(raw_provider),
        "failures": failures,
        "latency_ms": provider_ms,
    }
    trace["stages"]["normalized_results"] = {
        "count": len(normalized),
        "output": [_result_row(item, idx + 1) for idx, item in enumerate(normalized[:20])],
    }

    fused = fuse_result(normalized)
    trace["stages"]["fusion"] = {
        "count": len(fused),
        "output": [_result_row(item, idx + 1) for idx, item in enumerate(fused[:20])],
    }

    deduped = deduplicate(fused)
    trace["stages"]["deduplication"] = {
        "count": len(deduped),
        "output": [_result_row(item, idx + 1) for idx, item in enumerate(deduped[:20])],
    }

    reranked = await reranker(deduped)
    trace["stages"]["reranking"] = {
        "count": len(reranked),
        "output": [_result_row(item, idx + 1) for idx, item in enumerate(reranked[:20])],
    }

    top_k = reranked[:8]
    context = build_context(top_k)
    trace["stages"]["context"] = {
        "count": len(top_k),
        "context_chars": len(context),
        "output_preview": context[:1500],
    }

    prompt = build_prompt(query, context, intent=intent)
    trace["stages"]["generation_prompt"] = {
        "chars": len(prompt),
        "output_preview": prompt[:1500],
    }

    answer = await generate_answer(prompt)
    citation_map = build_citation_map(top_k)
    invalid_before_sanitize = find_invalid_citations(answer, citation_map)
    final_answer = append_references(answer, citation_map)
    trace["stages"]["generation"] = {
        "answer_preview": (answer or "")[:800],
        "answer_chars": len(answer or ""),
    }
    trace["stages"]["citation_mapping"] = {
        "citation_ids": list(citation_map.keys()),
        "invalid_before_sanitize": invalid_before_sanitize,
        "final_answer_preview": final_answer[:800],
    }

    trace["total_latency_ms"] = (time.perf_counter() - t0) * 1000
    return trace
