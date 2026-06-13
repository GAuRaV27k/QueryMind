import uuid
import asyncio
import random
from datetime import datetime
from typing import Optional
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
import sys
import time

# start = time.time()
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# ─── App ───────────────────────────────────────────────────────────────────────
from retrieval.retrieval_manager import retrivel_search
from postprocessing.fusion import fuse_result
from postprocessing.deduplication import deduplicate
from postprocessing.reranking_v2 import reranker
from generation.context_builder import build_context
from generation.prompt_builder import build_prompt
from generation.answer import generate_answer
from generation.cititation_map import build_citation_map, append_references
app = FastAPI(
    title="QueryMind API",
    description="AI Research Agent — Retrieval, Reranking, and Synthesis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── In-memory store ──────────────────────────────────────────────────────────

# {request_id: {"status": "processing"|"completed", "query": str, "answer": str, "sources": []}}
_store: dict[str, dict] = {}


# ─── Schemas ──────────────────────────────────────────────────────────────────


class QueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    intent: Literal["general", "research"] = "general"


class QueryResponse(BaseModel):
    request_id: str
    status: str


class AnswerResponse(BaseModel):
    request_id: str
    status: str
    answer: str | None = None



@app.post("/query")
async def submit_query(payload: QueryRequest):
    query = payload.query.strip()

    if not query:
        raise HTTPException(status_code=422, detail="Query cannot be empty")

    request_id = str(uuid.uuid4())

    _store[request_id] = {
        "status": "processing",
        "query": query,
        "intent": payload.intent,
        "answer": None,
        "sources": [],
        "Time" : None

    }

    asyncio.create_task(
        run_pipeline(request_id, query, payload.intent)
    )

    return {
        "request_id": request_id,
        "status": "processing"
    }



@app.get("/response/{request_id}")
async def get_response(request_id: str):

    if request_id not in _store:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )
    print("start")
    return _store[request_id]




async def run_pipeline(
    request_id: str,
    query: str,
    intent :str
):
    try:
        
        print("inside the pipeline")
        
        start = time.time()
        _store[request_id]["status"] = "Retrieving"
        retrieval_bundle = await retrivel_search(query)
        results = retrieval_bundle["results"]
        
        _store[request_id]["status"] = "Fusing"
        fused = fuse_result(results)
        
        _store[request_id]["status"] = "Deduplication"
        deduped = deduplicate(fused)
        
        _store[request_id]["status"] = "Reranking"
        reranked = await reranker(deduped)
        top_k = reranked[:8]

        _store[request_id]["status"] = "Context building"
        context = build_context(top_k)
        sources = []

        for r in top_k:
            sources.append({
                "title": r.title,
                "url": r.url,
                "provider": r.provider
            })
        


        _store[request_id]["status"] = "Prompt Building"
        prompt = build_prompt(
            query,
            context,
            intent= intent
        )
        
        _store[request_id]["status"] = "Answer Generation"
        answer = await generate_answer(prompt)

        _store[request_id]["status"] = "Citation Mapping "
        citation_map = build_citation_map(top_k)

        final_answer = append_references(
            answer,
            citation_map
        )
        end = time.time()
        total_time_taken = end - start
        _store[request_id] = {
            "status": "completed",
            "query": query,
            "answer": final_answer,
            "sources": sources,
            "Time" : f"{total_time_taken:.3f}"
        }
        

    except Exception as e:

        _store[request_id] = {
            "status": "failed",
            "query": query,
            "error": str(e)
            
        }





@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
