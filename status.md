# Project Status (2026-06-01)

This repo is a **retrieval backend skeleton**: query transformation is implemented, retrieval planning exists, and provider calls are available, but end-to-end retrieval+grounded generation is not wired.

## Current Implemented
1. **FastAPI endpoints**: `/query`, `/multi_query`, `/step_back` (stateful global query).
2. **Query expansion**: provider-fallback manager (Gemini/Groq/OpenRouter/Local) via `translate_chunk/extended_queries.py`.
3. **Retrieval planning**: Groq-based planner with heuristic fallback for invalid or incomplete plans.
4. **Provider clients**: Tavily, You.com, Exa API clients and simple provider wrappers.
5. **Async provider calls**: `_call_tavily`, `_you_call`, `_call_exa` with priority-based result sizing.
6. **Result normalization helpers**: `unified_retrieval_manager.py` maps provider output into `UnifiedRetrievalResult`.
7. **Postprocessing helpers**: `postprocessing/deduplication.py` and `postprocessing/fusion.py` for URL-based dedup and fusion scoring (prototype).
8. **Fusion metadata**: `UnifiedRetrievalResult` now includes `fusion_score`.

## Pipeline Status (Actual vs Intended)

| Stage | Status | Notes |
| --- | --- | --- |
| User Query intake | **Implemented** | `/query` stores query in a process-global variable. |
| Query Expansion (multi + step-back) | **Implemented** | Provider-fallback manager with retries; returns `[original_query]` on total failure. |
| Intent Classification & Planning | **Implemented** | Groq planner returns `RetrievalPlan` with tools + priority; heuristic fallback fills missing/duplicate plans. |
| Provider Routing | **Partial** | Planner selects tools, but orchestration is not wired to API. |
| Async Parallel Retrieval | **Partial** | Async provider calls exist; no unified execution pipeline. |
| Result Aggregation | **Not implemented** | No aggregation across providers. |
| Deduplication | **Partial** | URL-based dedup helper exists in `postprocessing/deduplication.py`. |
| Fusion / Reranking | **Partial** | Prototype fusion scoring via URL frequency in `postprocessing/fusion.py`. |
| Web Crawling / Extraction | **Not implemented** | No crawler or extractor. |
| Context Compression | **Not implemented** | No summarization or token budgeting. |
| Grounded Generation | **Not implemented** | No synthesis endpoint or citations. |

## Key Gaps
1. Retrieval orchestration that executes plans and normalizes results end-to-end.
2. Crawling, extraction, dedup, fusion/rerank, and grounded generation layers.
3. Stateless API design, storage, tests, and deployment/CI configuration.
