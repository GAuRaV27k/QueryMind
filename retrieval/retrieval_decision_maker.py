from pathlib import Path
import asyncio
from ast import literal_eval
from difflib import SequenceMatcher
import json
import logging
import os
import re
import sys
from typing import Dict, Iterable, List, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))




from translate_chunk.extended_queries import get_extended_query
from retrieval.retrieval_tool_capability import TOOL_CAPABILITIES
from retrieval.retrieval_plan import RetrievalPlan
from API.groq_client import client

logger = logging.getLogger(__name__)

# ================================================================================

INTENT_TAXONOMY = {
    "research": "Deep technical or academic investigation requiring semantic retrieval",
    "technical_comparison": "Comparing architectures, systems, or technical options",
    "conceptual": "Foundational explanations and abstract understanding",
    "freshness": "Time-sensitive or current information",
    "factoid": "Short factual lookup",
    "broad_web": "General web coverage, reviews, and consumer information",
    "coding": "Implementation guidance, code examples, repos, APIs",
}

ALLOWED_PRIORITIES = {"high", "medium", "low"}
# ================================================================================

SYSTEM_PROMPT = """You are a Retrieval Planner. Your job is to assign retrieval tools to queries.

Return ONLY a JSON array of objects. Do NOT return any prose or code fences.

Each object MUST include:
- query: string (must match one of the provided queries exactly)
- intent: string (use the intent taxonomy as guidance, but classify semantically)
- tools: array of tool names (subset of provided tools, multi-tool allowed)
- priority: "high" | "medium" | "low"
- reasoning: short string explaining the routing

Planning guidance:
- Prefer cost-aware routing: avoid high-cost tools unless depth is required.
- Prefer freshness-aware routing for time-sensitive queries.
- Prefer technical-depth routing for deep research/architecture/coding.
- Multi-intent queries may use multiple tools in a single plan item.
- Create exactly one plan per provided query.
"""

_FRESHNESS_KEYWORDS = (
    "latest",
    "recent",
    "today",
    "yesterday",
    "breaking",
    "news",
    "2024",
    "2025",
    "2026",
)
_COMPARISON_KEYWORDS = ("compare", "comparison", "vs", "versus", "difference", "differences")
_CODING_KEYWORDS = ("code", "implement", "implementation", "api", "sdk", "library", "github", "example")
_RESEARCH_KEYWORDS = (
    "paper",
    "research",
    "study",
    "architecture",
    "design",
    "system",
    "benchmark",
    "algorithm",
)
_CONCEPTUAL_KEYWORDS = ("concept", "overview", "principle", "theory", "explain", "definition")


def _tool_is_configured(tool_name: str) -> bool:
    name = (tool_name or "").lower()
    if name == "exa":
        return bool(os.getenv("EXA_API") or os.getenv("EXA_API_KEY"))
    if name == "tavily":
        return bool(os.getenv("TAVILY_API_KEY") or os.getenv("TRAVILY_API"))
    if name == "you":
        return bool(os.getenv("YOU_API_KEY") or os.getenv("YOU_PLATFORM"))
    return True


def _filter_tool_capabilities(tool_capabilities: Dict[str, dict]) -> Dict[str, dict]:
    filtered = {
        name: capability
        for name, capability in tool_capabilities.items()
        if _tool_is_configured(name)
    }
    if not filtered:
        raise ValueError(
            "No retrieval tools are configured. Set TAVILY_API_KEY (or TRAVILY_API), "
            "YOU_API_KEY (or YOU_PLATFORM), and/or EXA_API_KEY (or EXA_API)."
        )
    return filtered


def _get_model_name(model: str | None) -> str:
    return model or os.getenv("GROQ_PLANNER_MODEL") or os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant"







def _get_temperature() -> float:
    value = os.getenv("GROQ_PLANNER_TEMPERATURE", "0.05").strip()
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid GROQ_PLANNER_TEMPERATURE: {value}") from exc

# ================================================================================
def _normalize_queries(original_query: str, expanded_queries: Sequence[str] | None) -> List[str]:
    if not original_query or not original_query.strip():
        raise ValueError("Query cannot be empty")

    combined: List[str] = []
    if expanded_queries:
        for item in expanded_queries:
            if not isinstance(item, str):
                raise ValueError("Expanded queries must be a list of strings")
            cleaned = item.strip()
            if cleaned:
                combined.append(cleaned)

    original_clean = original_query.strip()
    if original_clean not in combined:
        combined.append(original_clean)

    seen = set()
    deduped: List[str] = []
    for query in combined:
        if query in seen:
            continue
        seen.add(query)
        deduped.append(query)

    return deduped

