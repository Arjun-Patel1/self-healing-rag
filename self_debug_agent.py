# self_debug_agent.py
import json
from transformers import pipeline

REPORT_FILE = "monitor_report.json"

def load_report():
    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def summarize_and_suggest(report):
    # small model to keep it runnable; replace with larger if available
    summarizer = pipeline("text2text-generation", model="google/flan-t5-small")
    prompt = f"""
You are a system debug assistant. Given the system monitor report below, summarize the top 3 issues and give concrete step-by-step fixes for each.

Report:
{json.dumps(report, indent=2)}

Return a JSON object with keys: summary, fixes (list).
"""
    out = summarizer(prompt, max_length=256)[0]["generated_text"]
    # Try to parse JSON. If not JSON, return as text under summary.
    try:
        import re
        m = re.search(r"\{.*\}", out, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception:
        pass
    return {"summary": out, "fixes": []}

if __name__ == "__main__":
    rep = load_report()
    advice = summarize_and_suggest(rep)
    print("=== ADVICE ===")
    print(json.dumps(advice, indent=2))

