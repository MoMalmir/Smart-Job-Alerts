# import requests
# import os


# def fetch_jobs(
#     RAPIDAPI_KEY, RAPIDAPI_HOST, keyword, location, remote, date_posted, num_pages=1
# ):
#     url = "https://jsearch.p.rapidapi.com/search"

#     querystring = {
#         "query": keyword,
#         "location": location,
#         "remote_jobs_only": str(remote).lower(),  # "true"/"false"
#         "date_posted": date_posted,
#         "page": "1",
#         "num_pages": str(num_pages),
#     }

#     headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": RAPIDAPI_HOST}

#     try:
#         response = requests.get(url, headers=headers, params=querystring)
#         response.raise_for_status()
#         return response.json()["data"]
#     except Exception as e:
#         print(f"Failed to fetch jobs for '{keyword}': {e}")
#         return []



import requests

def fetch_jobs(
    api_key,
    api_host,
    query,
    page,
    country="us",
    language="",
    date_posted="all",
    work_from_home=False,
    employment_types=None,
    job_requirements=None,
    radius=None,
    exclude_publishers=None,
    fields=None
):
    url = "https://jsearch.p.rapidapi.com/search"

    params = {
        "query": query,
        "page": page,
        "country": country,
        "date_posted": date_posted,
        "num_pages": 1  # Only 1 page per request (your loop handles multiple)
    }

    if language:
        params["language"] = language

    if work_from_home:
        params["work_from_home"] = "true"

    if employment_types:
        params["employment_types"] = ",".join(employment_types)

    if job_requirements:
        params["job_requirements"] = ",".join(job_requirements)

    if radius is not None:
        params["radius"] = str(radius)

    if exclude_publishers:
        params["exclude_job_publishers"] = ",".join(exclude_publishers)

    if fields:
        params["fields"] = ",".join(fields)

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"❌ Failed to fetch jobs for '{query}' on page {page}: {e}")
        return []
