import pdfplumber
from pathlib import Path

def extract_text_from_pdf(pdf_path: str) -> str:
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"Resume PDF not found at: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return text.strip()
