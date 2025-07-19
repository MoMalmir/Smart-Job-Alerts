# import yaml
# import os
# from pathlib import Path
# from dotenv import load_dotenv
# from app.job_tracker import load_seen_jobs, save_seen_jobs, is_new_job
# from app.job_fetcher import fetch_jobs
# from app.llm_matcher import query_openrouter_matcher
# from app.utils import extract_text_from_pdf
# from app.email_utils import send_job_matches_email
# import time 

# # Ensure the required environment variables are set
# # Uncomment the line below if using a .env file instead of Codespaces secrets
# load_dotenv()
# # Get environment variables
# RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
# RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
# sender_email = os.getenv("EMAIL_USERNAME")
# sender_password = os.getenv("EMAIL_PASSWORD")

# if not all([RAPIDAPI_KEY, RAPIDAPI_HOST, sender_email, sender_password]):
#     raise EnvironmentError("Missing one or more required environment variables.")


# # Load config
# with open("config.yaml", "r") as f:
#     config = yaml.safe_load(f)
    
# location = config["location"]
# remote = config["remote_only"]
# date_posted = config["date_posted"]
# # num_pages = config["num_pages"]
# Similarity_Threshold = config["Similarity_Threshold"]
# receiver_email = config["receiver_email"]
# max_pages = config["max_pages"]

# # Load blocked employers
# blocklist_path = Path("data/blocked_employers.yaml")
# if blocklist_path.exists():
#     with open(blocklist_path, "r") as f:
#         blocked_employers = set(yaml.safe_load(f).get("blocked_employers", []))
# else:
#     blocked_employers = set()

# # Load resume
# resume_pdf_path = "data/resume.pdf"
# if not Path(resume_pdf_path).exists():
#     print("resume.pdf not found in 'data/'. Using example resume instead.")
#     resume_pdf_path = "data/resume_example.pdf"
# resume_text = extract_text_from_pdf(resume_pdf_path)
# print(f"resume_text: {resume_text[0:500]}")


# # Load seen jobs
# seen = load_seen_jobs()
# new_seen = set(seen)

# def get_full_description(job):
#     desc = job.get("job_description", "")
#     highlights = job.get("job_highlights", {})
#     qualifications = " ".join(highlights.get("Qualifications", []))
#     responsibilities = " ".join(highlights.get("Responsibilities", []))
#     return f"{desc}\nQualifications: {qualifications}\nResponsibilities: {responsibilities}"


# # Process each keyword
# def process_jobs_for_keyword(keyword, max_matches):
#     print(f"\n Searching for: {keyword}")
#     matched_jobs = []
#     page = 1

#     while len(matched_jobs) < max_matches and page <= max_pages:
#         print(f"Fetching page {page}...")
#         jobs = fetch_jobs(
#             RAPIDAPI_KEY, RAPIDAPI_HOST, keyword, location, remote, date_posted, page
#         )
#         if not jobs:
#             print("No more jobs returned.")
#             break

#         print(len(jobs), "jobs found on this page")

#         for job in jobs:
#             if len(matched_jobs) >= max_matches:
#                 break

#             employer = job["employer_name"].strip()

#             if employer in blocked_employers:
#                 print(f"Skipped blocked employer: {employer}")
#                 continue

#             job_id = job["job_id"]
#             if is_new_job(job_id, seen):
#                 job_desc = get_full_description(job)
#                 result = query_openrouter_matcher(
#                     job_desc, resume_text, Similarity_Threshold
#                 )
#                 time.sleep(1)  # Rate limiting for OpenRouter API
#                 if result["reason"] not in [
#                     "OpenRouter API call failed.",
#                     "Invalid OpenRouter API response.",
#                     "Failed to parse OpenRouter response.",
#                 ]:
#                     new_seen.add(job_id)

#                     if result["match"]:
#                         matched_jobs.append(
#                             {
#                                 "job_keyword": keyword,
#                                 "title": job["job_title"],
#                                 "employer": job["employer_name"],
#                                 "url": job["job_apply_link"],
#                                 "reason": result["reason"],
#                                 "score": result["score"],
#                             }
#                         )

#                         print(f"\n MATCH: {job['job_title']}")
#                         print(f"employer: {employer}")
#                         print(f"Reason: {result['reason']}")
#                         print(f"job_id: {job_id}")
#                         print(f"URL: {job['job_apply_link']}")
#                         print(f"job_description: {job_desc[0:500]}")
#                         print("=" * 60)
#                 else:
#                     print(f"⚠️ Skipping job_id {job_id} — LLM failed or response was invalid.")
#         page += 1

#     print(f"\n {len(matched_jobs)} matches found for keyword: {keyword}")
#     print(f"\n sending the email of the matched jobs for keyword: {keyword}")
#     if matched_jobs:
#         send_job_matches_email(
#             sender_email=sender_email,
#             sender_password=sender_password,
#             receiver_email=receiver_email,
#             job_matches=matched_jobs,
#             keyword=keyword,
#         )
#         print("\n Email sent successfully!")
#     else:
#         print("\n No match found — email not sent.")


# # Save updated seen list
# save_seen_jobs(new_seen)




# keywords_config = config["job_keywords"]
# for kw in keywords_config:
#     keyword = kw["keyword"]
#     max_matches = kw.get("max_matches", 3)  # fallback to 3 if not specified
#     process_jobs_for_keyword(keyword, max_matches)





