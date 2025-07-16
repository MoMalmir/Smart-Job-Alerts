import requests
import os

# RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")  # Set this in your environment
# RAPIDAPI_HOST = "jsearch.p.rapidapi.com"

def fetch_jobs(RAPIDAPI_KEY,RAPIDAPI_HOST, keyword, location, remote, date_posted, num_pages=1):
    url = "https://jsearch.p.rapidapi.com/search"

    querystring = {
        "query": keyword,
        "location": location,
        "remote_jobs_only": str(remote).lower(),  # "true"/"false"
        "date_posted": date_posted,
        "page": "1",
        "num_pages": str(num_pages)
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()["data"]
    except Exception as e:
        print(f"Failed to fetch jobs for '{keyword}': {e}")
        return []
