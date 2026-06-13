GOOD.
This is now becoming the real “brain layer” of your retrieval system.

And this layer is VERY important because it determines:

```text id="m4x7qp"
retrieval efficiency
+
retrieval quality
+
cost
+
latency
+
signal-to-noise ratio
```

This is where your system starts becoming:

```text id="p9w2mk"
intelligent retrieval orchestration
```

instead of:

```text id="f3q8xn"
blind multi-search
```

---

# First Understand What This Layer REALLY IS

The:

# RetrievalDecisionMaker

is basically:

```text id="u6m1wp"
retrieval planning engine
```

Its job is NOT to search.

Its job is:

```text id="n2q7xk"
decide HOW retrieval should happen
```

VERY important distinction.

---

# Core Philosophy

Instead of:

```text id="q5m9wn"
every query
→ every provider
```

You now want:

```text id="k8q4xp"
right query
→ right provider
```

This is MUCH smarter.

---

# Main Responsibilities of RetrievalDecisionMaker

This layer should ONLY handle:

---

# 1. Query Understanding

Understand:

* query intent
* query depth
* freshness need
* semantic complexity
* research nature

---

# 2. Provider Capability Matching

Understand:

* Exa strengths
* Tavily strengths
* You strengths

---

# 3. Retrieval Planning

Create:

```text id="w1m7qz"
query-provider assignments
```

---

# 4. Retrieval Strategy

Decide:

* shallow search?
* deep research?
* multi-provider?
* semantic-first?
* broad retrieval?

---

# What This Layer SHOULD NOT DO

DO NOT:

* execute retrieval
* normalize results
* aggregate results
* rerank
* crawl

That belongs to:

```text id="r4q2wm"
RetrievalManager
```

---

# Recommended Architecture

---

# INPUT

```python id="h7m8xq"
[
   original_query,
   expanded_queries
]
```

Example:

```python id="j3q5wp"
[
    "Google I/O 2026 AI highlights",

    "Google AI product announcements",

    "Strategic AI roadmap from Google",

    "How do AI conferences influence the industry?"
]
```

---

# OUTPUT

A:

# Retrieval Plan

Example:

```python id="v9m1xk"
[
    {
        "query": "Google I/O 2026 AI highlights",
        "providers": ["tavily"],
        "priority": "freshness"
    },

    {
        "query": "Strategic AI roadmap from Google",
        "providers": ["exa"],
        "priority": "research"
    },

    {
        "query": "How do AI conferences influence the industry?",
        "providers": ["exa", "you"],
        "priority": "conceptual"
    }
]
```

THIS is the core output.

---

# IMPORTANT DESIGN PRINCIPLE

The RetrievalDecisionMaker should return:

```text id="c2m7wp"
instructions
```

NOT results.

This is CRITICAL architecture separation.

---

# What You Need To Design FIRST

Before coding:
define:

---

# 1. Query Categories

Your system needs:

```text id="f6q9xn"
query taxonomy
```

Start SIMPLE.

---

# Recommended Initial Query Types

---

# A. Freshness Query

Keywords:

```text id="x3m4wk"
latest
today
2026
recent
announcement
news
```

Needs:

```text id="u8q1xp"
fresh web retrieval
```

Provider:

```text id="r5m7wn"
Tavily
```

---

# B. Research Query

Keywords:

```text id="n9q2wm"
architecture
research
framework
paper
technical
```

Needs:

```text id="z4m8xk"
semantic retrieval
```

Provider:

```text id="j7q5wp"
Exa
```

---

# C. Broad Web Query

Needs:

```text id="p1m9xn"
general coverage
```

Provider:

```text id="v6q3wm"
You
```

---

# D. Conceptual Query

Usually:

* step-back queries
* abstraction queries

Needs:

```text id="h2m7xq"
deep semantic retrieval
```

Provider:

```text id="k8q4wp"
Exa
```

---

# FIRST RULE

Keep classification:

```text id="c5m1zn"
rule-based initially
```

DO NOT use LLM classification yet.

---

# Next Design Requirement

# Provider Capability Registry

VERY important.

You need a system-wide understanding of:

```text id="x9m2wk"
what each provider is good at
```

---

# Example

```python id="w4q7xm"
PROVIDER_CAPABILITIES = {

    "exa": {
        "semantic": True,
        "research": True,
        "freshness": False,
        "cost": "high"
    },

    "tavily": {
        "freshness": True,
        "fast": True,
        "research": False
    },

    "you": {
        "broad_search": True
    }
}
```

VERY important future foundation.

---

# NEXT DESIGN REQUIREMENT

# RetrievalPlan Schema

You need a formal structure.

---

# Example

```python id="t6m8xq"
@dataclass
class RetrievalPlan:

    query: str

    providers: List[str]

    intent: str

    priority: str

    top_k: int = 5
```

This becomes:

```text id="q3m1wp"
retrieval execution instructions
```

---

# Suggested Folder Structure

```text id="u7q4xn"
retrieval/
│
├── decision/
│   ├── retrieval_decision_maker.py
│   ├── query_classifier.py
│   ├── provider_registry.py
│   └── retrieval_plan.py
│
├── manager/
│   └── retrieval_manager.py
```

VERY clean architecture.

---

# Internal Pipeline

Your DecisionMaker flow should become:

```text id="f9m2wk"
Expanded Queries
   ↓
Query Classification
   ↓
Capability Matching
   ↓
Retrieval Planning
   ↓
Return Retrieval Plans
```

---

# IMPORTANT DESIGN THINKING

This layer should optimize:

---

# 1. Retrieval Quality

Right provider for right query.

---

# 2. Cost

Avoid:

```text id="j5q7xm"
8 queries × 3 providers
```

---

# 3. Latency

Reduce unnecessary calls.

---

# 4. Noise Reduction

Avoid:

* duplicate retrieval
* weak retrieval
* irrelevant results

---

# Initial Implementation Recommendation

DO NOT overcomplicate.

---

# PHASE 1 DecisionMaker

Use:

* keyword heuristics
* simple query rules
* provider mapping

ONLY.

---

# Example

```python id="k1m8wp"
if "latest" in query:
    use tavily

elif "research" in query:
    use exa

else:
    use you
```

This is enough initially.

---

# PHASE 2

Later add:

* embedding similarity
* query embeddings
* LLM routing
* adaptive routing

NOT now.

---

# MOST IMPORTANT DESIGN PRINCIPLE

Your architecture is now becoming:

```text id="r8q3xn"
PLAN
   ↓
EXECUTE
```

This is VERY strong systems architecture.

---

# Final Architecture

---

# Query Expansion Layer

Generates retrieval opportunities.

---

# RetrievalDecisionMaker

Creates retrieval strategy.

---

# RetrievalManager

Executes retrieval strategy.

---

# Retrieval Pool

Unified retrieval results.

---

# Future Layers

* reranking
* fusion
* grounding
* synthesis

---

# Biggest Insight

You are now designing:

```text id="w2m9xk"
retrieval routing infrastructure
```

This is MUCH more advanced than:

```text id="v7q1wp"
basic RAG pipelines
```

and honestly MUCH closer to how real retrieval-first AI systems evolve internally.
