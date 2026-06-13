# Project Overview

This repository is an **early-stage skeleton** of a Perplexity-style retrieval and research backend, currently centered on **query transformation + multi-provider search connectors** rather than a full end-to-end agentic RAG product. The implemented core is a small FastAPI surface (`API\main.py`) plus provider wrappers for Gemini, Tavily, You.com, and Exa (`API\*.py`, `search\provider\*.py`).

# Vision & System Direction

The intended direction is clear from `readme.txt` and `API\Exa.txt`:  
**retrieval-first AI system** with multi-query expansion, step-back prompting, provider fusion, crawling, extraction, reranking, and synthesis.

Current maturity is **pre-MVP architecture prototype**: the design intent is ambitious and modern, but most production-critical layers are still unimplemented.

# Current Architecture

Current real runtime architecture:

```text
Client
  -> FastAPI (API\main.py)
      -> /query stores query in process-global variable
      -> /multi_query calls Gemini for query variants
      -> /step_back calls Gemini for broader conceptual questions
```

Planned/aspirational architecture (from `readme.txt`):

```text
User Query
   ↓
Query Transformation
   ├── Original Query
   ├── Multi Queries
   └── Step-back Query
   ↓
Multi Search Providers (Tavily / You / Exa)
   ↓
Normalize + Deduplicate + Fusion
   ↓
Crawling/Extraction
   ↓
Reranking
   ↓
LLM Synthesis + Citations
```

**Updated/Enhanced Pipeline Architecture** (from `status.txt` — representing evolved design intent):

```text
User Query
   ↓
Query Expansion Layer
(Multi-query + Step-back)
   ↓
Query Intent Classification
   ↓
Retrieval Planning Engine
   ↓
Provider Routing
   ↓
Async Parallel Retrieval
   ↓
Web Crawling / Extraction
   ↓
Result Aggregation
   ↓
Deduplication
   ↓
Fusion / Reranking
   ↓
Context Compression
   ↓
Grounded Generation
   ↓
Final Response
```

The enhanced pipeline introduces several missing layers:
- **Query Intent Classification** — route queries to appropriate retrieval depth/strategy
- **Retrieval Planning Engine** — decide which providers/strategies to use
- **Provider Routing** — intelligent provider selection per query
- **Async Parallel Retrieval** — concurrent fanout across multiple providers
- **Context Compression** — prepare retrieved context for generation within token limits

This design represents a significant evolution from the simple linear pipeline, incorporating agentic planning and dynamic provider orchestration.

# Folder Structure Breakdown

```text
API\
  main.py             # FastAPI entrypoints for query + query transforms
  gemini_client.py    # Gemini client bootstrap via env key
  travily_client.py   # Tavily client bootstrap
  you_client.py       # You.com client bootstrap + test print
  exa_client.py       # Exa client bootstrap
  Exa.txt             # Exa integration notes/docs (non-runtime)

retrieval\
  retrieval_manager.py # Async orchestrator for parallel query transformations (NEW)

search\
  search_manager.py   # orchestration scratch file with provider imports + print
  provider\
    travily.py        # tavily search wrapper
    you.py            # you.com search wrapper
    exa.py            # exa search wrapper

schema\
  URS.py              # Unified RetrievalResult dataclass schema (NEW)

translate_chunk\
  multi_query.py      # Gemini prompt for 4 query rewrites
  step_back.py        # Gemini prompt for 3 broader questions

.vscode\
  settings.json       # VS Code Python environment config (NEW)
```

Observations:
- **NEW:** `schema\URS.py` introduces a unified result schema for normalizing outputs across providers.
- **NEW:** `.vscode\settings.json` configures Python environment (conda-based development).
- No frontend directory exists.
- No database layer exists.
- No tests, CI config, Docker, dependency lockfile, or deployment manifests are present.
- `__pycache__` is committed, indicating immature repo hygiene.

# Backend Architecture

Backend is a single-process FastAPI app (`API\main.py`) with three endpoints:
- `POST /query` stores normalized query in `qUERY` global (`API\main.py:16,23-27`)
- `POST /multi_query` depends on global query, calls `generate_multiquery` (`API\main.py:30-42`)
- `POST /step_back` depends on global query, calls `stepback` (`API\main.py:45-58`)

