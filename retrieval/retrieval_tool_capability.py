"""Compact capability registry for retrieval providers."""

TOOL_CAPABILITIES = {
    "exa": {
        "best_for": [
            "research",
            "technical",
            "academic papers",
            "github repositories",
            "deep semantic retrieval",
        ],
        "cost": "high",
        "freshness": "medium",
    },
    "tavily": {
        "best_for": [
            "news",
            "real-time information",
            "recent events",
            "fact lookup",
        ],
        "cost": "low",
        "freshness": "high",
    },
    "you": {
        "best_for": [
            "broad web search",
            "reviews",
            "comparisons",
            "consumer information",
        ],
        "cost": "low",
        "freshness": "medium",
    },
}

# Backwards-compatible alias
RETRIEVAL_TOOL_CAPABILITIES = TOOL_CAPABILITIES