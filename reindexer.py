# reindexer.py
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path
from index_manager import save_version

DATA_FILE = "data.jsonl"
META_OUT = "metadata.json"
INDEX_OUT = "vector.index"

def load_docs(path=DATA_FILE):
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))
    return docs

def chunk_text(text, chunk_size=200):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

def build_index(embedding_model="sentence-transformers/all-MiniLM-L6-v2", persist_index_file=INDEX_OUT, persist_meta_file=META_OUT):
    print("[reindexer] Loading embedder:", embedding_model)
    embedder = SentenceTransformer(embedding_model)

    docs = load_docs()
    chunks = []
    metadata = []
    for d in docs:
        for c in chunk_text(d["text"]):
            chunks.append(c)
            metadata.append({"doc_id": d["id"], "title": d.get("title",""), "chunk": c})

    print(f"[reindexer] Created {len(chunks)} chunks. Embedding...")
    vecs = embedder.encode(chunks, show_progress_bar=True)
    arr = np.array(vecs).astype("float32")
    dim = arr.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(arr)
    faiss.write_index(index, persist_index_file)

    with open(persist_meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Save version copy
    tag = save_version(persist_index_file, persist_meta_file)
    print("[reindexer] Reindex complete. saved version:", tag)
    return tag

if __name__ == "__main__":
    build_index()
