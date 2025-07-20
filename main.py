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
from collections import defaultdict
from app.job_matcher import match_job_to_resume

# Initialize global stats
total_stats = defaultdict(int)

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

similarity_filter_threshold = config.get("similarity_filter_threshold", 0.3)
llm_match_threshold = config.get("llm_match_threshold", 0.5)
receiver_email = config["receiver_email"]
max_pages = config["max_pages"]


# Merge any manual exclude list
exclude_publishers = set(config.get("exclude_job_publishers", []))


# Load blocked employers
blocked_employers = []
if config.get("use_blocked_employers", False):
    blocklist_path = Path("data/blocked_employers.yaml")
    if blocklist_path.exists():
        with open(blocklist_path, "r") as f:
            blocked_employers = yaml.safe_load(f).get("blocked_employers", [])
    else:
        print(
            "⚠️ blocked_employers.yaml not found — continuing without additional exclusions."
        )


# Load preferred publishers from YAML file
preferred_publishers = set()
preferred_path = Path("data/preferred_publishers.yaml")
if preferred_path.exists():
    with open(preferred_path, "r") as f:
        preferred_publishers = set(yaml.safe_load(f).get("preferred_publishers", []))
else:
    print(
        "⚠️ preferred_publishers.yaml not found — all jobs will be considered untrusted."
    )


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
    global_stats = defaultdict(int)

    while len(matched_jobs) < max_matches and page <= max_pages:
        print(f"📄 Fetching page {page}...")

        jobs = fetch_jobs(
            api_key=RAPIDAPI_KEY,
            api_host=RAPIDAPI_HOST,
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
            fields=config.get("fields", []),
        )
        global_stats["total_pages_fetched"] += 1
        global_stats["total_jobs_fetched"] += len(jobs)
        if not jobs:
            print("No jobs returned on this page.")
            break

        print(f"✅ {len(jobs)} jobs found on this page")

        for job in jobs:
            if len(matched_jobs) >= max_matches:
                break

            # Skip blocked employer names
            employer_name = job.get("employer_name", "").strip()
            if employer_name in blocked_employers:
                global_stats["blocked_employers_skipped"] += 1
                print(f"⛔ Skipping blocked employer: {employer_name}")
                continue

            # Filter by preferred publisher or apply_options
            job_publisher = job.get("job_publisher", "").strip()
            final_apply_link = job.get("job_apply_link")
            is_preferred = job_publisher in preferred_publishers

            # Try to find a better apply link if publisher isn't trusted
            better_option_found = False
            for option in job.get("apply_options") or []:
                option_publisher = option.get("publisher", "").strip()
                option_link = option.get("apply_link", "").strip()
                if option_publisher in preferred_publishers:
                    final_apply_link = option_link
                    better_option_found = True
                    break

            if not is_preferred and not better_option_found:
                global_stats["untrusted_publisher_skipped"] += 1
                print(
                    f"⛔ Skipping due to untrusted publisher and no good apply link: {job_publisher}"
                )
                continue

            # Proceed to LLM matching
            job_id = job["job_id"]

            # Optional: Skip jobs with senior titles using config-defined keywords
            if config.get("filter_senior_titles", False):
                title = job.get("job_title", "").lower()
                excluded_keywords = [
                    kw.lower() for kw in config.get("excluded_title_keywords", [])
                ]
                if any(keyword in title for keyword in excluded_keywords):
                    global_stats["senior_title_skipped"] += 1
                    print(f"⛔ Skipping senior-level job: {title}")
                    continue

            if is_new_job(job_id, seen):
                job_desc = get_full_description(job)

                # Optional: Pre-filter using semantic similarity
                if config.get("use_similarity_filter", False):
                    sim_result = match_job_to_resume(
                        job_desc, resume_text, similarity_filter_threshold
                    )
                    if not sim_result["match"]:
                        global_stats["similarity_filtered"] += 1
                        print(
                            f"⛔ Skipping due to low semantic similarity: {sim_result['reason']}"
                        )
                        continue

                result = query_openrouter_matcher(
                    job_desc, resume_text, llm_match_threshold
                )
                time.sleep(1)

                if result["reason"] not in [
                    "OpenRouter API call failed.",
                    "Invalid OpenRouter API response.",
                    "Failed to parse OpenRouter response.",
                ]:
                    new_seen.add(job_id)
                    if result["match"]:
                        global_stats["matched"] += 1
                        matched_jobs.append(
                            {
                                "job_keyword": keyword,
                                "title": job["job_title"],
                                "employer": employer_name,
                                "url": final_apply_link,
                                "reason": result["reason"],
                                "score": result["score"],
                            }
                        )

                        print(
                            f"\n🎯 MATCH with score ({result['score']}): {job['job_title']}"
                        )
                        print(f"🏢 employer: {employer_name}")
                        print(f"🔍 Reason: {result['reason']}")
                        print(f"🆔 job_id: {job_id}")
                        print(f"🔗 URL: {final_apply_link}")
                        print(f"📝 job_description: {job_desc[0:500]}")
                        print("=" * 60)
                    else:
                        global_stats["llm_filtered"] += 1
                        print(f"⚠️ LLM scored low (no match) — job_id {job_id}")
                else:
                    global_stats["llm_failed"] += 1
                    print(
                        f"⚠️ Skipping job_id {job_id} — LLM failed or response was invalid."
                    )

        page += 1

    if matched_jobs:

        summary_text = f"""
        📄 Total API pages fetched: {global_stats['total_pages_fetched']}
        🧲 Total jobs fetched: {global_stats['total_jobs_fetched']}
        ⛔ Blocked employers skipped: {global_stats['blocked_employers_skipped']}
        🔎 Similarity-pre-filtered: {global_stats['similarity_filtered']}
        👔 Senior-level jobs skipped: {global_stats['senior_title_skipped']}
        ⛔ Untrusted publishers skipped: {global_stats['untrusted_publisher_skipped']}
        ⚠️ LLM-filtered (no match): {global_stats['llm_filtered']}
        ❌ LLM failed completely: {global_stats['llm_failed']}
        ✅ Final matches (sent): {global_stats['matched']}
        📬 Email sent to: {receiver_email}
        """

        send_job_matches_email(
            sender_email=sender_email,
            sender_password=sender_password,
            receiver_email=receiver_email,
            job_matches=matched_jobs,
            keyword=keyword,
            summary_text=summary_text
        )

        print(
            f"\n📨 Email sent with {len(matched_jobs)} matches for keyword: {keyword}"
        )
    else:
        print(f"\n❌ No matching jobs found for keyword: {keyword} — email not sent.")

    return global_stats

 


