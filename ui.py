'''
# ui.py
import streamlit as st
import requests

# -------------------------
# Streamlit page config
# -------------------------
st.set_page_config(
    page_title="Self-Healing RAG Chatbot",
    layout="centered",
)

st.title("🤖 Self-Healing RAG Chatbot")
st.markdown(
    "Ask a question and the system will provide answers with hallucination detection and self-healing."
)

# -------------------------
# User input
# -------------------------
question = st.text_input("Ask a question:")

top_k = st.slider("Number of retrieved documents (top_k)", min_value=1, max_value=10, value=3)

if st.button("Submit") and question:
    with st.spinner("Generating answer..."):
        try:
            # Call the API
            api_url = "http://localhost:8000/query"
            payload = {"question": question, "top_k": top_k}
            response = requests.post(api_url, json=payload)

            if response.status_code == 200:
                data = response.json()
                st.subheader("📜 Raw Answer")
                st.write(data["raw_answer"])

                st.subheader("✨ Final Answer")
                st.write(data["final_answer"])

                if data["healed"]:
                    st.warning(f"⚠️ The original answer had hallucinations.\n🔧 Reason: {data['heal_reason']}")
                else:
                    st.success("✅ Answer verified, no hallucinations detected.")

                st.subheader("📄 Retrieved Chunks")
                for i, chunk in enumerate(data["retrieved"], 1):
                    st.markdown(f"**Chunk {i}:** {chunk['chunk'][:500]}...")

            else:
                st.error(f"API Error: {response.status_code} - {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the API. Make sure api.py is running.")
'''
