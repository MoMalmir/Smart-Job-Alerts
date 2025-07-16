import yaml
import os
from pathlib import Path
from dotenv import load_dotenv
from job_tracker import load_seen_jobs, save_seen_jobs, is_new_job
from job_fetcher import fetch_jobs
from job_matcher import match_job_to_resume
from app.utils import extract_text_from_pdf

# from job_summary import generate_summary
from email_utils import send_job_matches_email

# Ensure the required environment variables are set
# Uncomment the line below if using a .env file instead of Codespaces secrets
# load_dotenv()

# Get environment variables
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
sender_email = os.environ["EMAIL_USERNAME"]
sender_password = os.environ["EMAIL_PASSWORD"]


if not RAPIDAPI_KEY or not RAPIDAPI_HOST:
    raise EnvironmentError(
        "Missing RAPIDAPI_KEY or RAPIDAPI_HOST. Set them in Codespaces secrets or .env"
    )

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

keywords = config["job_keywords"]
location = config["location"]
remote = config["remote_only"]
date_posted = config["date_posted"]
num_pages = config["num_pages"]
Similarity_Threshold = config["Similarity_Threshold"]
receiver_email = config["receiver_email"]


# Load blocked employers
blocklist_path = Path("blocked_employers.yaml")
if blocklist_path.exists():
    with open(blocklist_path, "r") as f:
        blocked_employers = set(yaml.safe_load(f).get("blocked_employers", []))
else:
    blocked_employers = set()

# Load resume
resume_pdf_path = "resume.pdf"
resume_text = extract_text_from_pdf(resume_pdf_path)
print(f"resume_text: {resume_text}")
# Load seen jobs
seen = load_seen_jobs()
new_seen = set(seen)


def get_full_description(job):
    desc = job.get("job_description", "")
    highlights = job.get("job_highlights", {})
    qualifications = " ".join(highlights.get("Qualifications", []))
    responsibilities = " ".join(highlights.get("Responsibilities", []))
    return f"{desc}\nQualifications: {qualifications}\nResponsibilities: {responsibilities}"


# Process each keyword
for keyword in keywords:
    print(f"\n Searching for: {keyword}")
    jobs = fetch_jobs(
        RAPIDAPI_KEY, RAPIDAPI_HOST, keyword, location, remote, date_posted, num_pages
    )
    print(len(jobs), "jobs found")

    # Collect matched jobs
    matched_jobs = []

    for job in jobs:

        employer = job["employer_name"].strip()

        # Skip blocked employers
        if employer in blocked_employers:
            print(f"Skipped blocked employer: {employer}")
            continue

        job_id = job["job_id"]
        if is_new_job(job_id, seen):
            job_desc = get_full_description(job)
            result = match_job_to_resume(job_desc, resume_text, Similarity_Threshold)
            if result["match"]:
                matched_jobs.append(
                    {
                        "job_keyword": keyword,
                        "title": job["job_title"],
                        "employer": job["employer_name"],
                        "url": job["job_apply_link"],
                        "reason": result["reason"],
                    }
                )

                print(f"\n MATCH: {job['job_title']}")
                print(f"employer: {employer}")
                print(f"Reason: {result['reason']}")
                print(f"job_id: {job_id}")
                print(f"URL: {job['job_apply_link']}")
                print(f"job_description: {job_desc}")
                print("=" * 60)

            new_seen.add(job_id)
    # Send the email
    if matched_jobs:
        send_job_matches_email(
            sender_email=sender_email,
            sender_password=sender_password,
            receiver_email=receiver_email,
            job_matches=matched_jobs,
            keyword=keyword,
        )
        print("\n Email sent successfully!")

    else:
        print("\n No match found — email not sent.")

# Save updated seen list
save_seen_jobs(new_seen)