Key architectural issues:
- **Stateful API design** via process-global variable breaks stateless HTTP semantics and multi-user isolation.
- Endpoint dependency order (`/query` must be called first) is brittle.
- No auth, rate-limiting, validation hardening, exception mapping, observability, or request tracing.

# AI/RAG Pipeline

Implemented AI behavior:
- LLM-powered query rewriting (`translate_chunk\multi_query.py:12-31`)
- LLM-powered abstraction/step-back generation (`translate_chunk\step_back.py:11-25`)

Not implemented:
- Retrieval augmentation loop into generation
- Context assembly
- Citation-grounded synthesis endpoint
- Memory/session reasoning
- RAG chunking/indexing/retrieval lifecycle

Conclusion: this is **RAG-adjacent query preprocessing**, not yet a RAG pipeline.

# Retrieval Pipeline

## Unified Result Schema (NEW)

`schema\URS.py` defines a `RetrievalResult` dataclass that normalizes outputs across all search providers:

```python
@dataclass
class RetrievalResult:
    # Core Result
    title: str
    url: str
    snippet: str
    
    # Provider Info
    provider: str
    query: str
    
    # Ranking
    rank: int
    score: Optional[float] = None
    
    # Rich Content
    summary: Optional[str] = None
    highlights: List[str] = field(default_factory=list)
    
    # Crawling
    raw_content: Optional[str] = None
    crawled_content: Optional[str] = None
    
    # Metadata
    favicon: Optional[str] = None
    image: Optional[str] = None
    published_date: Optional[str] = None
    author: Optional[str] = None
    domain: Optional[str] = None
    
    # Entities
    entities: List[Dict] = field(default_factory=list)
    
    # Extra Metadata
    metadata: Dict = field(default_factory=dict)
```

This schema addresses a critical gap identified earlier: **result normalization across providers**. It provides:
- Canonical field names (title, url, snippet, provider)
- Ranking/scoring infrastructure (rank, score)
- Content extraction support (raw_content, crawled_content, summary, highlights)
- Metadata enrichment (favicon, image, published_date, author, domain, entities)
- Extensibility (metadata dict)

Implemented retrieval elements:
- Provider clients: Tavily, You, Exa
- Thin wrappers to issue searches (`search\provider\*.py`)
- Unified schema for result normalization (`schema\URS.py`)

Missing retrieval system components:
- Result schema mappers (adapters from each provider format to RetrievalResult)
- URL deduplication logic
- Hybrid retrieval/reranking pipelines using RetrievalResult schema
- Confidence scoring and source quality weighting
- Retrieval telemetry (latency, hit rates, source diversity)

# Agentic Workflow System

## Async Retrieval Orchestrator (NEW)

`retrieval\retrieval_manager.py` introduces **async task orchestration** for parallel query transformations:

```python
async def get_extended_query(query: str):
    loop = asyncio.get_event_loop()
    q1 = loop.run_in_executor(None, generate_multiquery, query)
    q2 = loop.run_in_executor(None, stepback, query)
    return await asyncio.gather(q1, q2)
```

Key design decisions:
- Uses `loop.run_in_executor()` to wrap synchronous functions (`generate_multiquery`, `stepback`) into non-blocking concurrent tasks
- `asyncio.gather()` ensures both transformations complete before returning
- Enables parallel execution of query variants (multi-query + step-back) without blocking

This represents a **significant architectural step forward** from the stateful, sequential API design (`API\main.py`). The orchestrator demonstrates:
- Async/await patterns for managed concurrency
- Non-blocking integration of synchronous I/O (LLM calls)
- Foundation for fan-out/fan-in parallelism across multiple providers

**Missing for full agentic behavior:**
- Automatic tool selection based on query intent
- Iterative search/refine loops with feedback
- Stopping criteria and budget controls (token limits, iteration count)
- Structured state persistence across orchestration steps
- Error recovery and fallback strategies

