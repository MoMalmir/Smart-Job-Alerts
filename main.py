import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

from job_tracker import load_seen_jobs, save_seen_jobs, is_new_job
from job_fetcher import fetch_jobs
from job_matcher import match_job_to_resume
from utils import extract_text_from_pdf

# Load environment variables from Codespaces secrets or .env
load_dotenv()  # This does nothing in Codespaces, but works locally

# Optional: check if keys exist
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

if not RAPIDAPI_KEY or not RAPIDAPI_HOST:
    raise EnvironmentError("Missing RAPIDAPI_KEY or RAPIDAPI_HOST. Set them in Codespaces secrets or .env")

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

keywords = config["job_keywords"]
location = config["location"]
remote = config["remote_only"]
date_posted = config["date_posted"]
num_pages = config["num_pages"]

# Load resume
resume_pdf_path = "resume.pdf"
resume_text = extract_text_from_pdf(resume_pdf_path)

# Load seen jobs
seen = load_seen_jobs()
new_seen = set(seen)

# Process each keyword
for keyword in keywords:
    print(f"\n Searching for: {keyword}")
    jobs = fetch_jobs(RAPIDAPI_KEY,RAPIDAPI_HOST, keyword, location, remote, date_posted, num_pages)
    print(len(jobs), "jobs found")
    for job in jobs:
        print(f"Processing job: {job['job_title']} at {job['employer_name']}")
        job_url = job["job_apply_link"]
        if is_new_job(job_url, seen):
            print(f"New job found: {job_url}")
            job_desc = job["job_description"]
            result = match_job_to_resume(job_desc, resume_text)
            if result["match"]:
                print("Match found!")
                print(f"Job Title: {job['job_title']}")
                print(f"\n MATCH: {job['job_title']} at {job['employer_name']}")
                print(f"Reason: {result['reason']}")
                print(f"URL: {job_url}")
                print("=" * 60)
            new_seen.add(job_url)

# Save updated seen list
save_seen_jobs(new_seen)
