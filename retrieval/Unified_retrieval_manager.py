from dataclasses import dataclass
from typing import Iterable

@dataclass
class UnifiedRetrievalResult:
    title: str
    url: str
    content: str

    provider: str

    query: str
    intent: str
    priority: str

    fusion_score: int = 1
    rerank_score : float =0.0
    score: float | None = None
    published_date: str | None = None


def _get_value(item: object, key: str):
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def _get_first(item: object, keys: Iterable[str]):
    for key in keys:
        value = _get_value(item, key)
        if value is not None:
            return value
    return None


def _pick_str(*values: object) -> str | None:
    for value in values:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                return stripped
    return None


def _pick_text(*values: object) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, list):
            joined = " ".join(
                str(item).strip() for item in value if str(item).strip()
            ).strip()
            if joined:
                return joined
            continue
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                return stripped
    return ""


def _coerce_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _extract_items(response: object, keys: Iterable[str]) -> list:
    if response is None:
        return []

    if isinstance(response, list):
        return response
    if isinstance(response, tuple):
        return list(response)

    if isinstance(response, dict):
        for key in keys:
            if key not in response:
                continue
            value = response.get(key)
            if value is None:
                continue
            if isinstance(value, list):
                return value
            if isinstance(value, tuple):
                return list(value)
            return [value]

    for key in keys:
        value = getattr(response, key, None)
        if value is None:
            continue
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]

    return []


def _normalize_items(
    items: list,
    provider: str,
    query: str,
    intent: str,
    priority: str,
) -> list[UnifiedRetrievalResult]:
    results: list[UnifiedRetrievalResult] = []

    for item in items:
        title = _pick_str(
            _get_first(item, ("title", "name")),
        )
        url = _pick_str(
            _get_first(item, ("url", "link", "href")),
        )
        content = _pick_text(
            _get_first(item, ("content", "snippet", "description", "summary", "text", "answer")),
            _get_first(item, ("highlights",)),
            _get_first(item, ("raw_content", "rawContent", "page_content", "pageContent")),
        )

        if not title and not url and not content:
            continue

        score = _coerce_float(_get_first(item, ("score", "relevance", "rank")))
        published_date = _pick_str(
            _get_first(item, ("published_date", "publishedDate", "publishedAt", "date"))
        )

        results.append(
            UnifiedRetrievalResult(
                title=title or "",
                url=url or "",
                content=content,
                provider=provider,
                query=query,
                intent=intent,
                priority=priority,
                score=score,
                published_date=published_date,
            )
        )

    return results


def normalize_provider_output(
    provider: str,
    response: object,
    query: str,
    intent: str,
    priority: str,
) -> list[UnifiedRetrievalResult]:
    provider = (provider or "").lower()

    if provider == "tavily":
        items = _extract_items(response, ("results", "data"))
        return _normalize_items(items, provider, query, intent, priority)

    if provider == "you":
        items = _extract_items(response, ("results", "search_results", "web_results", "items"))
        return _normalize_items(items, provider, query, intent, priority)

    if provider == "exa":
        items = _extract_items(response, ("results",))
        return _normalize_items(items, provider, query, intent, priority)

    raise ValueError(f"Unsupported provider: {provider}")


def normalize_provider_bundle(bundle: dict) -> list[UnifiedRetrievalResult]:
    return normalize_provider_output(
        bundle.get("provider", ""),
        bundle.get("response"),
        bundle.get("query", ""),
        bundle.get("intent", ""),
        bundle.get("priority", ""),
    )