# === Start Job Matching for All Keywords ===
keywords_config = config["query"]
for kw in keywords_config:
    keyword = kw["keyword"]
    max_matches = kw.get("max_matches", 3)
    keyword_stats = process_jobs_for_keyword(keyword, max_matches)
    for key in keyword_stats:
        total_stats[key] += keyword_stats[key]


# Save updated seen job list
save_seen_jobs(new_seen)


print("\n✅ All keywords processed.")
print(f"🔒 Total new jobs added to seen list: {len(new_seen - seen)}")

print("\n📊 === Statistics Summary ===")
print(f"🧲 Total jobs fetched: {total_stats['total_jobs_fetched']}")
print(f"📄 Total JSearch API pages fetched: {total_stats['total_pages_fetched']}")
print(f"⛔ Blocked employers skipped: {total_stats['blocked_employers_skipped']}")
print(f"🔎 Similarity-pre-filtered: {total_stats['similarity_filtered']}")
print(f"👔 Senior-level jobs skipped: {total_stats['senior_title_skipped']}")
print(f"⛔ Untrusted publishers skipped: {total_stats['untrusted_publisher_skipped']}")
print(f"⚠️ LLM-filtered (no match): {total_stats['llm_filtered']}")
print(f"❌ LLM failed completely: {total_stats['llm_failed']}")
print(f"✅ Final matches (sent): {total_stats['matched']}")
print(f"📬 Emails sent to: {receiver_email}")