# Clean LLM output.
_COMMENT_RE = re.compile(r"//.*?$|/\*.*?\*/", re.DOTALL | re.MULTILINE)
_TRAILING_COMMA_RE = re.compile(r",\s*(\]|\})")


def _extract_json(raw_content: str) -> str:
    content = raw_content.strip().lstrip("\ufeff")
    if content.startswith("```"):
        content = content.strip("`").lstrip()
        if content.lower().startswith("json"):
            content = content[4:].lstrip()

    start = content.find("[")
    if start == -1:
        return content

    in_string = False
    string_char = ""
    escape = False
    depth = 0
    for index in range(start, len(content)):
        char = content[index]
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
                return content[start : index + 1]

    return content[start:]


def _clean_json_like(raw_content: str) -> str:
    cleaned = raw_content.strip().lstrip("\ufeff")
    cleaned = _COMMENT_RE.sub("", cleaned)
    cleaned = _TRAILING_COMMA_RE.sub(r"\1", cleaned)
    cleaned = cleaned.replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'")
    return cleaned


def _is_word_char(char: str) -> bool:
    return char.isalnum() or char == "_"


def _replace_unquoted_literals(text: str) -> str:
    replacements = {"true": "True", "false": "False", "null": "None"}
    output: List[str] = []
    index = 0
    in_string = False
    string_char = ""
    escape = False

    while index < len(text):
        char = text[index]
        if in_string:
            output.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == string_char:
                in_string = False
            index += 1
            continue

        if char in ("'", '"'):
            in_string = True
            string_char = char
            output.append(char)
            index += 1
            continue

        matched = False
        for literal, replacement in replacements.items():
            if text.startswith(literal, index):
                prev = text[index - 1] if index > 0 else ""
                next_char = text[index + len(literal)] if index + len(literal) < len(text) else ""
                if (not prev or not _is_word_char(prev)) and (not next_char or not _is_word_char(next_char)):
                    output.append(replacement)
                    index += len(literal)
                    matched = True
                    break

        if matched:
            continue

        output.append(char)
        index += 1

    return "".join(output)


def _loads_json_payload(raw_content: str) -> object:
    extracted = _extract_json(raw_content)
    try:
        return json.loads(extracted)
    except json.JSONDecodeError:
        cleaned = _clean_json_like(extracted)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            try:
                return literal_eval(_replace_unquoted_literals(cleaned))
            except (SyntaxError, ValueError) as literal_exc:
                raise exc from literal_exc


def _normalize_query_key(query: str) -> str:
    cleaned = query.strip().lower()
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _resolve_expected_query(query: str, expected_queries: Sequence[str]) -> str | None:
    if not expected_queries:
        return None

    if query in expected_queries:
        return query

    normalized_query = _normalize_query_key(query)
    normalized_map: Dict[str, List[str]] = {}
    for expected in expected_queries:
        key = _normalize_query_key(expected)
        normalized_map.setdefault(key, []).append(expected)

    if normalized_query in normalized_map:
        return normalized_map[normalized_query][0]

    candidates: List[str] = []
    for expected in expected_queries:
        expected_key = _normalize_query_key(expected)
        if normalized_query and (expected_key in normalized_query or normalized_query in expected_key):
            candidates.append(expected)
    if len(candidates) == 1:
        return candidates[0]

    best_ratio = 0.0
    best_match: str | None = None
    for expected in expected_queries:
        expected_key = _normalize_query_key(expected)
        if not expected_key or not normalized_query:
            continue
        ratio = SequenceMatcher(None, normalized_query, expected_key).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = expected

    threshold = 0.7 if len(expected_queries) > 1 else 0.6
    if best_match and best_ratio >= threshold:
        return best_match

    return None


def _classify_intent(query: str) -> str:
    lowered = query.lower()
    if any(keyword in lowered for keyword in _FRESHNESS_KEYWORDS):
        return "freshness"
    if any(keyword in lowered for keyword in _COMPARISON_KEYWORDS):
        return "technical_comparison"
    if any(keyword in lowered for keyword in _CODING_KEYWORDS):
        return "coding"
    if any(keyword in lowered for keyword in _RESEARCH_KEYWORDS):
        return "research"
    if any(keyword in lowered for keyword in _CONCEPTUAL_KEYWORDS):
        return "conceptual"
    return "broad_web"