import yaml
import os
from pathlib import Path
from dotenv import load_dotenv
from app.job_tracker import load_seen_jobs, save_seen_jobs, is_new_job
from app.llm_matcher import query_openrouter_matcher
from app.utils import extract_text_from_pdf
from app.email_utils import send_job_matches_email
from app.job_fetcher import fetch_jobs  # This must now use updated fetch_jobs logic
import time

# Load environment variables
load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
sender_email = os.getenv("EMAIL_USERNAME")
sender_password = os.getenv("EMAIL_PASSWORD")
if not all([RAPIDAPI_KEY, RAPIDAPI_HOST, sender_email, sender_password]):
    raise EnvironmentError("Missing one or more required environment variables.")

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

Similarity_Threshold = config["Similarity_Threshold"]
receiver_email = config["receiver_email"]
max_pages = config["max_pages"]

# Load blocked employers
blocked_employers = []
if config.get("use_blocked_employers", False):
    blocklist_path = Path("data/blocked_employers.yaml")
    if blocklist_path.exists():
        with open(blocklist_path, "r") as f:
            blocked_employers = yaml.safe_load(f).get("blocked_employers", [])
    else:
        print("⚠️ blocked_employers.yaml not found — continuing without additional exclusions.")

# Merge any manual exclude list
exclude_publishers = set(config.get("exclude_job_publishers", []))
exclude_publishers.update(blocked_employers)

# Load resume
resume_pdf_path = "data/resume.pdf"
if not Path(resume_pdf_path).exists():
    print("⚠️ resume.pdf not found in 'data/'. Using example resume instead.")
    resume_pdf_path = "data/resume_example.pdf"
resume_text = extract_text_from_pdf(resume_pdf_path)
print(f"resume_text: {resume_text[0:500]}")

# Load seen jobs
seen = load_seen_jobs()
new_seen = set(seen)

def get_full_description(job):
    desc = job.get("job_description", "")
    highlights = job.get("job_highlights", {})
    qualifications = " ".join(highlights.get("Qualifications", []))
    responsibilities = " ".join(highlights.get("Responsibilities", []))
    return f"{desc}\nQualifications: {qualifications}\nResponsibilities: {responsibilities}"

# === MAIN MATCHING LOOP PER KEYWORD ===
def process_jobs_for_keyword(keyword, max_matches):
    print(f"\n🔍 Searching for: {keyword}")
    matched_jobs = []
    page = 1

    while len(matched_jobs) < max_matches and page <= max_pages:
        print(f"📄 Fetching page {page}...")

        jobs = fetch_jobs(
            api_key = RAPIDAPI_KEY,
            api_host = RAPIDAPI_HOST,
            query=keyword,
            page=page,
            country=config.get("country", "us"),
            language=config.get("language", ""),
            date_posted=config.get("date_posted", "all"),
            work_from_home=config.get("work_from_home", False),
            employment_types=config.get("employment_types", []),
            job_requirements=config.get("job_requirements", []),
            radius=config.get("radius", None),
            exclude_publishers=list(exclude_publishers),
            fields=config.get("fields", [])
        )

        if not jobs:
            print("No jobs returned on this page.")
            break

        print(f"✅ {len(jobs)} jobs found on this page")

        for job in jobs:
            if len(matched_jobs) >= max_matches:
                break

            job_id = job["job_id"]
            if is_new_job(job_id, seen):
                job_desc = get_full_description(job)
                result = query_openrouter_matcher(job_desc, resume_text, Similarity_Threshold)
                time.sleep(1)  # Rate-limit OpenRouter API

                if result["reason"] not in [
                    "OpenRouter API call failed.",
                    "Invalid OpenRouter API response.",
                    "Failed to parse OpenRouter response.",
                ]:
                    new_seen.add(job_id)

                    if result["match"]:
                        matched_jobs.append(
                            {
                                "job_keyword": keyword,
                                "title": job["job_title"],
                                "employer": job["employer_name"],
                                "url": job["job_apply_link"],
                                "reason": result["reason"],
                                "score": result["score"],
                            }
                        )

                        print(f"\n🎯 MATCH with score ({result["score"]}): {job['job_title']}")
                        print(f"🏢 employer: {job['employer_name']}")
                        print(f"🔍 Reason: {result['reason']}")
                        print(f"🆔 job_id: {job_id}")
                        print(f"🔗 URL: {job['job_apply_link']}")
                        print(f"📝 job_description: {job_desc[0:500]}")
                        print("=" * 60)
                else:
                    print(f"⚠️ Skipping job_id {job_id} — LLM failed or response was invalid.")

        page += 1

    print(f"\n📬 {len(matched_jobs)} matches found for keyword: {keyword}")
    if matched_jobs:
        send_job_matches_email(
            sender_email=sender_email,
            sender_password=sender_password,
            receiver_email=receiver_email,
            job_matches=matched_jobs,
            keyword=keyword,
        )
        print("✅ Email sent successfully!")
    else:
        print("ℹ️ No match found — email not sent.")


# === Start Job Matching for All Keywords ===
keywords_config = config["query"]
for kw in keywords_config:
    keyword = kw["keyword"]
    max_matches = kw.get("max_matches", 3)
    process_jobs_for_keyword(keyword, max_matches)

# Save updated seen job list
save_seen_jobs(new_seen)
