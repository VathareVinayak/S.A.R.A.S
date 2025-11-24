# backend/saras_engine_integration/engine_runner.py
"""
Engine runner connecting Django backend <-> S.A.R.A.S AI Engine.

Features:
- Runs Non-RAG tasks using ManagerAgent.handle_request()
- Runs RAG tasks (file-based) using embedding + vector-store retrieval
- Saves every result into backend/traces/<task_id>.json
- Produces Option-C response format:
    final_answer + sources + tools_used + agents + metadata + trace

Important operations are commented inline so you can see why each step exists.
"""

import hashlib
import os
import time
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List

# ------------------------------------------------------------------
# NOTE: these imports expect your saras_engine package to be importable.
# Ensure Python path includes project root (manage.py location) or
# that saras_engine is installed as a package in your venv.
# ------------------------------------------------------------------
try:
    from saras_engine.src.tools.pdf_extractor import extract_text_or_fail
    from saras_engine.src.tools.embeddings import embeddings_for_document_bytes
    from saras_engine.src.tools.vector_store import build_store, query_store
    from saras_engine.src.agents.manager_agent import ManagerAgent
except Exception as e:
    # Important operation: surface a clear import error (helps diagnose PYTHONPATH issues)
    raise ImportError(f"Engine imports failed (saras_engine.*). Fix package path or imports. Error: {e}")

# Environment-configurable API key for agents (optional)
SARAS_API_KEY = os.getenv("SARAS_API_KEY", "demo-key")

# Base directories for storing traces and uploaded files (create if missing)
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
TRACES_DIR = BASE_DIR / "traces"
UPLOADS_DIR = BASE_DIR / "uploads"

