# from transformers import pipeline

# # Load the summarization model once globally
# summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# def generate_summary(job_description: str, resume_text: str) -> str:
#     """
#     Generate a summary explaining why this job is a good match based on the job description and resume content.
#     """
#     prompt = (
#         "Analyze the resume and job posting below. Briefly summarize why the applicant is suitable for the position. \n\n" 
#         f"Job Description:\n{job_description}\n\nResume:\n{resume_text}"
#     )
    

#     summary = summarizer(prompt, max_length=100, min_length=30, do_sample=False)
#     return summary[0]['summary_text']


from transformers import pipeline

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def truncate_text(text, max_tokens=800):
    return " ".join(text.split()[:max_tokens])

def generate_summary(job_description, resume_text):
    # Truncate both to stay within ~1024 tokens combined
    short_job = truncate_text(job_description, 500)
    short_resume = truncate_text(resume_text, 200)

    prompt = f"Based on the resume and job description below, explain in 3–4 sentences why this job is a good match for the candidate.\n\nJob Description:\n{short_job}\n\nResume:\n{short_resume}"

    summary = summarizer(prompt, max_length=120, min_length=40, do_sample=False)
    return summary[0]['summary_text']
