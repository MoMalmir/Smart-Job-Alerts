import requests
import json
import os
import requests
from app.utils import extract_text_from_pdf
import sys
from dotenv import load_dotenv
import argparse

load_dotenv()

def get_full_description(job):
    desc = job.get("job_description", "")
    highlights = job.get("job_highlights", {})
    qualifications = " ".join(highlights.get("Qualifications", []))
    responsibilities = " ".join(highlights.get("Responsibilities", []))
    return f"{desc}\n\nQualifications:\n{qualifications}\n\nResponsibilities:\n{responsibilities}"



with open("jobs.json", 'r', encoding='utf-8') as f:
    extracted_jobs = json.load(f)["data"][:10]

# --- Load and parse resume ---
resume_pdf_path = "data/resume.pdf"
resume_text = extract_text_from_pdf(resume_pdf_path)
print("Resume loaded. Preview:\n", resume_text[:500])


parser = argparse.ArgumentParser(description="Job matcher using OpenRouter.")
parser.add_argument(
    "--prompt_file",
    type=str,
    default="data/prompt_template.txt",
    help="Path to the prompt template file"
)
args = parser.parse_args()


with open(args.prompt_file, "r", encoding="utf-8") as f:
    prompt_template = f.read()

print(prompt_template[:500])  # Preview the prompt template
def query_openrouter_matcher(job_desc: str, resume_text: str) -> dict:
    prompt = prompt_template.format(resume_text=resume_text, job_desc=job_desc)
    
    headers = {
    "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
    "HTTP-Referer": "https://jobmatcher.parnian.dev",  # Placeholder domain is fine
    "X-Title": "Job Matcher",
    "Content-Type": "application/json",
    }
    # "deepseek/deepseek-r1-0528-qwen3-8b:free"
    # "moonshotai/kimi-k2:free"
    data = {
        "model": "moonshotai/kimi-k2:free",  
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    result = response.json()
    content = result["choices"][0]["message"]["content"]

    print("\n🔍  How the job match:\n")

    # Parse score and reason
    try:
        score_line, reason_line = content.strip().split("\n", 1)
        score = float(score_line.split(":")[1].strip())
        reason = reason_line.split(":", 1)[1].strip()
        return {"match": score >= 0.1, "score": score, "reason": reason}
    except Exception as e:
        print("❌ Failed to parse response:", e)
        return {"match": False, "score": 0.0, "reason": "Failed to parse OpenRouter response."}


# --- Run matching on all jobs ---
for job in extracted_jobs[0:2]:  # Limit to first 5 jobs for demo
    job_desc = get_full_description(job)
    result = query_openrouter_matcher(job_desc, resume_text)

    print(f"✅ Match Score: {result['score']}")
    print(f"\n📝 Job Title: {job['job_title']} at {job['employer_name']}")
    print(f"\n🔗 URL: {job['job_apply_link']}")
    print(f"\n💬 Reason: {result['reason']}")
    print("=" * 80)