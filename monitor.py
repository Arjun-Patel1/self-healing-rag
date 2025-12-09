# monitor.py
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
import time

META_FILE = "metadata.json"
INDEX_FILE = "vector.index"
REPORT_FILE = "monitor_report.json"

def load_meta():
    with open(META_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def check_schema(expected_keys=("doc_id","title","chunk")):
    meta = load_meta()
    problems = []
    for i, m in enumerate(meta):
        for k in expected_keys:
            if k not in m:
                problems.append({"idx": i, "missing_key": k, "meta": m})
    return problems

def detect_duplicate_embeddings(sample_n=500, sim_threshold=0.93):
    """
    Load up to sample_n vectors from FAISS by reconstructing them.
    FAISS IndexFlatL2 supports reconstruct(i) to get vectors.
    """
    idx = faiss.read_index(INDEX_FILE)
    ntotal = idx.ntotal
    n = min(sample_n, ntotal)
    duplicates = []
    if n <= 1:
        return duplicates

    # pick evenly spaced ids
    ids = np.linspace(0, ntotal-1, n).astype(int)
    vecs = np.array([idx.reconstruct(int(i)) for i in ids]).astype("float32")
    sims = cosine_similarity(vecs)
    # only check upper triangle
    for i in range(n):
        for j in range(i+1, n):
            if sims[i,j] > sim_threshold:
                duplicates.append({"i": int(ids[i]), "j": int(ids[j]), "sim": float(sims[i,j])})
    return duplicates

def retrieval_health_check(queries, top_k=3, embed_model="sentence-transformers/all-MiniLM-L6-v2"):
    from retriever import Retriever
    r = Retriever(top_k=top_k)
    results = {}
    for q in queries:
        res = r.search(q)
        # simple metric: average distance
        avg = sum([r["score"] for r in res]) / max(1, len(res))
        results[q] = {"avg_score": avg, "top_k": len(res)}
    return results

def run_monitor_sample():
    out = {"ts": time.strftime("%Y%m%dT%H%M%S")}
    out["schema_problems"] = check_schema()
    out["duplicates_sample"] = detect_duplicate_embeddings()
    # example queries to test retrieval health
    sample_queries = [
        "What is photosynthesis?",
        "Explain neural networks",
        "What is blockchain?"
    ]
    out["retrieval_health"] = retrieval_health_check(sample_queries)
    Path(REPORT_FILE).write_text(json.dumps(out, indent=2))
    print("[monitor] Report written to", REPORT_FILE)
    return out

if __name__ == "__main__":
    run_monitor_sample()
