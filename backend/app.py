import os
import uuid
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ==== SPRAWDZANIE ====
REQUIRED_ENV_VARS = ["QDRANT_URL", "QDRANT_API_KEY"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing_vars:
    raise RuntimeError(f"X - No Enviroment varibles (.ENV) : {', '.join(missing_vars)} ")

# ===== Local IMPORTS =====
from embeddings import embed_texts 
from document_parser import parse_any, chunk_text, clean_text
from qdrant_utils import upsert_chunks, search, reset_collection, ensure_collection


# ===== Config =====
# OPENAI_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
# COHERE_MODEL = "embed-multilingual-v3.0"


# ~~ Konfiguracja FastAPI:
app = FastAPI(title="Chatbot RAG API", version="1.0.0")

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

# ===== Helpers =====
def build_answer(query: str, hits) -> ChatResponse:
    # Prosty "extractive" styl: wybierz kilka najlepszych chunków i sklej wraz z lekkim podsumowaniem.
    if not hits:
        return ChatResponse(answer="Nie znalazłem pasujących danych. Spróbuj doprecyzować pytanie lub wgrać pliki/CMS.", sources=[])

    context_parts = []
    sources = []
    for r in hits:
        payload = r.payload or {}
        txt = payload.get("text", "")
        context_parts.append(txt)
        # zbuduj metadane do pokazania w UI
        sources.append({
            "id": payload.get("id") or str(uuid.uuid4())[:8],
            "source": payload.get("source") or payload.get("title") or "fragment",
            "file_type": payload.get("file_type") or "text",
            "url": payload.get("url"),
        })

    # Bardzo prosta odpowiedź: streszczenie + zacytowane fragmenty (skrót)
    # (Możesz tu podmienić na generatywną odpowiedź LLM, przekazując kontekst do modelu.)
    summary = f"Na podstawie {len(hits)} dopasowanych fragmentów:"
    snippets = []
    for p in context_parts[:3]:
        p = p.strip()
        if len(p) > 300:
            p = p[:300] + "…"
        snippets.append(f"• {p}")
    answer = summary + "\n" + "\n".join(snippets)
    return ChatResponse(answer=answer, sources=sources[:5])

# ===== Endpoints =====
@app.get("/health")
def health():
    ensure_collection()
    return {"status": "ok", "embedding_model": "all-MiniLM-L6-v2"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    query = clean_text(req.query)
    if not query:
        raise HTTPException(status_code=400, detail="Puste zapytanie.")
    q_vec = embed_texts([query])[0]
    hits = search(q_vec, top_k=max(1, min(10, req.top_k)))
    return build_answer(query, hits)

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