No true agent loop exists yet (no planner/executor/critic/tool-feedback loop).  
Current flow is single-step concurrent function calls, not iterative reasoning.

# LLM Orchestration

Current orchestration is direct Gemini calls with inline prompt strings (`translate_chunk\*.py`).  

Strength:
- Simple, easy to iterate.

Gaps:
- No prompt templates/versioning
- No model routing/fallback across providers
- No token budget controls
- No structured output enforcement
- No retry/backoff around model calls
- No tracing of prompt/response artifacts

# Vector Database Integration

**No vector database integration exists** in this codebase:
- No embedding generation pipeline
- No vector store client (Pinecone/Weaviate/FAISS/pgvector/etc.)
- No semantic index build/update jobs
- No ANN retrieval path

# Web Search & Scraping Layer

Current:
- Search API connectors are present (Tavily/You/Exa).

Missing:
- Web crawling/extraction pipeline
- Content cleaning/boilerplate removal
- robots/politeness controls
- freshness/cache strategy implementation
- retry/circuit-breaker logic for provider instability

# API Architecture

API surface is minimal and incomplete:
- Only query acceptance and query transformation endpoints
- No endpoint to execute full research/search pipeline
- No endpoint returning grounded final answer with citations
- No streaming endpoint

Contract concerns:
- Query passed indirectly via shared global state instead of per-request payload contracts.

# Frontend Structure

There is **no frontend implementation** in this repository:
- no React/Next/Vue app
- no UI state management
- no SSE/WebSocket integration
- no client-side citation rendering or research workspace

# Development Environment Configuration

**VS Code Setup** (`.vscode\settings.json`):
- Python environment manager: **Conda** (`ms-python.python:conda`)
- Package manager: **Conda**

This indicates the project uses Conda for environment and dependency management, though no `environment.yml` or `conda.lock` file is currently tracked in the repository.

No streaming or async architecture is present:
- FastAPI handlers are synchronous `def`, not `async def`
- no background workers (Celery/RQ/Arq)
- no queues
- no SSE/websocket tokens streaming
- no concurrent provider fanout/fan-in orchestration

# Current Features Implemented

1. Gemini-based multi-query generation.
2. Gemini-based step-back query generation.
3. API client initialization for Tavily, You.com, Exa, Gemini via env vars.
4. Basic FastAPI endpoints for query ingestion and transform invocation.
5. Basic provider-specific search wrapper functions.
6. **Unified RetrievalResult schema** for result normalization across providers (`schema\URS.py`). ✅ **NEW**
7. **Enhanced pipeline architecture design** with query intent classification, retrieval planning, provider routing, and async orchestration (`status.txt`). ✅ **NEW**
8. **Async Retrieval Orchestrator** (`retrieval\retrieval_manager.py`) — parallel execution of multi-query and step-back transformations using `loop.run_in_executor()` for non-blocking sync function calls. ✅ **NEW**

# Missing Features

Critical missing product capabilities:

1. End-to-end research answer generation with source-grounded citations.
2. Retrieval fusion/ranking and URL deduplication.
3. Crawling and content extraction.
4. Chunking, embedding, vector indexing, semantic retrieval.
5. Async orchestration and streaming responses.
6. Session model and multi-user-safe state handling.
7. Evaluation harness and regression testing.
8. Robust error taxonomy and resiliency middleware.

# Production Readiness Analysis

Current readiness: **Not production-ready**.

Blocking factors:
- plaintext secrets stored in `.env` inside project tree
- global mutable query state in API process
- no auth/authz
- no dependency manifest (no `requirements.txt` / `pyproject.toml`)
- no tests
- no deployment/runtime config
- no logging/metrics/tracing

# Technical Debt

High-priority technical debt:

1. Import/runtime bug: `search\search_manager.py` imports `exa_client` from `search.provider.exa`, but `search\provider\exa.py` exports `search_exa` only.
2. Typo consistency debt (`travily` naming across files, likely meant `tavily`).
3. Imperative `print(...)` side effects in module scope (`search\search_manager.py`, `API\you_client.py`).
4. Repeated `sys.path` manipulation across files instead of package/module structure.
5. Lack of typed response schemas for provider outputs.

