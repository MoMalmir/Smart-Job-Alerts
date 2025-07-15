from job_tracker import load_seen_jobs, save_seen_jobs, is_new_job

import requests

url = "https://jsearch.p.rapidapi.com/search"

querystring = {
    "query": "machine learning engineer",
    "page": "1",
    "num_pages": "1",
    "remote_jobs_only": "false"
}

headers = {
    "X-RapidAPI-Key": "bfd2ba68b5msh77d768337361350p170c29jsn2859ff704d3a",
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

seen = load_seen_jobs()
new_seen = set(seen)


for job in response.json()["data"][:10]:  # check top 10 jobs
    url = job["job_apply_link"]
    if is_new_job(url, seen):
        print(f"NEW MATCH! {job['job_title']} at {job['employer_name']}")
        print(f"URL: {url}")
        print("=" * 50)
        new_seen.add(url)

save_seen_jobs(new_seen)