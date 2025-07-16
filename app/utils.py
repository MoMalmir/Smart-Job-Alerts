# utils.py

import fitz  # PyMuPDF
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"Resume PDF not found at: {pdf_path}")

    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()
