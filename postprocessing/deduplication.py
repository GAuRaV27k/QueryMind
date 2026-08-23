from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


_TRACKING_PREFIXES = ("utm_", "gclid", "fbclid", "msclkid")


def _canonical_url(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    parsed = urlparse(text)
    query_items = [
        (key, val)
        for key, val in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith(_TRACKING_PREFIXES)
    ]
    cleaned = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        path=parsed.path.rstrip("/"),
        query=urlencode(query_items, doseq=True),
        fragment="",
    )
    return urlunparse(cleaned)


def deduplicate(results):
    if not results:
        return []
    
    """
    Return unique results based on url.
    Comparison is case-insensitive and ignores surrounding whitespace.
    """
    seen = set()
    unique = []

    for result in results:
        url = _canonical_url(getattr(result, "url", None))

        # Duplicate if the url has already been seen.
        if url and url in seen:
            continue

        if url:
            seen.add(url)

        unique.append(result)

    return unique
