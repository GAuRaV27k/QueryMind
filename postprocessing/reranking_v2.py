import time
from flashrank import Ranker, RerankRequest

print("[reranker] Loading FlashRank...", flush=True)

_t0 = time.time()

ranker = Ranker()

print(
    f"[reranker] FlashRank ready in {time.time() - _t0:.1f}s",
    flush=True
)


async def reranker(results):

    print(
        f"[reranker] reranker() called with {len(results)} results",
        flush=True
    )

    if not results:
        return []

    query = results[0].query

    passages = []

    for idx, result in enumerate(results):
        passages.append({
            "id": idx,
            "text": result.content[:1500]
        })

    request = RerankRequest(
        query=query,
        passages=passages
    )

    ranked_passages = ranker.rerank(request)

    ranked_results = []

    for item in ranked_passages:

        result = results[item["id"]]

        result.rerank_score = float(
            item.get("score", 0.0)
        )

        ranked_results.append(result)

    print(
        f"[reranker] Top score = {ranked_results[0].rerank_score:.4f}",
        flush=True
    )

    return ranked_results


