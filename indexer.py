import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Paths
DATA_FILE = "data.jsonl"
INDEX_FILE = "vector.index"
META_FILE = "metadata.json"

# Load embedding model
print("Loading embedding model...")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load data
print("Loading JSONL data...")
docs = []
with open(DATA_FILE, "r", encoding="utf-8") as f:
    for line in f:
        docs.append(json.loads(line))

# Create chunks (simple version)
def chunk_text(text, chunk_size=200):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i : i + chunk_size])

# Build chunks and metadata
chunks = []
metadata = []

print("Chunking documents...")
for doc in docs:
    for chunk in chunk_text(doc["text"]):
        chunks.append(chunk)
        metadata.append({
            "doc_id": doc["id"],
            "title": doc["title"],
            "chunk": chunk
        })

print(f"Total chunks created: {len(chunks)}")

# Embed all chunks
print("Embedding chunks...")
embeddings = embedder.encode(chunks, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

# Build FAISS index
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)

print("Adding vectors to FAISS index...")
index.add(embeddings)

# Save index
faiss.write_index(index, INDEX_FILE)

# Save metadata
with open(META_FILE, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print("✓ Indexing complete")
print("Saved:")
print(" -", INDEX_FILE)
print(" -", META_FILE)

from index_manager import save_version
save_version("vector.index", "metadata.json")
print("✓ Versioned copy saved.")