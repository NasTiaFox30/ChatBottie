import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from dotenv import load_dotenv
import uuid

load_dotenv()

# ==== SPRAWDZANIE ====
REQUIRED_ENV_VARS = ["QDRANT_URL", "QDRANT_API_KEY"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise RuntimeError(f"X - No Enviroment varibles : {', '.join(missing_vars)}")


# ==== Config ====
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")  # Qdrant Cloud
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "docs")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "1024")) # embed-multilingual-v3.0 → 1024 

_client = None

def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return _client

def ensure_collection():
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

def upsert_chunks(chunks: List[str], vectors: List[List[float]], meta: List[Dict[str,Any]]):
    client = get_client()
    ensure_collection()
    points = []
    for i, (v, m, text) in enumerate(zip(vectors, meta, chunks)):
        m = dict(m)
        m.update({"text": text})
        raw_id = f"{m.get('source', 'unknown')}-{i}"
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, raw_id))
        points.append(PointStruct(id=point_id, vector=v, payload=m))
    client.upsert(collection_name=COLLECTION_NAME, points=points)

def search(query_vec: List[float], top_k: int = 5, where: Dict[str,Any] | None = None):
    client = get_client()
    ensure_collection()
    _filter = None
    if where:
        conditions = [FieldCondition(key=k, match=MatchValue(value=v)) for k,v in where.items()]
        _filter = Filter(must=conditions)
    res = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=top_k,
        query_filter=_filter,
        with_payload=True,
        with_vectors=False
    )
    return res

def reset_collection():
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
