import re
from typing import List

def extract_keywords(text: str, top_k: int = 10) -> List[str]:
    # Important operation: simple regex tokenization and deduplication
    if not text:
        return []
    words = re.findall(r"[A-Za-z]{3,}", text)
    unique = list(dict.fromkeys(words))
    return unique[:top_k]
