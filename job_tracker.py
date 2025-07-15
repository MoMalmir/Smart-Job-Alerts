import json
from pathlib import Path

SEEN_JOBS_FILE = "seen_jobs.json"

def load_seen_jobs():
    if Path(SEEN_JOBS_FILE).exists():
        if Path(SEEN_JOBS_FILE).stat().st_size == 0:
            return set()
        with open(SEEN_JOBS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_jobs(seen_jobs):
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(list(seen_jobs), f)

def is_new_job(job_url, seen_jobs):
    return job_url not in seen_jobs
