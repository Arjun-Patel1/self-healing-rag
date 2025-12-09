import re
from transformers import pipeline

class DetectorHealer:

    def __init__(self):
        print("Loading LLM for detector & healer module...")
        self.model = pipeline(
            "text2text-generation",
            model="google/flan-t5-large",
            max_new_tokens=256
        )

    # -------------------------------------------------
    # 1. DETECTOR
    # -------------------------------------------------
    def detect_problem(self, answer, retrieved_chunks):
        """
        Detect hallucinations, unsupported claims, contradictions,
        and missing information.
        """

        context = "\n\n".join([c["chunk"] for c in retrieved_chunks])

        prompt = f"""
You are a hallucination detector. 
Given the retrieved context and the model's answer, identify if the answer contains:

1. Unsupported facts  
2. Missing key information  
3. Contradictions  
4. Hallucinations  

Return ONLY a JSON object like this:
{{
  "hallucination": true/false,
  "reason": "short explanation"
}}

Answer:

{answer}

Context:

{context}
        """

        response = self.model(prompt)[0]["generated_text"]

        # Extract JSON using regex
        try:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            return eval(match.group())
        except:
            return {"hallucination": False, "reason": "Parsing failed -> assume OK"}

    # -------------------------------------------------
    # 2. HEALER
    # -------------------------------------------------
    def heal_answer(self, question, answer, retrieved_chunks):
        """
        Rewrite the answer using retrieved context,
        ensuring no hallucinations.
        """

        context = "\n\n".join([c["chunk"] for c in retrieved_chunks])

        prompt = f"""
You are a RAG Healer.

Rewrite the answer using ONLY the retrieved context below.  
Fix hallucinations, remove unsupported claims, and ensure the answer is:

- Grounded strictly in context
- Factual
- Concise
- Accurate
- Useful for the user

QUESTION:
{question}

OLD ANSWER:
{answer}

RETRIEVED CONTEXT:
{context}

Return only the corrected answer. 
        """

        healed = self.model(prompt)[0]["generated_text"]
        return healed.strip()

    # -------------------------------------------------
    # 3. SELF-HEAL FULL EXECUTION
    # -------------------------------------------------
    def run(self, question, raw_answer, retrieved_chunks):
        result = self.detect_problem(raw_answer, retrieved_chunks)

        if result["hallucination"]:
            print("\n⚠️ Hallucination detected:", result["reason"])
            print("🔧 Healing answer...\n")
            healed = self.heal_answer(question, raw_answer, retrieved_chunks)
            return {
                "final_answer": healed,
                "hallucinated": True,
                "reason": result["reason"]
            }

        else:
            return {
                "final_answer": raw_answer,
                "hallucinated": False,
                "reason": None
            }


# Test
if __name__ == "__main__":
    dh = DetectorHealer()

    fake_chunks = [
        {"chunk": "Python is a programming language created by Guido van Rossum."},
        {"chunk": "It is widely used for AI, ML, and backend systems."}
    ]

    q = "What is Python?"
    wrong_a = "Python is a snake that created Google."

    result = dh.run(q, wrong_a, fake_chunks)
    print("\nFinal Output:")
    print(result)
