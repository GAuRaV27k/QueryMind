from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Annotated
from pathlib import Path

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from translate_chunk.multi_query import generate_multiquery
from translate_chunk.step_back import stepback
app = FastAPI()
qUERY: str = ""


class Query(BaseModel):
    query: Annotated[str, Field(..., description="User enter the query here !")]


@app.post("/query")
def query(payload: Query):
    global qUERY
    qUERY = payload.query.strip().lower()
    return JSONResponse(status_code=201, content={"message": "Query is received"})


@app.post("/multi_query")
def multi_query():
    if not qUERY:
        return JSONResponse(
            status_code=400,
            content={"message": "No query value found. Call /query first."},
        )

    multi_query_output = generate_multiquery(qUERY)
    return JSONResponse(
        status_code=200,
        content={"query": qUERY, "multi_query": multi_query_output},
    )


@app.post("/step_back")
def step_Back():
    if not qUERY:
        return JSONResponse(
            status_code=400,
            content={"message": "No query value found. Call /query first."},
        )
    step_back_queries = stepback(qUERY)

    return JSONResponse(
        status_code=201,
        content={
            "query" :qUERY , "step_back_queries" : step_back_queries
        }
    )