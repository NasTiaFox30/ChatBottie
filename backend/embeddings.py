from typing import List
import os
import cohere
from dotenv import load_dotenv

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise RuntimeError("X - Brak COHERE_API_KEY w .env")


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Akceptuje listę tekstów, zwraca listę wektorów.
    """
    return