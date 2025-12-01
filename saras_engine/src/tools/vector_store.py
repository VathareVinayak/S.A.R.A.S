import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from scipy.spatial.distance import cosine

# Root directory for persistent vector stores
BASE_DIR = Path(__file__).resolve().parents[3]  # backend/saras_engine_integration/...
STORE_DIR = BASE_DIR / "vector_stores"
STORE_DIR.mkdir(parents=True, exist_ok=True)


  
# INTERNAL UTILITIES
  
def _store_path(key: str) -> Path:
    """Return full json filepath for a vector store keyed by hash."""
    return STORE_DIR / f"{key}.json"


def _save_json(path: Path, data: Dict[str, Any]):
    """Atomic JSON write (safe)."""
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    tmp.replace(path)


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


  
# BUILD STORE
  
def build_store(key: str, chunks: List[str], embeddings: List[List[float]]):
    """
    Build a vector store (chunks + embeddings) and save to disk.

    Expected: embeddings shape = (num_chunks, 768)
    """

    if not embeddings or len(embeddings) != len(chunks):
        raise ValueError("Embeddings list must match chunks list length.")

    store = {
        "chunks": chunks,
        "embeddings": embeddings,    # list of 768-dim vectors
        "dim": 768,
        "count": len(chunks),
    }

    _save_json(_store_path(key), store)


  
# QUERY STORE – top-k cosine similarity
  
def query_store(
    key: str,
    query_embedding: List[float],
    k: int = 3
) -> List[Dict[str, Any]]:
    """
    Perform similarity search for query_embedding in the stored document.

    Returns:
    [
        {
            "chunk_id": "chunk-0",
            "score": 0.91,
            "text_excerpt": "first 300 chars..."
        },
        ...
    ]
    """

    path = _store_path(key)
    if not path.exists():
        raise FileNotFoundError(f"Vector store not found for key: {key}")

    store = _load_json(path)

    chunks = store["chunks"]
    embeddings = np.array(store["embeddings"], dtype=float)
    dim = store.get("dim", 768)

    query_vec = np.array(query_embedding, dtype=float)
    if query_vec.shape[0] != dim:
        raise ValueError(
            f"Query embedding dim mismatch: got {query_vec.shape[0]} but expected {dim}"
        )

    # Compute cosine similarity for each chunk
    similarities = []
    for i, emb_vec in enumerate(embeddings):
        sim = 1 - cosine(query_vec, emb_vec)  # cosine similarity
        similarities.append((i, sim))

    # Sort by similarity score descending
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Build output structure
    top_results = []
    for idx, score in similarities[:k]:
        excerpt = chunks[idx][:300].replace("\n", " ").strip()
        top_results.append({
            "chunk_id": f"chunk-{idx}",
            "score": float(score),
            "text_excerpt": excerpt
        })

    return top_results
