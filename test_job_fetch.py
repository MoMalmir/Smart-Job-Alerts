#from job_tracker import load_seen_jobs, save_seen_jobs, is_new_job
import json
#import requests
from job_matcher import match_job_to_resume
from utils import extract_text_from_pdf
from email_utils import send_job_matches_email
from job_tracker import load_seen_jobs, save_seen_jobs, is_new_job

import os

# url = "https://jsearch.p.rapidapi.com/search"

# querystring = {
#     "query": "machine learning engineer",
#     "page": "1",
#     "num_pages": "1",
#     "remote_jobs_only": "false"
# }

# headers = {
#     "X-RapidAPI-Key": "bfd2ba68b5msh77d768337361350p170c29jsn2859ff704d3a",
#     "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
# }

# response = requests.get(url, headers=headers, params=querystring)

# seen = load_seen_jobs()
# new_seen = set(seen)

# for job in response.json()["data"][:10]:  # check top 10 jobs
#     url = job["job_apply_link"]
#     if is_new_job(url, seen):
#         print(f"NEW MATCH! {job['job_title']} at {job['employer_name']}")
#         print(f"URL: {url}")
#         print("=" * 50)
#         new_seen.add(url)

# save_seen_jobs(new_seen)





# I want to save this jobs to a file called "jobs.json"
# jobs = response.json()
# with open("jobs.json", 'w', encoding='utf-8') as f:
#     json.dump(jobs, f, indent=4, ensure_ascii=False) #



# --- Load test jobs from jobs.json ---
with open("jobs.json", 'r', encoding='utf-8') as f:
    extracted_jobs = json.load(f)

# --- Extract and score a specific job ---
example = 4
job = extracted_jobs["data"][example]

def get_full_description(job):
    desc = job.get("job_description", "")
    highlights = job.get("job_highlights", {})
    qualifications = " ".join(highlights.get("Qualifications", []))
    responsibilities = " ".join(highlights.get("Responsibilities", []))
    return f"{desc}\nQualifications: {qualifications}\nResponsibilities: {responsibilities}"

job_desc = get_full_description(job)

print("Job Description:\n", job_desc)

# --- Load and parse resume ---
resume_pdf_path = "resume.pdf"
resume_text = extract_text_from_pdf(resume_pdf_path)
print("\nParsed Resume Text:\n", resume_text[:500])  # Just show first 500 chars

# --- Check similarity score ---
SIMILARITY_THRESHOLD = 0.3
sender_email = os.environ["EMAIL_USERNAME"]
sender_password = os.environ["EMAIL_PASSWORD"]

score = match_job_to_resume(job_desc, resume_text, SIMILARITY_THRESHOLD)
print("\nSimilarity Score:", score)

# --- Create mock match if relevant ---
if score["match"]:
    matched_jobs = [{
        "job_keyword": "test-email",  # You can replace this with a real keyword if needed
        "title": job["job_title"],
        "employer": job["employer_name"],
        "url": job["job_apply_link"],
        "reason": score["reason"],
    }]

    # --- Send email with matched job ---
    send_job_matches_email(
        sender_email=sender_email,
        sender_password=sender_password,
        receiver_email="malmir.edumail@gmail.com",
        job_matches=matched_jobs
    )
    print("\n Email sent successfully!")

else:
    print("\n No match found — email not sent.")