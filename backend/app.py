import os
import uuid
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

load_dotenv()

# ==== SPRAWDZANIE ====
REQUIRED_ENV_VARS = ["QDRANT_URL", "QDRANT_API_KEY", "GEMINI_API_KEY"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing_vars:
    raise RuntimeError(f"X - No Enviroment varibles (.ENV) : {', '.join(missing_vars)} ")

# ===== Local IMPORTS =====
from embeddings import embed_texts 
from document_parser import parse_any, chunk_text, clean_text
from qdrant_utils import upsert_chunks, search, reset_collection, ensure_collection


# ===== Config =====
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ~~ Konfiguracja FastAPI:
app = FastAPI(title="Chatbot RAG + Gemini", version="2.0.0")

# CORS (testy lokalne)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # w produkcji zawęź do domeny frontendu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Schemy =====
class ChatRequest(BaseModel):
    query: str
    top_k: int = 5

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str,Any]]

class CMSRecord(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    body: str
    url: Optional[str] = None
    file_type: Optional[str] = "cms"

class CMSImport(BaseModel):
    collection: Optional[str] = "docs"
    records: List[CMSRecord]

# ===== Generacja odpowiedzi za pomocą Gemini =====
async def generate_with_gemini(prompt: str, temperature: float = 0.7) -> str:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature}
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, params=params, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Gemini error: {response.text}")
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

# ===== Endpoints =====
@app.get("/health")
def health():
    ensure_collection()
    return {"status": "ok", "model": "Gemini 1.5 Flash"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    query = clean_text(req.query)
    if not query:
        raise HTTPException(status_code=400, detail="Puste zapytanie.")

    # 1️) Wektoryzacja
    q_vec = embed_texts([query])[0]
    # 2️) Szukanie fragmentów
    hits = search(q_vec, top_k=max(1, min(10, req.top_k)))
    if not hits:
        return ChatResponse(
            answer="Nie znalazłem danych ;( Spróbuj zadać inne pytanie lub wgraj dokumenty.",
            sources=[]
        )
    # 3️) Formowanie kontekstu
    context = "\n".join(r.payload.get("text", "") for r in hits[:3])
    prompt = f"""
Odpowiadaj na pytania użytkownika, korzystając z podanego kontekstu.
Jeżeli w kontekście nie ma odpowiedzi, szczerze powiedz, że nie wiesz.

Pytanie: {query}

Kontekst:
{context}
"""
    
    

@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    total_chunks = 0
    for f in files:
        try:
            content = await f.read()
            text = parse_any(f.filename, content)
            chunks = chunk_text(text)
            vecs = embed_texts(chunks)
            meta = [{
                "id": f"{f.filename}-{i}",
                "source": f.filename,
                "file_type": f.filename.split(".")[-1].lower(),
            } for i in range(len(chunks))]
            upsert_chunks(chunks, vecs, meta)
            total_chunks += len(chunks)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Błąd pliku {f.filename}: {e}")
    return {"indexed": total_chunks}

@app.post("/cms/import")
def import_cms(data: CMSImport):
    chunks, meta = [], []
    for rec in data.records:
        base_meta = {
            "id": rec.id or str(uuid.uuid4()),
            "source": rec.title or "CMS",
            "file_type": rec.file_type or "cms",
            "url": rec.url,
            "title": rec.title
        }
        text = ((rec.title + " — ") if rec.title else "") + (rec.body or "")
        for i, ch in enumerate(chunk_text(text)):
            chunks.append(ch)
            m = dict(base_meta)
            m["id"] = f"{base_meta['id']}-{i}"
            meta.append(m)
    if not chunks:
        raise HTTPException(status_code=400, detail="Brak danych do importu.")
    vecs = embed_texts(chunks)
    upsert_chunks(chunks, vecs, meta)
    return {"indexed": len(chunks)}

@app.post("/reset")
def reset():
    reset_collection()
    return {"status": "reset"}
