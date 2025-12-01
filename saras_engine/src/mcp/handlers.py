from fastapi import HTTPException
from typing import Dict
from saras_engine.src.tools import google_search, extract_keywords, outline_generator, tool_registry

def handle_google_search(payload: Dict):
    # Important operation: validate payload
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="missing 'query'")
    # Important operation: call the tool implementation (mock or real)
    return google_search.search(query=query, api_key=payload.get("api_key"), use_real=False)

def handle_extract_keywords(payload: Dict):
    text = payload.get("text", "")
    return {"keywords": extract_keywords.extract_keywords(text)}

def handle_outline_start(payload: Dict):
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(status_code=400, detail="missing 'topic'")
    return outline_generator.start_outline(topic)
