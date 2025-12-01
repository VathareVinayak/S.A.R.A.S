import os
import requests
from typing import List, Dict, Any

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY is not set.")


def _call_gemini(model: str, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> Dict[str, Any]:
    """
    Generic Gemini text call using generateContent.
    """
    try:
        url = f"{BASE_URL}/{model}:generateContent?key={GOOGLE_API_KEY}"

        body = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        r = requests.post(url, json=body, timeout=30)
        r.raise_for_status()
        data = r.json()

        text = ""
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            text = ""

        return {"error": None, "output_text": text, "raw": data}

    except Exception as e:
        return {"error": str(e), "output_text": "", "raw": {"error": str(e)}}


def generate_text_flash(prompt: str, temperature: float = 0.0, max_tokens: int = 512) -> Dict[str, Any]:
    """
    Wrapper for a fast, cheaper Gemini model.
    Use any current flash model, e.g. gemini-2.0-flash or gemini-2.5-flash.
    """
    model = "gemini-2.0-flash"
    return _call_gemini(model, prompt, max_tokens=max_tokens, temperature=temperature)


def generate_text_pro(prompt: str, temperature: float = 0.0, max_tokens: int = 1024) -> Dict[str, Any]:
    """
    Wrapper for a higher-quality Gemini model.
    Use a current pro-style model if available in your project.
    """
    # Adjust this if you have a specific pro model (e.g. gemini-2.0-flash-lite, or future pro IDs)
    model = "gemini-2.0-flash"
    return _call_gemini(model, prompt, max_tokens=max_tokens, temperature=temperature)


def embed_texts(text_list: List[str]) -> List[List[float]]:
    """
    Embeddings API using text-embedding-004, which is still supported.
    """
    url = f"https://generativelanguage.googleapis.com/v1/models/text-embedding-004:embedContent?key={GOOGLE_API_KEY}"
    vectors: List[List[float]] = []

    for text in text_list:
        body = {
            "model": "text-embedding-004",
            "content": {"parts": [{"text": text}]},
        }

        try:
            r = requests.post(url, json=body, timeout=20)
            r.raise_for_status()
            res = r.json()
            vec = res["embedding"]["values"]
            vectors.append(vec)
        except Exception:
            vectors.append([])

    return vectors


def local_stub_summary(prompt: str, role: str = "pro") -> Dict[str, Any]:
    return {
        "error": "stub_used",
        "output_text": "(Stub) Gemini unavailable. Add API key for real output.",
        "raw": None,
    }
