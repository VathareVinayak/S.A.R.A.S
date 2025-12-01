import uuid
from typing import Dict, Any

# In-memory store (kept only for compatibility)
_LONG_OP_STORE: Dict[str, Dict[str, Any]] = {}


def start_outline(topic: str) -> Dict[str, Any]:
    """Return outline immediately (no long-running simulation)."""
    task_id = str(uuid.uuid4())

    outline = {
        "title": topic,
        "sections": [
            {"heading": "Introduction", "notes": "Define the topic and motivation."},
            {"heading": "Background", "notes": "Summarize key ideas."},
            {"heading": "Analysis", "notes": "Important observations and insights."},
            {"heading": "Conclusion", "notes": "Final summary and next steps."}
        ]
    }

    # store instantly completed outline
    _LONG_OP_STORE[task_id] = {
        "task_id": task_id,
        "topic": topic,
        "outline": outline,
        "status": "completed"
    }

    return {
        "task_id": task_id,
        "requires_approval": False,
        "outline_preview": outline
    }


def approve_outline(task_id: str) -> Dict[str, Any]:
    """Kept for compatibility. Instantly returns the stored outline."""
    entry = _LONG_OP_STORE.get(task_id)
    if not entry:
        return {"error": "task_not_found", "task_id": task_id}

    return {
        "task_id": task_id,
        "status": "approved",
        "final_outline": entry["outline"]
    }
