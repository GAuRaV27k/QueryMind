import time
try:
    from flashrank import Ranker, RerankRequest
except Exception as exc:  # pragma: no cover - environment dependent
    Ranker = None
    RerankRequest = None
    _flashrank_import_error = str(exc)
else:
    _flashrank_import_error = None

_ranker = None


def _get_ranker():
    if Ranker is None:
        raise RuntimeError(f"FlashRank is unavailable: {_flashrank_import_error}")
    global _ranker
    if _ranker is None:
        _t0 = time.time()
        _ranker = Ranker()
        print(f"[reranker] FlashRank ready in {time.time() - _t0:.1f}s", flush=True)
    return _ranker


async def reranker(results, ranker_instance=None):

    print(
        f"[reranker] reranker() called with {len(results)} results",
        flush=True
    )

    if not results:
        return []
    if RerankRequest is None and ranker_instance is None:
        raise RuntimeError(f"FlashRank is unavailable: {_flashrank_import_error}")

    query = results[0].query

    passages = []

    for idx, result in enumerate(results):
        passages.append({
            "id": idx,
            "text": result.content[:1500]
        })

    if RerankRequest is None:
        request = {"query": query, "passages": passages}
    else:
        request = RerankRequest(
            query=query,
            passages=passages
        )

    ranker_obj = ranker_instance or _get_ranker()
    ranked_passages = ranker_obj.rerank(request)

    ranked_results = []

    for item in ranked_passages:
        result_idx = item["id"]
        if not isinstance(result_idx, int) or result_idx < 0 or result_idx >= len(results):
            continue
        result = results[result_idx]

        result.rerank_score = float(
            item.get("score", 0.0)
        )

        ranked_results.append(result)

    return ranked_results if ranked_results else results
