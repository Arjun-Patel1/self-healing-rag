# self-healing-rag
Self-Healing RAG Chatbot

Self-Healing RAG is a Retrieval-Augmented Generation (RAG) chatbot that can answer questions using relevant documents, detect hallucinations in its responses, and self-heal incorrect or misleading outputs. It combines document retrieval, large language model (LLM) generation, and an automated healing mechanism to ensure accurate answers.

Features

Retrieval-Augmented Generation (RAG): Retrieves relevant chunks from a document database to generate informed answers.

Hallucination Detection: Checks if the LLM output contains misinformation or inconsistencies.

Self-Healing Mechanism: Automatically corrects answers if hallucinations are detected.

Customizable Retrieval: Configure the number of top documents to retrieve (top_k).

FastAPI API: Provides endpoints for querying, reindexing, monitoring, and checking history.

Streamlit UI: Interactive web interface for asking questions and viewing results.

Getting Started
Prerequisites

Python 3.10+

pip

Optional: Docker for containerized deployment

Install dependencies
pip install -r requirements.txt

Run the Streamlit UI
streamlit run ui.py

Run the FastAPI API
uvicorn api:app --host 0.0.0.0 --port 8000

Usage
Streamlit UI

Open http://localhost:8501 in your browser.

Enter your question in the input box.

Adjust top_k to control the number of retrieved documents.

See Raw Answer, Final Answer, and Retrieved Chunks.

Check if the answer was self-healed.

Project Structure

self-healing-rag/
├─ api.py           # FastAPI API endpoints
├─ ui.py            # Streamlit UI interface
├─ app.py           # Optional combined script (Streamlit + API)
├─ retriever.py     # Document retrieval module
├─ detector_healer.py # Hallucination detection & healing
├─ reindexer.py     # Index building module
├─ monitor.py       # System monitoring utilities
├─ index_manager.py # Manage document index versions
├─ requirements.txt # Python dependencies
└─ Dockerfile       # Docker container definition

Docker Deployment

Build Docker image:

docker build -t self_healing_rag .


Run container:

docker run -p 8000:8000 self_healing_rag


Access the API at http://localhost:8000 or Streamlit UI at http://localhost:8501.

Future Improvements

Add support for multiple LLM backends.

Enable real-time indexing for new documents.

Improve healing mechanism with more advanced validation.