def _select_tools(intent: str, available_tools: List[str]) -> List[str]:
    def pick(*names: str) -> str | None:
        for name in names:
            if name in available_tools:
                return name
        return available_tools[0] if available_tools else None

    if intent == "freshness":
        tool = pick("tavily", "you", "exa")
        return [tool] if tool else []
    if intent == "technical_comparison":
        tools = [tool for tool in ("exa", "you") if tool in available_tools]
        if tools:
            return tools
        tool = pick("you", "tavily", "exa")
        return [tool] if tool else []
    if intent in {"research", "conceptual", "coding"}:
        tool = pick("exa", "you", "tavily")
        return [tool] if tool else []
    if intent == "factoid":
        tool = pick("tavily", "you", "exa")
        return [tool] if tool else []
    tool = pick("you", "tavily", "exa")
    return [tool] if tool else []


def _fallback_plan_for_query(query: str, available_tools: List[str]) -> RetrievalPlan:
    intent = _classify_intent(query)
    tools = _select_tools(intent, available_tools)
    if not tools:
        raise ValueError("No retrieval tools available for fallback planning")
    if intent == "freshness":
        priority = "high"
    elif intent in {"research", "technical_comparison", "conceptual", "coding"}:
        priority = "medium"
    else:
        priority = "low"
    return RetrievalPlan(
        query=query,
        intent=intent,
        tools=tools,
        priority=priority,
        reasoning="Fallback heuristic routing (planner output invalid).",
    )


def _validate_plan_item(
    item: Dict[str, object],
    allowed_tools: Iterable[str],
    expected_queries: Sequence[str],
) -> RetrievalPlan:
    query = item.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Each plan must include a non-empty query string")
    query = query.strip()
    resolved_query = _resolve_expected_query(query, expected_queries)
    if resolved_query is None:
        raise ValueError(f"Plan query must match provided queries. Unknown query: {query}")
    query = resolved_query

    intent = item.get("intent")
    if not isinstance(intent, str) or not intent.strip():
        raise ValueError("Each plan must include a non-empty intent string")
    intent = intent.strip().lower().replace(" ", "_")

    priority = item.get("priority")
    if not isinstance(priority, str) or not priority.strip():
        raise ValueError("Each plan must include a non-empty priority string")
    priority = priority.strip().lower()
    if priority not in ALLOWED_PRIORITIES:
        raise ValueError(f"Priority must be one of {sorted(ALLOWED_PRIORITIES)}")

    tools = item.get("tools")
    if not isinstance(tools, list) or not tools:
        raise ValueError("Each plan must include a non-empty tools array")

    normalized_tools: List[str] = []
    allowed_tool_set = {tool.lower() for tool in allowed_tools}
    for tool in tools:
        if not isinstance(tool, str) or not tool.strip():
            raise ValueError("Tools must be non-empty strings")
        tool_name = tool.strip().lower()
        if tool_name not in allowed_tool_set:
            raise ValueError(f"Unknown tool in plan: {tool_name}")
        if tool_name not in normalized_tools:
            normalized_tools.append(tool_name)

    reasoning = item.get("reasoning")
    if not isinstance(reasoning, str) or not reasoning.strip():
        raise ValueError("Each plan must include a non-empty reasoning string")
    reasoning = reasoning.strip()

    return RetrievalPlan(
        query=query,
        intent=intent,
        tools=normalized_tools,
        priority=priority,
        reasoning=reasoning,
    )

