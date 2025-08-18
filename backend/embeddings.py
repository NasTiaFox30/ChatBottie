from typing import List
import os
import cohere
from dotenv import load_dotenv

load_dotenv()




def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Akceptuje listę tekstów, zwraca listę wektorów.
    """
    return