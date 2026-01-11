from pypdf import PdfReader
from typing import List
import os


# Extract text from PDF #

def extract_text_from_pdf(file_path: str) -> List[str]:
    reader = PdfReader(file_path)
    pages = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append((page_num + 1, text))

    return pages



# Chunk text #

def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    return chunks
