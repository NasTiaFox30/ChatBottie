from typing import List
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Akceptuje listę tekstów, zwraca listę wektorów.
    """
    return _model.encode(texts, convert_to_numpy=True).tolist()