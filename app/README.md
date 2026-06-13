# QueryMind — AI Research Platform

A full-stack AI research agent that retrieves, reranks, and synthesizes knowledge from multiple sources into clear, cited answers.

## Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Frontend | React 19, Vite, custom responsive CSS          |
| Backend  | FastAPI, Python 3.11+, Uvicorn                 |

---

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend runs at **http://localhost:8000**  
Swagger UI at **http://localhost:8000/docs**

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

---

## Architecture

```
app/
├── frontend/              # React + Vite app
│   └── src/
│       ├── components/
│       │   ├── Header.jsx
│       │   ├── Footer.jsx
│       │   ├── Sidebar.jsx
│       │   ├── SearchBar.jsx
│       │   ├── LoadingTimeline.jsx
│       │   ├── TypingAnswer.jsx
│       │   ├── SourceCard.jsx
│       │   └── SourceGrid.jsx
│       └── pages/
│           ├── Home.jsx
│           ├── Workspace.jsx
│           └── Settings.jsx
└── backend/               # FastAPI app
    ├── main.py            # Endpoints + run_pipeline()
    └── requirements.txt
```

---

## API Endpoints

### `POST /query`
Submit a research query.

**Body:** `{ "query": "...", "intent": "general" | "research" }`
**Response:** `{ "request_id": "<uuid>", "status": "processing" }`

### `GET /response/{request_id}`
Poll for the answer.

**Response (processing):** returns the current pipeline stage, such as `Retrieving`, `Reranking`, or `Answer Generation`.
**Response (done):**
```json
{
  "status": "completed",
  "query": "...",
  "answer": "...",
  "sources": [{ "title": "...", "provider": "...", "url": "..." }],
  "Time": "12.345"
}
```

---

## Research Pipeline

The frontend consumes the existing pipeline in `backend/main.py`:

- **Retrieval** — BM25 / dense retrieval
- **Fusion** — Reciprocal Rank Fusion
- **Deduplication**
- **FlashRank** — reranker
- **Context Builder**
- **Prompt Builder**
- **Llama** — inference
- **Citation Mapper**
# temp
