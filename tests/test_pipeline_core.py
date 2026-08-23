from generation.context_builder import build_context
from generation.cititation_map import build_citation_map
from postprocessing.deduplication import deduplicate
from postprocessing.fusion import fuse_results
from retrieval.Unified_retrieval_manager import UnifiedRetrievalResult
from query_expansion.utils import normalize_queries, parse_query_list


def mk(url, title="t", content="c", score=1.0, provider="exa", query="q"):
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


def test_normalize_queries_preserves_original():
    out = normalize_queries("orig", ["a", "orig", "b"])
    assert out[0] == "a"
    assert "orig" in out


def test_parse_query_list_handles_json_and_bullets():
    assert parse_query_list('["a", "b"]') == ["a", "b"]
    assert parse_query_list("- a\n- b") == ["a", "b"]


def test_fusion_uses_canonical_url():
    results = [mk("https://example.com/a?utm_source=x"), mk("https://example.com/a")]
    fused = fuse_results(results)
    assert fused[0].fusion_score == 2


def test_deduplication_removes_tracking_variants():
    results = [mk("https://example.com/a?utm_source=x"), mk("https://example.com/a")]
    assert len(deduplicate(results)) == 1


def test_context_and_citations_use_stable_source_ids():
    results = [mk("https://example.com/a"), mk("https://example.com/b")]
    context = build_context(results)
    citations = build_citation_map(results)
    assert "[Source S1]" in context
    assert citations["S1"]["url"] == "https://example.com/a"
