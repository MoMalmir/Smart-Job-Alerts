from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model once globally
model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_similarity(resume: str, job_desc: str) -> float:
    embeddings = model.encode([resume, job_desc])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return similarity
