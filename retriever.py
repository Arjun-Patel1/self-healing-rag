import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_FILE = "vector.index"
META_FILE = "metadata.json"

class Retriever:
    def __init__(self, top_k=3):
        self.top_k = top_k

        # Load embedding model
        print("Loading embedding model for retriever...")
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # Load FAISS index
        print("Loading FAISS index...")
        self.index = faiss.read_index(INDEX_FILE)

        # Load metadata
        print("Loading metadata...")
        with open(META_FILE, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        print("Retriever ready.")

    def search(self, query):
        # Embed query
        query_vec = self.embedder.encode([query]).astype("float32")

        # Search in FAISS
        distances, indices = self.index.search(query_vec, self.top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            results.append({
                "score": float(dist),
                "chunk": self.metadata[idx]["chunk"],
                "title": self.metadata[idx]["title"],
                "doc_id": self.metadata[idx]["doc_id"]
            })

        return results


# Test locally
if __name__ == "__main__":
    r = Retriever(top_k=3)
    query = input("Enter your question: ")
    results = r.search(query)

    print("\nTop Results:")
    for r_ in results:
        print("\n---")
        print("Title :", r_["title"])
        print("Score :", r_["score"])
        print("Chunk :", r_["chunk"])
