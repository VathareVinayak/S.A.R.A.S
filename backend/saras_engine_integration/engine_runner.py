import hashlib
import os
import time
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List

 
# IMPORT ENGINE LAYERS
try:
    from saras_engine.src.tools.pdf_extractor import extract_text_or_fail
    from saras_engine.src.tools.embeddings import embeddings_for_document_bytes
    from saras_engine.src.tools.vector_store import build_store, query_store
    from saras_engine.src.agents.manager_agent import ManagerAgent
except Exception as e:
    raise ImportError(f"Engine imports failed: {e}")

 
# BASE & ENV CONFIG
 
SARAS_API_KEY = os.getenv("SARAS_API_KEY", "demo-key")

BASE_DIR = Path(__file__).resolve().parents[1]
TRACES_DIR = BASE_DIR / "traces"
UPLOADS_DIR = BASE_DIR / "uploads"

TRACES_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

 
# UTILITY HELPERS
 
def _make_task_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def _atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)

def _save_payload(task_id: str, payload: Dict[str, Any]):
    path = TRACES_DIR / f"{task_id}.json"
    _atomic_write_json(path, payload)

 
# CLEANING LAYER (MOST IMPORTANT)
 
def _clean_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts internal engine output into clean final JSON format.

    USER SHOULD SEE ONLY:
    - summary
    - final_answer
    - sections
    - citations
    - sources
    - task_id
    - mode
    """

    cleaned = {
        "status": payload.get("status"),
        "task_id": payload.get("task_id"),
        "mode": payload.get("mode"),
        "answer": payload.get("final_answer", ""),
        "summary": "",
        "sections": [],
        "citations": [],
        "sources": payload.get("sources", []),
    }

    # If final_answer is JSON (writer format), parse it
    try:
        if cleaned["answer"].strip().startswith("{"):
            parsed = json.loads(cleaned["answer"])
            cleaned["summary"] = parsed.get("summary", "")
            cleaned["sections"] = parsed.get("sections", [])
            cleaned["citations"] = parsed.get("citations", [])
            cleaned["answer"] = parsed.get("final_text", cleaned["answer"])
    except Exception:
        pass

    return cleaned

 
# NON-RAG PIPELINE
 
def run_non_rag(query: str) -> Dict[str, Any]:
    task_id = _make_task_id("nonrag")
    start = time.time()

    try:
        mgr = ManagerAgent(api_key=SARAS_API_KEY)
        engine_output = mgr.handle_request(task=query, rag_context=None)

        # Normalize internal engine output
        internal = {
            "status": "success",
            "task_id": task_id,
            "mode": "Non-RAG",
            "final_answer": engine_output["writer_agent_output"].get("text", ""),
            "sources": engine_output.get("research_agent_output", {}).get("results", []),
        }

        # CLEAN RESPONSE
        final = _clean_response(internal)

        # Log time (for server debug)
        final["server_time_ms"] = round((time.time() - start) * 1000, 2)

        return final

    except Exception as e:
        return {
            "status": "error",
            "task_id": task_id,
            "mode": "Non-RAG",
            "answer": "",
            "summary": "",
            "sections": [],
            "sources": [],
            "citations": [],
            "error": str(e)
        }

 
# RAG PIPELINE
 
def run_rag(query: str, file_bytes: bytes, filename: str,
            file_url: Optional[str] = None) -> Dict[str, Any]:

    task_id = _make_task_id("rag")
    start = time.time()

    try:
        # Save uploaded file
        safe_name = f"{uuid.uuid4().hex[:8]}_{filename}"
        saved_path = UPLOADS_DIR / safe_name
        with saved_path.open("wb") as f:
            f.write(file_bytes)

        # Extract text
        extraction = extract_text_or_fail(file_bytes)
        if extraction.get("error"):
            return {
                "status": "error",
                "task_id": task_id,
                "mode": "RAG",
                "error": extraction["error"]
            }

        full_text = extraction["text"]

        #  Chunk
        chunk_size = 3000
        chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]

        #  Embeddings
        embeddings = embeddings_for_document_bytes(file_bytes, chunks)

        #  Build vector store
        key = hashlib.sha256(file_bytes).hexdigest()
        build_store(key, chunks, embeddings)

        #  Query vector store
        from saras_engine.src.services.gemini_client import embed_texts
        q_emb = embed_texts([query])[0]
        top_chunks = query_store(key, q_emb, k=3)

        # Hand retrieved context to ManagerAgent
        retrieved_context = "\n".join([c["text_excerpt"] for c in top_chunks])
        mgr = ManagerAgent(api_key=SARAS_API_KEY)

        engine_out = mgr.handle_request(
            task=f"RAG Query: {query}",
            rag_context=retrieved_context
        )

        # Prepare internal
        internal = {
            "status": "success",
            "task_id": task_id,
            "mode": "RAG",
            "final_answer": engine_out["writer_agent_output"].get("text", ""),
            "sources": top_chunks
        }

        # CLEAN RESPONSE
        final = _clean_response(internal)
        final["server_time_ms"] = round((time.time() - start) * 1000, 2)

        return final

    except Exception as e:
        return {
            "status": "error",
            "task_id": task_id,
            "mode": "RAG",
            "answer": "",
            "summary": "",
            "sections": [],
            "sources": [],
            "citations": [],
            "error": str(e)
        }
