from typing import List, Tuple, Iterable
from io import BytesIO
import pandas as pd
from docx import Document as DocxDocument
from pdfminer.high_level import extract_text
import re

def clean_text(s: str) -> str:
    s = re.sub(r'\s+', ' ', s or '').strip()
    return s

def split_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]

def chunk_text(text: str, max_chars: int = 1000, overlap: int = 150) -> List[str]:
    text = clean_text(text)
    sentences = split_sentences(text)
    chunks = []
    current = ""

    for sent in sentences:
        if len(current) + len(sent) + 1 <= max_chars:
            current += (" " if current else "") + sent
        else:
            if current:
                chunks.append(current.strip())
            current = sent

    if current:
        chunks.append(current.strip())

    # overlap (poprzednia część)
    result = []
    for i, chunk in enumerate(chunks):
        if i > 0 and overlap > 0:
            prev = chunks[i-1]
            overlap_text = prev[-overlap:]
            chunk = overlap_text + " " + chunk
        result.append(chunk.strip())

    return result

# === Parser'y===

def parse_pdf(file_bytes: bytes) -> str:
    return clean_text(extract_text(BytesIO(file_bytes)))

def parse_docx(file_bytes: bytes) -> str:
    f = BytesIO(file_bytes)
    doc = DocxDocument(f)
    paras = [p.text for p in doc.paragraphs]
    return clean_text("\n".join(paras))

def parse_csv(file_bytes: bytes) -> str:
    f = BytesIO(file_bytes)
    df = pd.read_csv(f)
    # prosta linearizacja CSV -> tekst
    lines = []
    for _, row in df.iterrows():
        parts = [f"{col}: {row[col]}" for col in df.columns]
        lines.append("; ".join(map(str, parts)))
    return clean_text("\n".join(lines))

def parse_any(filename: str, file_bytes: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        return parse_pdf(file_bytes)
    if name.endswith(".docx"):
        return parse_docx(file_bytes)
    if name.endswith(".csv"):
        return parse_csv(file_bytes)
    # fallback: traktujemy jako txt
    return clean_text(file_bytes.decode("utf-8", errors="ignore"))
