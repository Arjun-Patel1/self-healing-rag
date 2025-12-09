from retriever import Retriever
from detector_healer import DetectorHealer
from transformers import pipeline

# ------------------------------------------------
# LOAD MODULES
# ------------------------------------------------
print("\nInitializing system...")

retriever = Retriever(top_k=3)
healer = DetectorHealer()

print("Loading LLM for answer generation...")
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-large",
    max_new_tokens=300
)

print("\nSystem Ready ✔\n")

# ------------------------------------------------
# RAG ANSWER GENERATION
# ------------------------------------------------
def generate_answer(question, retrieved_chunks):
    context = "\n\n".join([chunk["chunk"] for chunk in retrieved_chunks])

    prompt = f"""
You are an AI assistant. 
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

# ------------------------------------------------
# MAIN LOOP
# ------------------------------------------------
if __name__ == "__main__":
    print("🔥 Self-Healing RAG Chatbot Started")
    print("----------------------------------")

    while True:
        question = input("\nAsk a question (or 'exit'): ")

        if question.lower() == "exit":
            print("Goodbye!")
            break

        # 1. Retrieve chunks
        print("\n🔎 Retrieving relevant documents...")
        retrieved = retriever.search(question)

        if len(retrieved) == 0:
            print("❌ No relevant documents found.")
            continue

        # 2. Generate answer
        print("🤖 Generating answer...")
        raw_answer = generate_answer(question, retrieved)

        print("\nRAW ANSWER:")
        print(raw_answer)

        # 3. Detect hallucinations
        print("\n🕵️ Checking for hallucination...")
        final_result = healer.run(question, raw_answer, retrieved)

        # 4. Show final answer
        print("\n==============================")
        print("✨ FINAL ANSWER:")
        print(final_result["final_answer"])
        print("==============================")

        # If self-healed
        if final_result["hallucinated"]:
            print("⚠️ The original answer had hallucinations.")
            print("🔧 Reason:", final_result["reason"])
            print("✔ Answer healed and corrected.")
