import time
import json
from pathlib import Path
from django.http import JsonResponse
from rest_framework.decorators import api_view

BASE_DIR = Path(__file__).resolve().parents[1]  
TRACES_DIR = BASE_DIR / "traces"


@api_view(["GET"])
def get_trace(request, task_id):
    """
    Returns the JSON payload saved for the task id by engine_runner.
    
    """
    trace_path = TRACES_DIR / f"{task_id}.json"

    if trace_path.exists():
        try:
            with trace_path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            return JsonResponse(payload)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": "Failed to read trace file.",
                "error": str(e)
            }, status=500)

    # Fallback mock if no trace saved
    mock_trace = [
        {"step": 1, "actor": "ManagerAgent", "action": "Start task (fallback)"},
        {"step": 2, "actor": "ResearchAgent", "action": "Collect info (fallback)"},
        {"step": 3, "actor": "WriterAgent", "action": "Generate answer (fallback)"},
    ]
    return JsonResponse({
        "status": "not_found",
        "task_id": task_id,
        "trace": mock_trace,
        "message": "No saved trace found for this task id."
    }, status=404)
     