from typing import List
import os
import cohere
from dotenv import load_dotenv

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise RuntimeError("X - Brak COHERE_API_KEY w .env")

_client = cohere.Client(COHERE_API_KEY)

_MODEL = "embed-multilingual-v3.0"

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Akceptuje listę tekstów, zwraca listę wektorów.
    """
    return