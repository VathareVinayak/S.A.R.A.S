from typing import Dict, Any, List
import re


def coherence_score(text: str) -> float:
    if not text:
        return 0.0

    # count lines and tokens
    tokens = re.findall(r"\w+", text)
    token_count = len(tokens)

    # basic heuristics
    if token_count < 50:
        base = 0.2
    elif token_count < 200:
        base = 0.6
    else:
        base = 0.8

    # give a bonus if headings appear
    headings = 1 if re.search(r"(^|\n)#+\s", text) or "Outline" in text else 0
    score = min(1.0, base + 0.1 * headings)
    return round(score, 3)


def factuality_score(research: Dict[str, Any], candidate: str) -> float:

    if not research or not candidate:
        return 0.0

    keywords = research.get("keywords", [])
    if not keywords:
        return 0.0

    cand_tokens = set([t.lower() for t in re.findall(r"\w+", candidate)])
    match_count = sum(1 for kw in keywords if kw.lower() in cand_tokens)

    # normalized score
    score = match_count / max(1, len(keywords))
    return round(min(1.0, score), 3)


def length_score(candidate: str) -> float:
    if not candidate:
        return 0.0
    token_count = len(re.findall(r"\w+", candidate))
    if token_count < 50:
        return 0.2
    elif token_count < 400:
        return 0.7
    else:
        return 0.9


def overall_score(research: Dict[str, Any], candidate: str, weights: Dict[str, float] = None) -> Dict[str, Any]:
    if weights is None:
        weights = {"coherence": 0.4, "factuality": 0.4, "length": 0.2}

    coh = coherence_score(candidate)
    fact = factuality_score(research, candidate)
    lng = length_score(candidate)

    final = round(coh * weights["coherence"] + fact * weights["factuality"] + lng * weights["length"], 3)

    return {
        "coherence": coh,
        "factuality": fact,
        "length": lng,
        "final_score": final,
        "weights": weights
    }

def llm_judge(reference: str, candidate: str, api_key: str = None) -> Dict[str, Any]:
    raise NotImplementedError("LLM judge hook not implemented. Use overall_score() for offline evaluation.")
