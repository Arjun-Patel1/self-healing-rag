# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports
# 8501 for Streamlit UI, 8000 for FastAPI API
EXPOSE 8501
EXPOSE 8000

# Default command: Run both API and UI
# Use & to run API in background and Streamlit in foreground
CMD uvicorn api:app --host 0.0.0.0 --port 8000 & streamlit run ui.py --server.port 8501 --server.address 0.0.0.0
