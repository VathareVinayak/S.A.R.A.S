from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(["GET"])
def get_session_memory(request):
    """
    SESSION MEMORY (mock version)
    Later this will be connected to saras_engine session memory.
    """
    fake_session_memory = [
        {"key": "last_query", "value": "Explain quantum computing"},
        {"key": "last_mode", "value": "Non-RAG"}
    ]

    return JsonResponse({
        "status": "success",
        "memory_type": "session",
        "data": fake_session_memory
    })


@api_view(["GET"])
def get_long_term_memory(request):
    """
    LONG TERM MEMORY (mock version)
    Will be connected to saras_engine/long_term_memory.py.
    """
    fake_long_term_memory = [
        {"topic": "AI Agents", "notes": "User often asks about research tasks"},
        {"topic": "Assignments", "notes": "User works on ML/AI projects"}
    ]

    return JsonResponse({
        "status": "success",
        "memory_type": "long-term",
        "data": fake_long_term_memory
    })
