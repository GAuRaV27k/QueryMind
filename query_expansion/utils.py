from __future__ import annotations

import ast
import json
import random
import re
from typing import Iterable, List

_BULLET_RE = re.compile(r"^\s*[-*•]\s+")
_NUMBERED_RE = re.compile(r"^\s*\d+[\.)]\s+")
_COMMENT_RE = re.compile(r"//.*?$|/\*.*?\*/", re.DOTALL | re.MULTILINE)
_TRAILING_COMMA_RE = re.compile(r",\s*(\]|\})")


def normalize_queries(original_query: str, expanded_queries: Iterable[str]) -> List[str]:
    combined: List[str] = []
    for item in expanded_queries:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        if cleaned:
            combined.append(cleaned)

    original_clean = original_query.strip()
    if original_clean and original_clean not in combined:
        combined.append(original_clean)

    seen = set()
    deduped: List[str] = []
    for query in combined:
        if query in seen:
            continue
        seen.add(query)
        deduped.append(query)

    return deduped


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip().lstrip("\ufeff")
    if not cleaned.startswith("```"):
        return cleaned
    cleaned = cleaned.strip("`").lstrip()
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].lstrip()
    return cleaned


def _extract_json_array(text: str) -> str | None:
    start = text.find("[")
    if start == -1:
        return None
    depth = 0
    in_string = False
    string_char = ""
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == string_char:
                in_string = False
            continue
        if char in ("'", '"'):
            in_string = True
            string_char = char
            continue
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def _clean_json_like(text: str) -> str:
    cleaned = _COMMENT_RE.sub("", text)
    cleaned = _TRAILING_COMMA_RE.sub(r"\1", cleaned)
    cleaned = cleaned.replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'")
    return cleaned


def parse_query_list(raw_text: str) -> List[str]:
    if not raw_text:
        return []
    cleaned = _strip_code_fences(raw_text)
    json_candidate = _extract_json_array(cleaned)
    if json_candidate:
        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(_clean_json_like(json_candidate))
            except (ValueError, SyntaxError, json.JSONDecodeError):
                continue
            if isinstance(parsed, list):
                items: List[str] = []
                for item in parsed:
                    if not isinstance(item, str):
                        item = str(item)
                    item = item.strip()
                    if item:
                        items.append(item)
                if items:
                    return items

    items: List[str] = []
    for line in re.split(r"\n+", cleaned):
        line = line.strip()
        if not line:
            continue
        line = _BULLET_RE.sub("", line)
        line = _NUMBERED_RE.sub("", line)
        if ";" in line:
            parts = [segment.strip() for segment in re.split(r";\s+(?=\w)", line)]
        else:
            parts = [line]
        for part in parts:
            if part:
                items.append(part)
    return items


_RETRYABLE_HINTS = (
    "rate limit",
    "too many requests",
    "temporarily",
    "timeout",
    "timed out",
    "unavailable",
    "service unavailable",
    "connection reset",
    "connection aborted",
    "connection refused",
)

_NON_RETRYABLE_HINTS = (
    "invalid api key",
    "authentication",
    "unauthorized",
    "forbidden",
    "permission",
    "invalid request",
    "bad request",
    "malformed",
)

_RETRYABLE_STATUS_CODES = {429, 503}
_NON_RETRYABLE_STATUS_CODES = {400, 401, 403, 404}


def _extract_status_code(exc: BaseException) -> int | None:
    for attr in ("status_code", "status", "code"):
        value = getattr(exc, attr, None)
        if value is None:
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def is_retryable_exception(exc: BaseException) -> bool:
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return True
    status_code = _extract_status_code(exc)
    if status_code in _RETRYABLE_STATUS_CODES:
        return True
    if status_code in _NON_RETRYABLE_STATUS_CODES:
        return False

    message = str(exc).lower()
    if any(hint in message for hint in _NON_RETRYABLE_HINTS):
        return False
    if any(hint in message for hint in _RETRYABLE_HINTS):
        return True
    if isinstance(exc, (ValueError, TypeError, KeyError)):
        return False
    return False


def compute_backoff(attempt: int, base_delay_s: float, max_delay_s: float, multiplier: float, jitter_s: float) -> float:
    delay = base_delay_s * (multiplier ** attempt)
    delay = min(delay, max_delay_s)
    if jitter_s <= 0:
        return delay
    return max(0.0, delay + random.uniform(-jitter_s, jitter_s))