# Bottlenecks & Risks

Primary risks:
- **Correctness risk:** no result normalization across providers.
- **Concurrency risk:** process-global query state causes cross-request contamination.
- **Security risk:** exposed API keys in repository `.env`.
- **Scalability risk:** synchronous, single-step calls without fanout orchestration.
- **Reliability risk:** no retries/timeouts/circuit breakers around external APIs.

# Scalability Analysis

Current architecture does not scale horizontally or safely:
- In-memory state breaks multi-instance deployment consistency.
- No caching layer for repeated queries.
- No async scatter-gather for multi-provider parallel retrieval.
- No backpressure controls or queue isolation for expensive operations.

Required scalability primitives:
- Stateless request contracts
- Async provider fanout
- Redis/queue-backed work orchestration
- Caching + dedupe + content-store layers

# Security Concerns

1. **Critical:** `.env` contains live keys in repo directory (must rotate/revoke immediately and remove from tracked artifacts).
2. No secrets management (Vault/SSM/GCP Secret Manager/etc.).
3. No request authentication or abuse controls.
4. No outbound request governance (allowlist, timeout policies, SSRF-safe fetching).
5. No PII/security logging strategy.

# Optimization Opportunities

Near-term performance gains:

1. Parallelize provider searches using async gather.
2. Add response caching for query rewrites + provider search calls.
3. Implement result normalization + duplicate URL collapse early.
4. Limit prompt tokens and enforce structured LLM outputs.
5. Add lightweight reranker before expensive synthesis.

# Suggested Refactoring

Recommended target module decomposition:

```text
app/
  api/
    routes/
      research.py
      health.py
    schemas/
  core/
    config.py
    logging.py
    security.py
  llm/
    prompts/
    providers/
    orchestrator.py
  retrieval/
    providers/
    normalize.py
    fusion.py
    rerank.py
  crawling/
    fetcher.py
    extractor.py
  memory/
    embeddings.py
    vector_store.py
  workflows/
    research_agent.py
```

Refactor priorities:
1. Replace global query state with per-request payload.
2. Create typed provider adapters + unified `SearchResult` schema.
3. Move prompt text to templates with versioning.
4. Introduce centralized config and dependency injection.
5. Add robust error model + middleware.

# Future Roadmap

1. Build a single `/research` endpoint that performs full orchestration.
2. Implement async multi-provider retrieval + normalization/fusion.
3. Add crawler/extractor with content quality filters.
4. Add embedding + vector memory for iterative and follow-up queries.
5. Implement grounded synthesis with strict citation attachment.
6. Add evaluation suite (retrieval precision, citation accuracy, answer faithfulness).
7. Introduce observability stack (logs, metrics, traces, cost telemetry).

# Recommended Advanced Features

1. **Planner-Executor-Critic agent loop** for multi-hop research tasks.
2. **Query intent classifier** to pick fast vs deep retrieval modes.
3. **Source trust scoring** with domain-level reliability priors.
4. **Temporal freshness routing** (live crawl only when required).
5. **Auto-eval and replay** framework for regression on research quality.
6. **Model orchestration policy engine** (cost/latency/quality-aware routing).
7. **Evidence graph** construction linking claims to citations and snippets.

# Overall Engineering Assessment

This repo demonstrates a **clear product thesis** and the right high-level retrieval-first direction, but implementation is currently a **prototype foundation**, not an operational Perplexity-like system. The strongest existing assets are the query-transformation components and initial provider integrations. The most urgent next step is converting the current disconnected pieces into a **stateless, async, end-to-end research pipeline** with normalization, citation-grounded synthesis, and production-grade security/observability.

Relative positioning:
- vs **Perplexity**: currently far earlier; lacks citation-grounded synthesis engine, retrieval quality controls, and production infra.
- vs **OpenAI Deep Research-style systems**: no autonomous multi-step planning/execution loop yet.
- vs **modern agentic RAG**: has initial query transformation primitives, but lacks vector memory, reranking, orchestration policy, and eval instrumentation.
