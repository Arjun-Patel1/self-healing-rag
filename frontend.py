# frontend.py
import streamlit as st
import requests

# -------------------------
# Configuration
# -------------------------
API_URL = "http://localhost:8000/query"
REINDEX_URL = "http://localhost:8000/reindex"
MONITOR_URL = "http://localhost:8000/monitor"
HISTORY_URL = "http://localhost:8000/history"

st.set_page_config(page_title="Self-Healing-RAG Frontend", layout="wide")
st.title("🧠 Self-Healing-RAG System")

# -------------------------
# Ask a Question
# -------------------------
st.subheader("💬 Ask a Question")
user_input = st.text_input("Enter your question:")

if st.button("Submit Question"):
    if user_input.strip() == "":
        st.warning("Please enter a question first!")
    else:
        try:
            response = requests.post(API_URL, json={"question": user_input})
            if response.status_code == 200:
                data = response.json()
                st.markdown("### ✅ Response")
                st.markdown(f"**Raw Answer:** <span style='color:blue'>{data['raw_answer']}</span>", unsafe_allow_html=True)
                st.markdown(f"**Final Answer:** <span style='color:green'>{data['final_answer']}</span>", unsafe_allow_html=True)
                st.markdown(f"**Healed:** {data['healed']}")
                st.markdown(f"**Heal Reason:** <span style='color:red'>{data.get('heal_reason', 'N/A')}</span>", unsafe_allow_html=True)
            else:
                st.error(f"Request failed: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error connecting to API: {e}")

# -------------------------
# Reindex / Heal System
# -------------------------
st.subheader("🛠 Reindex / Heal System")
if st.button("Reindex"):
    try:
        response = requests.post(REINDEX_URL)
        if response.status_code == 200:
            st.success("Reindexing started successfully!")
        else:
            st.error(f"Failed to start reindexing: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")

# -------------------------
# Monitor
# -------------------------
st.subheader("🩺 System Monitor")
if st.button("Run Monitor"):
    try:
        response = requests.get(MONITOR_URL)
        if response.status_code == 200:
            data = response.json()
            st.json(data)
        else:
            st.error(f"Monitor failed: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")

# -------------------------
# History
# -------------------------
st.subheader("📜 Query & Heal History")
if st.button("Show History"):
    try:
        response = requests.get(HISTORY_URL)
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(f"Failed to get history: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
