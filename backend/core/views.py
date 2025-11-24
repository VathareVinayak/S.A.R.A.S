from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser

@api_view(["GET"])
def health_check(request):
    return JsonResponse({
        "status": "ok",
        "service": "S.A.R.A.S Backend Core",
        "message": "Backend is running successfully."
    })


@api_view(["POST"])
@parser_classes([JSONParser, MultiPartParser])
def run_task(request):
    # Extract prompt
    query = request.data.get("query", None)

    # Detect file upload - RAG
    uploaded_file = request.FILES.get("file", None)

    # Routing logic
    if uploaded_file:
        # RAG detected
        return JsonResponse({
            "status": "accepted",
            "mode": "RAG",
            "message": "File received. Forwarding to RAG pipeline.",
            "filename": uploaded_file.name,
            "next_endpoint": "/api/rag/run/",
            "query": query
        })

    else:
        # Non-RAG request
        return JsonResponse({
            "status": "accepted",
            "mode": "Non-RAG",
            "message": "No file found. Will run standard agent pipeline.",
            "next_endpoint": "/api/non-rag/run/",
            "query": query
        })
