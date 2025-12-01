from typing import Dict, Any
import json

from saras_engine.src.services.gemini_client import (
    generate_text_flash,
    generate_text_pro,
    local_stub_summary
)


class WriterAgent:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def _build_prompt(self, task_prompt: str, retrieved_context: str, guidelines: str) -> str:
        return f"""
You are S.A.R.A.S WriterAgent. Respond ONLY in valid JSON.
JSON format:
{{
  "summary": "...",
  "final_text": "...",
  "sections": [{{"heading":"...", "content":"..."}}],
  "citations": [{{"chunk_id":"...", "excerpt":"..."}}]
}}

Task:
\"\"\"{task_prompt}\"\"\"

Retrieved Context:
\"\"\"{retrieved_context}\"\"\"

Guidelines:
{guidelines}

STRICT: Return ONLY JSON.
"""

    def write_article(self, task_prompt: str, context: Dict[str, Any], mode: str) -> Dict[str, Any]:
        retrieved_context = context.get("final_answer_context", "")

        if mode == "RAG":
            model_fn = generate_text_pro
            guidelines = (
                "Use retrieved context for evidence. "
                "Cite chunk_id when possible."
            )
        else:
            model_fn = generate_text_flash
            guidelines = "Answer shortly & clearly."

        prompt = self._build_prompt(task_prompt, retrieved_context, guidelines)

        # call model
        res = model_fn(prompt)

        # fallback
        if res.get("error") or not res.get("output_text"):
            fb = local_stub_summary(prompt, role="pro" if mode == "RAG" else "flash")
            return {
                "text": fb["output_text"],
                "summary": fb["output_text"],
                "sections": [],
                "citations": [],
            }

        raw_text = res["output_text"].strip()

        # parse JSON
        try:
            parsed = json.loads(raw_text)
        except Exception:
            parsed = {
                "summary": raw_text[:200],
                "final_text": raw_text,
                "sections": [],
                "citations": []
            }

        return {
            "text": parsed.get("final_text", raw_text),
            "summary": parsed.get("summary", ""),
            "sections": parsed.get("sections", []),
            "citations": parsed.get("citations", [])
        }
