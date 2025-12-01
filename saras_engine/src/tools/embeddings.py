import requests
import os
from typing import List, Dict

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBED_URL = (
    "https://generativelanguage.googleapis.com/v1/models/"
    "text-embedding-004:embedContent?key=" + GOOGLE_API_KEY
)

    
# 1) Embed a single text
    
def embed_one(text: str) -> List[float]:
    body = {
        "model": "text-embedding-004",
        "content": {"parts": [{"text": text}]}
    }

    r = requests.post(EMBED_URL, json=body, timeout=20)
    r.raise_for_status()
    data = r.json()

    return data["embedding"]["values"]  # ALWAYS 768 dims


    
# 2) Embed a list of texts
    
def embed_texts(text_list: List[str]) -> List[List[float]]:
    vectors = []
    for text in text_list:
        try:
            vectors.append(embed_one(text))
        except Exception:
            vectors.append([0.0] * 768)  # SAFE fallback
    return vectors


    
# 3) Embed all document chunks
    
def embeddings_for_document_bytes(doc_bytes: bytes, chunks: List[str]):
    return embed_texts(chunks)
