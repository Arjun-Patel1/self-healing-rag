import streamlit as st
from retriever import Retriever
from detector_healer import DetectorHealer
from transformers import pipeline

# ----------------------------------------
# LOAD MODULES
# ----------------------------------------
@st.cache_resource
def load_system():
    retriever = Retriever(top_k=3)
    healer = DetectorHealer()
    generator = pipeline(
        "text2text-generation",
        model="google/flan-t5-large",
        max_new_tokens=300
    )
    return retriever, healer, generator

retriever, healer, generator = load_system()

# ----------------------------------------
# RAG ANSWER GENERATION
# ----------------------------------------
def generate_answer(question, retrieved_chunks):
    context = "\n\n".join([chunk["chunk"] for chunk in retrieved_chunks])

    prompt = f"""
Answer the user's question using ONLY the provided context.
Do NOT hallucinate. If the answer is not present, say "Information not found".

QUESTION:
{question}

CONTEXT:
{context}

ANSWER:
"""
    output = generator(prompt)[0]["generated_text"]
    return output.strip()

# ----------------------------------------
# STREAMLIT UI
# ----------------------------------------
st.title("🧠 Self-Healing RAG Chatbot")

question = st.text_input("Ask a question:")

if st.button("Submit") and question:
    with st.spinner("Retrieving documents..."):
        retrieved = retriever.search(question)

    if len(retrieved) == 0:
        st.error("No relevant documents found.")
        st.stop()

    with st.spinner("Generating answer..."):
        raw_answer = generate_answer(question, retrieved)

    st.subheader("Raw Answer")
    st.write(raw_answer)

    with st.spinner("Checking hallucinations..."):
        final = healer.run(question, raw_answer, retrieved)

    st.subheader("Final Answer")
    st.success(final["final_answer"])

    if final["hallucinated"]:
        st.warning("Hallucinations detected and corrected.")
        st.write("Reason:", final["reason"])
