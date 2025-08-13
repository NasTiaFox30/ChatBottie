import os
from dotenv import load_dotenv
from typing import List
from openai import OpenAI

load_dotenv()

# === OpenAi Config ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# === Cohere cofig ===
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# === Local model ===
LOCAL_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_local_model = None


def _load_local_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        print(f"🔄 Завантажую локальну модель {LOCAL_MODEL_NAME}...")
        _local_model = SentenceTransformer(LOCAL_MODEL_NAME)
    return _local_model



def embed_texts(texts: List[str]) -> List[List[float]]:
     # 1. OpenAI
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            resp = client.embeddings.create(model=OPENAI_MODEL, input=texts)
            return [d.embedding for d in resp.data]
        except Exception as e:
            if "insufficient_quota" in str(e) or "You exceeded your current quota" in str(e):
                print("!!! Limit wyczrpany OpenAI. Wykorzytuję lokalny model...")
            else:
                print(f"Błąd OpenAI: {e}. Wykorzytuję lokalny model...")
    
    # 2. Lokalny model 
    model = _load_local_model()
    vecs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vecs.tolist()