TRACES_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------
# Utility helpers
# -------------------------
def _make_task_id(prefix: str) -> str:
    """Important operation: create short unique task id with readable prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    """
    Important operation: atomically write JSON by writing to a tmp file then renaming
    - prevents partial files if the process is killed while writing
    """
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def _save_payload(task_id: str, payload: Dict[str, Any]) -> None:
    """Persist the full response payload to backend/traces/ for later retrieval."""
    path = TRACES_DIR / f"{task_id}.json"
    _atomic_write_json(path, payload)


# -------------------------
# Normalize manager output
# -------------------------
def _normalize_manager_output(manager_output: Dict[str, Any], task_id: str, mode: str,
                              file_ref: Optional[str] = None) -> Dict[str, Any]:
    """
    Convert ManagerAgent output to Option-C contract:
    - final_answer: prefer writer_agent_output.text or final_text, fallback to research summary
    - sources: manager_output['sources'] OR constructed from research results
    - tools_used / agents / metadata are preserved where available
    - trace: use manager_output['trace'] if present
    """
    writer_out = manager_output.get("writer_agent_output")
    research_out = manager_output.get("research_agent_output")

    final_answer = ""
    writer_used_fallback = False
    writer_citations: List[Dict[str, str]] = []

    # Important operation: handle writer output shape (dict preferred, string fallback)
    if isinstance(writer_out, dict):
        final_answer = writer_out.get("text") or writer_out.get("final_text") or ""
        writer_citations = writer_out.get("citations", []) or []
        writer_used_fallback = writer_out.get("used_fallback", False)
    elif isinstance(writer_out, str):
        final_answer = writer_out
    else:
        # Affordable fallback: synthesize from research output if writer failed
        if isinstance(research_out, dict):
            final_answer = research_out.get("research_summary") or research_out.get("summary", "") or str(research_out)
        else:
            final_answer = str(manager_output)

    # Import sources: prefer explicit manager_output['sources']
    sources = manager_output.get("sources", [])
    if not sources and isinstance(research_out, dict):
        results = research_out.get("results") or research_out.get("sources") or []
        if isinstance(results, list):
            for i, r in enumerate(results):
                sources.append({
                    "chunk_id": f"r{i+1}",
                    "page": r.get("page") if isinstance(r, dict) else None,
                    "text_excerpt": r.get("snippet", r.get("text", "")) if isinstance(r, dict) else str(r)[:200]
                })

    # Tools used and agents
    metadata = manager_output.get("metrics", {}) if isinstance(manager_output.get("metrics", {}), dict) else {}
    tools_used = metadata.get("tools_used", []) if isinstance(metadata.get("tools_used", []), list) else []
    agents = manager_output.get("metrics", {}).get("agents", None) or ["ManagerAgent", "ResearchAgent", "WriterAgent"]

    # Add file ref if present
    if file_ref:
        metadata["file_ref"] = file_ref

    # Add writer flags to metadata to make debugging easier
    metadata["writer_used_fallback"] = writer_used_fallback
    metadata["writer_citations"] = writer_citations

    trace = manager_output.get("trace", [])
    if not isinstance(trace, list):
        trace = []

    payload = {
        "status": "success" if final_answer else "error",
        "task_id": task_id,
        "mode": mode,
        "final_answer": final_answer,
        "sources": sources,
        "tools_used": tools_used,
        "agents": agents,
        "metadata": metadata,
        "trace": trace
    }

    return payload


# -------------------------
# NON-RAG pipeline
# -------------------------
def run_non_rag(query: str) -> Dict[str, Any]:
    """
    Important operations:
    - instantiate ManagerAgent
    - call handle_request(query)
    - normalize + persist payload
    """
    task_id = _make_task_id("nonrag")
    start = time.time()

    try:
        # Instantiate ManagerAgent (fresh instance — avoids cross-request state)
        mgr = ManagerAgent(api_key=SARAS_API_KEY)

        # Run orchestrator (Non-RAG mode). ManagerAgent may internally call tools.
        engine_output = mgr.handle_request(task=query, rag_context="", mode="Non-RAG")

        # Normalize to Option-C response
        payload = _normalize_manager_output(engine_output, task_id=task_id, mode="Non-RAG", file_ref=None)

        # Add timing + query metadata
        payload.setdefault("metadata", {})
        payload["metadata"].update({
            "execution_time_seconds": round(time.time() - start, 3),
            "query": query
        })

        # Persist trace for future inspection
        _save_payload(task_id, payload)
        return payload

    except Exception as e:
        # Important operation: always persist error payload for post-mortem
        err = {
            "status": "error",
            "task_id": task_id,
            "mode": "Non-RAG",
            "final_answer": "",
            "sources": [],
            "tools_used": [],
            "agents": ["ManagerAgent"],
            "metadata": {"error": str(e)},
            "trace": [{"actor": "engine_runner", "action": "exception", "details": str(e)}]
        }
        _save_payload(task_id, err)
        return err


# -------------------------
# RAG pipeline (embedding + store + retrieval)
# -------------------------
def run_rag(query: str, file_bytes: bytes, filename: str, file_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Steps (Important operations called out):
    1) Save file to disk (uploads/)
    2) Extract text (PyMuPDF preferred; fall back to explicit error)
    3) Chunk document for embeddings
    4) Compute embeddings for chunks
    5) Build/persist vector store (keyed by doc checksum)
    6) Embed query and query store -> top-k chunks
    7) Call ManagerAgent passing retrieved context in rag_context
    8) Normalize + persist result
    """
    task_id = _make_task_id("rag")
    start = time.time()

    try:
        # 1) Save uploaded file bytes to uploads directory (unique safe filename)
        safe_name = f"{uuid.uuid4().hex[:8]}_{os.path.basename(filename)}"
        saved_path = UPLOADS_DIR / safe_name
        with saved_path.open("wb") as f:
            f.write(file_bytes)

        # 2) Extract text using your pdf_extractor helper (non-ocr preferred)
        extraction = extract_text_or_fail(file_bytes)
        # Important operation: check for explicit extraction errors and return structured payload
        if extraction.get("error"):
            err_payload = {
                "status": "error",
                "task_id": task_id,
                "mode": "RAG",
                "final_answer": "",
                "metadata": {"error": extraction.get("message", extraction.get("error"))},
                "trace": [{"actor": "engine_runner", "action": "extraction_failed", "details": extraction}]
            }
            _save_payload(task_id, err_payload)
            return err_payload

        full_text = extraction.get("text", "")
        pages_info = extraction.get("pages", [])  # optional

        # 3) Chunking - simple character-based split (tune later if needed)
        chunk_size = 3000  # chars per chunk (empiric)
        chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)] or [full_text]

        # 4) Compute embeddings for document chunks (service function)
        # Important operation: embeddings_for_document_bytes is expected to return a list of vectors aligned to chunks
        embeddings = embeddings_for_document_bytes(doc_bytes=file_bytes, chunks=chunks)

        # 5) Build and persist vector store for this document
        # Use document checksum as stable key for caching / retrieval
        key = hashlib.sha256(file_bytes).hexdigest()
        build_store(key=key, chunks=chunks, embeddings=embeddings)

        # 6) Embed query and query the store for top-k matching chunks
        # NOTE: embed_texts should be implemented in your gemini_client or embeddings service.
        # Defer import to here so the module can be replaced easily in tests.
        try:
            from saras_engine.src.services.gemini_client import embed_texts
        except Exception:
            # If embed_texts is missing, raise an informative error (helps debugging)
            raise ImportError("embed_texts not available in saras_engine.src.services.gemini_client")

        q_embs = embed_texts([query])
        if not q_embs or not isinstance(q_embs, list):
            raise RuntimeError("embed_texts did not return a list of embeddings")

        q_emb = q_embs[0]
        top_chunks = query_store(key=key, query_embedding=q_emb, k=3)  # returns list of {text_excerpt, chunk_id, score}

        # 7) Prepare retrieved context text (concatenate top excerpts)
        retrieved_context_text = "\n".join([c.get("text_excerpt", "") for c in top_chunks])

        # 8) Build a descriptive task text for ManagerAgent
        task_text = f"RAG task — Query: {query} ; FilePath: {str(saved_path)} ; RetrievedContext: {retrieved_context_text}"

        # 9) Instantiate ManagerAgent and hand off (pass rag_context so writer can choose Pro model)
        mgr = ManagerAgent(api_key=SARAS_API_KEY)
        manager_output = mgr.handle_request(task=task_text, rag_context=retrieved_context_text, mode="RAG")

        # 10) Normalize manager output into Option-C payload
        payload = _normalize_manager_output(manager_output, task_id=task_id, mode="RAG", file_ref=str(saved_path))

        # 11) Add technical metadata (execution time, file refs, vector store id)
        payload.setdefault("metadata", {})
        payload["metadata"].update({
            "execution_time_seconds": round(time.time() - start, 3),
            "saved_path": str(saved_path),
            "original_filename": filename,
            "vector_store": f"store_{key[:8]}",
            "num_sources": len(top_chunks)
        })

        # 12) Add the top_chunks as 'sources' (useful for frontend)
        payload["sources"] = top_chunks

        # 13) Persist trace
        _save_payload(task_id, payload)
        return payload

    except Exception as e:
        # Important: persist error payload for debugging
        err_payload = {
            "status": "error",
            "task_id": task_id,
            "mode": "RAG",
            "final_answer": "",
            "metadata": {"error": str(e)},
            "trace": [{"actor": "engine_runner", "action": "exception", "details": str(e)}]
        }
        try:
            _save_payload(task_id, err_payload)
        except Exception:
            # best-effort persistence only
            pass
        return err_payload
