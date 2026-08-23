import asyncio

from generation.cititation_map import append_references, build_citation_map
from generation.context_builder import build_context
from postprocessing.deduplication import deduplicate
from postprocessing.fusion import fuse_result
from postprocessing.reranking_v2 import reranker
from query_expansion.manager.query_expansion_manager import QueryExpansionManager
from query_expansion.types import QueryExpansionProvider
from retrieval.Unified_retrieval_manager import UnifiedRetrievalResult
from retrieval.retrieval_decision_maker import plan_retrieval
from retrieval.retrieval_manager import retrivel_search_with_trace
from retrieval.retrieval_plan import RetrievalPlan


def _run(coro):
    return asyncio.run(coro)


def _bundle(provider, query, status="success", response=None, error=None):
    return {
        "provider": provider,
        "query": query,
        "intent": "research",
        "priority": "high",
        "status": status,
        "response": response,
        "error": error,
    }


def _item(url, title, content, score=0.5, provider="exa", query="q"):
    return UnifiedRetrievalResult(
        title=title,
        url=url,
        content=content,
        provider=provider,
        query=query,
        intent="research",
        priority="high",
        score=score,
    )


def _provider_success_bundle(provider, query, url, title):
    return _bundle(
        provider,
        query,
        response={"results": [{"title": title, "url": url, "content": f"{title} content", "score": 0.8}]},
    )


def _mock_plan_with_all(query):
    return [
        RetrievalPlan(
            query=query,
            intent="research",
            tools=["tavily", "exa", "you"],
            priority="high",
            reasoning="test plan",
        )
    ]


async def _async_return(value):
    return value


def test_all_providers_succeed(monkeypatch):
    query = "latest battery breakthrough"
    async def _plan(_):
        return _mock_plan_with_all(query)
    monkeypatch.setattr("retrieval.retrieval_manager.plan_retrieval_async", _plan)
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_tavily",
        lambda *args: _async_return(_provider_success_bundle("tavily", query, "https://a.com", "A")),
    )
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_exa",
        lambda *args: _async_return(_provider_success_bundle("exa", query, "https://b.com", "B")),
    )
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_you",
        lambda *args: _async_return(_provider_success_bundle("you", query, "https://c.com", "C")),
    )

    traced = _run(retrivel_search_with_trace(query))
    assert len(traced["failures"]) == 0
    assert len(traced["results"]) == 3
    assert traced["metrics"]["normalized_count"] == 3


def test_provider_failure_degrades_gracefully(monkeypatch):
    query = "news update"
    async def _plan(_):
        return _mock_plan_with_all(query)
    monkeypatch.setattr("retrieval.retrieval_manager.plan_retrieval_async", _plan)
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_tavily",
        lambda *args: _async_return(_bundle("tavily", query, status="failed", error="timeout", response=None)),
    )
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_exa",
        lambda *args: _async_return(_provider_success_bundle("exa", query, "https://b.com", "B")),
    )
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_you",
        lambda *args: _async_return(_provider_success_bundle("you", query, "https://c.com", "C")),
    )

    traced = _run(retrivel_search_with_trace(query))
    assert any(item["provider"] == "tavily" for item in traced["failures"])
    assert len(traced["results"]) == 2


def test_exa_failure_degrades_gracefully(monkeypatch):
    query = "technical research"
    async def _plan(_):
        return _mock_plan_with_all(query)
    monkeypatch.setattr("retrieval.retrieval_manager.plan_retrieval_async", _plan)
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_tavily",
        lambda *args: _async_return(_provider_success_bundle("tavily", query, "https://a.com", "A")),
    )
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_exa",
        lambda *args: _async_return(_bundle("exa", query, status="failed", error="api error", response=None)),
    )
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_you",
        lambda *args: _async_return(_provider_success_bundle("you", query, "https://c.com", "C")),
    )
    traced = _run(retrivel_search_with_trace(query))
    assert any(item["provider"] == "exa" for item in traced["failures"])
    assert len(traced["results"]) == 2


