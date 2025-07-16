from semantic_matcher import compute_similarity


def match_job_to_resume(
    job_description: str, resume_text: str, threshold: float
) -> dict:
    score = compute_similarity(resume_text, job_description)

    if score >= threshold:
        return {
            "match": True,
            "reason": f"Semantic similarity score: {score:.2f} (above threshold)",
        }
    else:
        return {
            "match": False,
            "reason": f"Semantic similarity score: {score:.2f} (below threshold)",
        }
