from transformers import pipeline

# Load the summarization model once globally
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def generate_summary(job_description: str, resume_text: str) -> str:
    """
    Generate a summary explaining why this job is a good match based on the job description and resume content.
    """
    prompt = (
        "Analyze the resume and job posting below. Briefly summarize why the applicant is suitable for the position. \n\n", 
        f"Job Description:\n{job_description}\n\nResume:\n{resume_text}"
    )
    
    # Truncate input if it's too long for the model
    if len(prompt) > 1024:
        prompt = prompt[:1024]

    summary = summarizer(prompt, max_length=100, min_length=30, do_sample=False)
    return summary[0]['summary_text']
