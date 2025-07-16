

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
