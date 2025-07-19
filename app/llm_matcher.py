import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Reads the prompt template at startup
with open("data/prompt_template.txt", "r", encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()


def query_openrouter_matcher(job_desc: str, resume_text: str, threshold: float) -> dict:
    prompt = PROMPT_TEMPLATE.format(resume_text=resume_text, job_desc=job_desc)

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "HTTP-Referer": "https://jobmatcher.parnian.dev",
        "X-Title": "Job Matcher",
        "Content-Type": "application/json",
    }

    data = {
        "model": "moonshotai/kimi-k2",
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data
        )
        result = response.json()
        if "choices" not in result:
            print("❌ Invalid API response:", result)
            return {"match": False, "score": 0.0, "reason": "Invalid OpenRouter API response."}
        
        content = result["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ API error:", e)
        return {"match": False, "score": 0.0, "reason": "OpenRouter API call failed."}

    try:
        score_line, reason_line = content.strip().split("\n", 1)
        score = float(score_line.split(":")[1].strip())
        reason = reason_line.split(":", 1)[1].strip()
        return {"match": score >= threshold, "score": score, "reason": reason}
    except Exception as e:
        print("❌ Parsing error:", e)
        return {
            "match": False,
            "score": 0.0,
            "reason": "Failed to parse OpenRouter response.",
        }
