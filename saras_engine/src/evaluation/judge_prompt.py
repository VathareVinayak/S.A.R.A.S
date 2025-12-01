
from typing import Dict


def build_judge_prompt(reference: str, candidate: str) -> str:
    prompt = f"""
You are an objective content evaluation assistant. Compare the CANDIDATE text to the REFERENCE text.
Return a JSON object only (no additional commentary) with these fields:
- coherence: number between 0.0 and 1.0 (how coherent and well-structured is the candidate)
- factuality: number between 0.0 and 1.0 (how many claims are supported by the reference)
- relevance: number between 0.0 and 1.0 (how on-topic is the candidate)
- comment: a brief 1-2 sentence justification.

REFERENCE:
\"\"\"{reference}\"\"\"

CANDIDATE:
\"\"\"{candidate}\"\"\"

Return only a valid JSON object.
"""
    return prompt