def test_you_failure_degrades_gracefully(monkeypatch):
    query = "ambiguous apple model"
    async def _plan(_):
        return _mock_plan_with_all(query)
    monkeypatch.setattr("retrieval.retrieval_manager.plan_retrieval_async", _plan)
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_tavily",
        lambda *args: _async_return(_provider_success_bundle("tavily", query, "https://a.com", "A")),
    )
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_exa",
        lambda *args: _async_return(_provider_success_bundle("exa", query, "https://b.com", "B")),
    )
    monkeypatch.setattr(
        "retrieval.retrieval_manager._call_you",
        lambda *args: _async_return(_bundle("you", query, status="failed", error="bad response", response=None)),
    )
    traced = _run(retrivel_search_with_trace(query))
    assert any(item["provider"] == "you" for item in traced["failures"])
    assert len(traced["results"]) == 2


def test_dedup_with_same_url_across_providers():
    results = [
        _item("https://x.com/a", "A1", "content1", provider="tavily"),
        _item("https://x.com/a", "A2", "content2", provider="exa"),
        _item("https://x.com/b", "B", "content3", provider="you"),
    ]
    deduped = deduplicate(fuse_result(results))
    assert len(deduped) == 2


def test_dedup_with_tracking_variants():
    results = [
        _item("https://x.com/a?utm_source=social", "A1", "content1"),
        _item("https://x.com/a?fbclid=123", "A2", "content2"),
    ]
    assert len(deduplicate(fuse_result(results))) == 1


class _MockRanker:
    def rerank(self, request):
        return [
            {"id": 2, "score": 0.91},
            {"id": 0, "score": 0.51},
            {"id": 1, "score": 0.33},
        ]


def test_reranking_changes_order_and_preserves_metadata():
    results = [
        _item("https://x.com/1", "Doc1", "c1", provider="tavily"),
        _item("https://x.com/2", "Doc2", "c2", provider="exa"),
        _item("https://x.com/3", "Doc3", "c3", provider="you"),
    ]
    reranked = _run(reranker(results, ranker_instance=_MockRanker()))
    assert [item.url for item in reranked] == ["https://x.com/3", "https://x.com/1", "https://x.com/2"]
    assert reranked[0].title == "Doc3"
    assert reranked[0].provider == "you"
    assert reranked[0].rerank_score == 0.91


def test_empty_retrieval_returns_empty(monkeypatch):
    query = "no tools"
    async def _plan(_):
        return []
    monkeypatch.setattr("retrieval.retrieval_manager.plan_retrieval_async", _plan)
    traced = _run(retrivel_search_with_trace(query))
    assert traced["results"] == []
    assert traced["provider_bundles"] == []


def test_malformed_planner_falls_back(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "dummy")
    monkeypatch.setattr("retrieval.retrieval_decision_maker._plan_with_retries", lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("bad json")))
    plans = plan_retrieval("what is rag", expanded_queries=["what is rag"])
    assert len(plans) == 1
    assert plans[0].query == "what is rag"
    assert plans[0].tools


class _FailingProvider(QueryExpansionProvider):
    name = "failing"
    priority = 1

    async def expand(self, query: str):
        raise ValueError("malformed expansion")


def test_malformed_expansion_keeps_original_query():
    manager = QueryExpansionManager(providers=[_FailingProvider()])
    result = _run(manager.expand_with_metadata("query"))
    assert result.fallback_used is True
    assert result.queries == ["query"]


def test_invalid_citations_are_sanitized():
    results = [
        _item("https://x.com/1", "Doc1", "content"),
        _item("https://x.com/2", "Doc2", "content"),
    ]
    citation_map = build_citation_map(results)
    answer = "Claim [S1]. Unsupported [S9]."
    output = append_references(answer, citation_map)
    assert "[S1]" in output
    assert "[S9]" not in output
    assert "[citation unavailable]" in output


def test_mocked_end_to_end_pipeline_properties():
    query = "Compare RAG and fine-tuning for production chatbots"
    results = [
        _item("https://x.com/rag", "RAG Guide", "retrieval improves freshness", provider="tavily", query=query),
        _item("https://x.com/ft", "Fine-tuning Guide", "fine-tuning improves style", provider="exa", query=query),
    ]
    reranked = _run(reranker(results, ranker_instance=_MockRanker()))
    context = build_context(reranked)
    citation_map = build_citation_map(reranked)
    answer = append_references("Use retrieval for freshness [S1] and tuning for style [S2].", citation_map)
    assert query == reranked[0].query
    assert len(context) > 0
    assert "[Source S1]" in context
    assert "[S1]" in answer and "[S2]" in answer