# Convert raw LLM response into objects.
def _parse_plans(
    raw_content: str,
    allowed_tools: Iterable[str],
    expected_queries: List[str],
) -> List[RetrievalPlan]:
    allowed_tools_list = [tool.lower() for tool in allowed_tools]
    parsed = _loads_json_payload(raw_content)
    if not isinstance(parsed, list):
        raise ValueError("Planner output must be a JSON array")

    expected_query_set = set(expected_queries)
    plans = [
        _validate_plan_item(item, allowed_tools_list, expected_queries)
        for item in parsed
        if isinstance(item, dict)
    ]
    if len(plans) != len(parsed):
        raise ValueError("Planner output must be an array of objects")

    deduped: Dict[str, RetrievalPlan] = {}
    duplicates: List[str] = []
    for plan in plans:
        if plan.query in deduped:
            duplicates.append(plan.query)
            continue
        deduped[plan.query] = plan
    if duplicates:
        logger.warning("Planner output contained duplicate plans for queries: %s", duplicates)

    missing = expected_query_set.difference(deduped.keys())
    if missing:
        logger.warning("Planner output missing plans for queries: %s", sorted(missing))
        for query in missing:
            deduped[query] = _fallback_plan_for_query(query, allowed_tools_list)

    return [deduped[query] for query in expected_queries if query in deduped]


def _build_messages(
    original_query: str,
    expanded_queries: List[str],
    tool_capabilities: Dict[str, dict],
) -> List[Dict[str, str]]:
    payload = {
        "original_query": original_query,
        "expanded_queries": expanded_queries[:3],
        "tool_capabilities": tool_capabilities,
        "intent_taxonomy": INTENT_TAXONOMY,
        "priority_levels": sorted(ALLOWED_PRIORITIES),
        "available_tools": sorted(tool_capabilities.keys()),
    }
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def _call_planner(messages: List[Dict[str, str]], model: str) -> str:
    response = client.chat.completions.create(









        model=model,
        messages=messages,
        temperature=_get_temperature(),



    )
    content = response.choices[0].message.content if response.choices else None


    if not content:
        raise RuntimeError("Groq planner returned an empty response")
    return content




def _plan_with_retries(
    messages: List[Dict[str, str]],
    model: str,
    allowed_tools: Iterable[str],
    expected_queries: List[str],
    max_retries: int,
) -> List[RetrievalPlan]:
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        content = _call_planner(messages, model)
        try:
            return _parse_plans(content, allowed_tools, expected_queries)
        except (ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt >= max_retries:
                break
            messages.extend(
                [
                    {"role": "assistant", "content": content},
                    {
                        "role": "user",
                        "content": (
                            "Your previous response was invalid. "
                            f"Fix it and return ONLY a valid JSON array. Error: {exc}"
                        ),
                    },
                ]
            )
    raise ValueError(f"Failed to produce a valid retrieval plan: {last_error}")


def plan_retrieval(
    query: str,
    expanded_queries: Sequence[str] | None = None,
    tool_capabilities: Dict[str, dict] | None = None,
    model: str | None = None,
    max_retries: int = 2,
) -> List[RetrievalPlan]:
    if expanded_queries is None:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            expanded_queries = asyncio.run(get_extended_query(query))
        else:
            raise RuntimeError(
                "plan_retrieval cannot run inside an event loop. Use plan_retrieval_async instead."
            )

    capabilities = _filter_tool_capabilities(tool_capabilities or TOOL_CAPABILITIES)
    normalized_queries = _normalize_queries(query, expanded_queries)
    messages = _build_messages(query, normalized_queries, capabilities)
    model_name = _get_model_name(model)
    return _plan_with_retries(
        messages,
        model_name,
        capabilities.keys(),
        normalized_queries,
        max_retries,
    )


async def plan_retrieval_async(
    query: str,
    expanded_queries: Sequence[str] | None = None,
    tool_capabilities: Dict[str, dict] | None = None,
    model: str | None = None,
    max_retries: int = 2,
) -> List[RetrievalPlan]:
    if expanded_queries is None:
        expanded_queries = await get_extended_query(query)

    capabilities = _filter_tool_capabilities(tool_capabilities or TOOL_CAPABILITIES)
    normalized_queries = _normalize_queries(query, expanded_queries)
    messages = _build_messages(query, normalized_queries, capabilities)
    model_name = _get_model_name(model)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _plan_with_retries,
        messages,
        model_name,
        capabilities.keys(),
        normalized_queries,
        max_retries,
    )



if __name__ == "__main__":

    query = input("Enter Query: ").strip()

    plans = plan_retrieval(query)

    print("\nRetrieval Plans:")
    print("=" * 50)

    for plan in plans:

        print(f"\nQuery: {plan.query}")
        print(f"Intent: {plan.intent}")
        print(f"Tools: {plan.tools}")
        print(f"Priority: {plan.priority}")
        print(f"Reason: {plan.reasoning}")
