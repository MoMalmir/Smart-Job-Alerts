from job_tracker import load_seen_jobs, save_seen_jobs, is_new_job
import json
import requests

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



# lets open the file kobs.json and read the the jobs from it and store it in a variable called extracted_jobs
with open("jobs.json", 'r', encoding='utf-8') as f:
    extracted_jobs = json.load(f)



def get_full_description(job):
    desc = job.get("job_description", "")
    highlights = job.get("job_highlights", {})
    qualifications = " ".join(highlights.get("Qualifications", []))
    responsibilities = " ".join(highlights.get("Responsibilities", []))
    return f"{desc}\nQualifications: {qualifications}\nResponsibilities: {responsibilities}"


example = 4
job_discription = get_full_description(extracted_jobs["data"][example])

print("Job Description:", job_discription)


# now let try out the similaritey function 
from job_matcher import match_job_to_resume
from utils import extract_text_from_pdf


resume_pdf_path = "resume.pdf"
resume_text = extract_text_from_pdf(resume_pdf_path)
print("\n\n\n\n\n\n\n Resume Text:", resume_text)



score = match_job_to_resume(resume_text, job_discription)
print ("\n\n\n\n The score is:", score)