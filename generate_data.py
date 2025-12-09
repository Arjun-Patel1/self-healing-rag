import json

# Sample documents for your RAG system
docs = [
    {
        "id": "1",
        "title": "Photosynthesis Basics",
        "text": "Photosynthesis is the process by which green plants use sunlight to synthesize foods from carbon dioxide and water."
    },
    {
        "id": "2",
        "title": "Machine Learning Definition",
        "text": "Machine learning is a field of AI that allows systems to learn patterns from data and improve over time without explicit programming."
    },
    {
        "id": "3",
        "title": "RAG Pipeline Explanation",
        "text": "Retrieval Augmented Generation (RAG) is an architecture where an LLM retrieves relevant documents before generating an answer."
    },
    {
        "id": "4",
        "title": "The Solar System",
        "text": "The solar system consists of the Sun and the objects that orbit it, including the eight planets and their moons."
    },
    {
        "id": "5",
        "title": "Neural Networks",
        "text": "A neural network is a computational model inspired by the human brain, consisting of layers of interconnected nodes."
    }
]

# Write to JSONL
with open("data.jsonl", "w", encoding="utf-8") as f:
    for doc in docs:
        f.write(json.dumps(doc) + "\n")

print("✓ data.jsonl created with", len(docs), "documents")
