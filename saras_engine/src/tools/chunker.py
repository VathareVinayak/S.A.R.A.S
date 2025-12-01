from typing import List, Dict
import uuid

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    if not text:
        return []
    chunks = []
    start = 0
    text_len = len(text)
    idx = 0
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({
                "chunk_id": f"chunk-{idx}",
                "text": chunk_text,
                "start_char": start,
                "end_char": end
            })
            idx += 1
        # advance start with overlap
        start = end - overlap if (end - overlap) > start else end
    return chunks
