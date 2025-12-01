from typing import Dict, Any, List
import uuid
import numpy as np

from saras_engine.src.tools.pdf_extractor import extract_text
from saras_engine.src.tools.chunker import chunk_text
from saras_engine.src.tools.embeddings import embed_texts
from saras_engine.src.tools.vector_store import build_index, persist_index, search_index, load_index

# main entrypoint
def run_rag_pipeline(file_bytes: bytes, filename: str, query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Returns:
    {
      "final_answer_context": str,         # concatenated retrieved passages
      "sources": [ {chunk metadata...} ],
      "store_name": str                   # name used for persisted index (optional)
    }
    Important operation: store_name uses a uuid so multiple uploads don't conflict.
    """
    # 1) Extract text from file
    text = extract_text(file_bytes, filename)

    # 2) Chunk text
    chunks = chunk_text(text, chunk_size=1000, overlap=200)  # tunable
    chunk_texts = [c["text"] for c in chunks]

    # When no text produced, return empty result gracefully
    if not chunk_texts:
        return {"final_answer_context": "", "sources": [], "store_name": None}

    # 3) Embed chunks
    embeddings = embed_texts(chunk_texts)  # numpy (n,d) float32

    # 4) Build FAISS index
    index = build_index(embeddings)

    # 5) Persist index & metadatas to disk for debugging / retrieval
    store_name = f"store_{uuid.uuid4().hex[:8]}"
    # store metadata per vector (chunk_id, text, extra)
    metadatas = [{"chunk_id": c["chunk_id"], "text_excerpt": c["text"][:500], "start": c["start_char"], "end": c["end_char"]} for c in chunks]
    persist_index(index, metadatas, store_name)

    # 6) Embed query and search
    q_emb = embed_texts([query])[0]
    distances, indices = search_index(index, q_emb, top_k=top_k)

    # 7) Convert results to structured sources (closest)
    sources = []
    for idx_list, dist_list in zip(indices, distances):
        for i, idx in enumerate(idx_list):
            if idx < 0:
                continue
            meta = metadatas[idx]
            sources.append({
                "chunk_id": meta["chunk_id"],
                "score": float(dist_list[i]),
                "text_excerpt": meta["text_excerpt"]
            })

    # 8) Build final_answer_context (concatenate top-k excerpts)
    final_context = "\n\n".join([s["text_excerpt"] for s in sources[:top_k]])

    return {"final_answer_context": final_context, "sources": sources, "store_name": store_name}
