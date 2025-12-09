# api.py
import time
import threading
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Your modules (make sure these exist in the same folder)
from retriever import Retriever
from detector_healer import DetectorHealer
from reindexer import build_index
from monitor import run_monitor_sample
from index_manager import list_versions

app = FastAPI(title="Self-Healing-RAG API")

# Allow CORS for all origins (so Streamlit UI can call it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Singleton components
# -------------------------
RETRIEVER = None
HEALER = None
RETRIEVER_LOCK = threading.Lock()

def get_retriever():
    global RETRIEVER, HEALER
    with RETRIEVER_LOCK:
        if RETRIEVER is None:
            RETRIEVER = Retriever(top_k=3)
        if HEALER is None:
            HEALER = DetectorHealer()
    return RETRIEVER, HEALER

# -------------------------
# Request / response models
# -------------------------
class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class QueryResponse(BaseModel):
    question: str
    raw_answer: str
    final_answer: str
    healed: bool
    heal_reason: Optional[str] = ""  # Fixed for Pydantic v2
    retrieved: List[Dict[str, Any]] = []

class ReindexRequest(BaseModel):
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

# -------------------------
# Endpoints
# -------------------------
@app.get("/")
def root():
    return {"message": "Self-Healing RAG API is running. Use /query to ask questions."}

@app.get("/health")
def health():
    return {"status": "ok", "ts": time.strftime("%Y%m%dT%H%M%S")}

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    retriever, healer = get_retriever()
    retriever.top_k = req.top_k

    # Retrieve documents
    retrieved = retriever.search(req.question)
    if not retrieved:
        raise HTTPException(status_code=404, detail="No relevant documents found")

    # Generate raw answer
    try:
        raw = healer.generate_answer(req.question, "\n\n".join([r["chunk"] for r in retrieved]))
    except AttributeError:
        raw = " ".join([r["chunk"] for r in retrieved])[:400]

    # Run detector/healer
    result = healer.run(
        req.question,
        raw,
        [{"chunk": r["chunk"], "title": r["title"], "doc_id": r["doc_id"], "score": r["score"]} for r in retrieved]
    )

    response = {
        "question": req.question,
        "raw_answer": raw,
        "final_answer": result.get("final_answer", raw),
        "healed": result.get("hallucinated", False),
        "heal_reason": result.get("reason", ""),
        "retrieved": retrieved
    }
    return response

@app.post("/reindex")
def reindex(req: ReindexRequest):
    def _do_reindex(model_name):
        try:
            build_index(embedding_model=model_name)
        except Exception as e:
            print("[reindex] error:", e)

    threading.Thread(target=_do_reindex, args=(req.embedding_model,), daemon=True).start()
    return {"status": "reindex_started", "embedding_model": req.embedding_model}

@app.get("/monitor")
def monitor():
    try:
        report = run_monitor_sample()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def history():
    try:
        return {"versions": list_versions()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
