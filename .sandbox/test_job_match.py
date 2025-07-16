

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


jobs = response.json()["data"][:10]

result = match_job_to_resume(job_desc, resume_text)
if result["match"]:
    print("Match found!")
    print(f"Job Title: {job['job_title']}")
    print(f"\n MATCH: {job['job_title']} at {job['employer_name']}")
    print(f"Reason: {result['reason']}")
    print(f"URL: {job_url}")
    print("=" * 60)