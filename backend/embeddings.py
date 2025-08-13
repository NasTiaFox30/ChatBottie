import os
from dotenv import load_dotenv
from typing import List
from openai import OpenAI

load_dotenv()

# === OpenAi Config ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# === Local model ===
LOCAL_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_local_model = None

_client = None

def get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

def embed_texts(texts: List[str]) -> List[List[float]]:
    # OpenAI embeddings expect UTF-8 strings; returns 1536 dims for -3-small
    client = get_client()
    resp = client.embeddings.create(model=OPENAI_MODEL, input=texts)
    return [d.embedding for d in resp.data]
