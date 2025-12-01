import time
from django.http import JsonResponse

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, JSONParser

from saras_engine_integration.engine_runner import run_rag as engine_run_rag


"""
    RAG endpoint:
    - Accepts query + PDF
    - Reads file bytes
    - Passes everything to engine_runner.run_rag()
    - Returns structured JSON result
"""

@api_view(["POST"])
@parser_classes([MultiPartParser, JSONParser])
def run_rag(request):

    # Validate file
    uploaded_file = request.FILES.get("file")
    if uploaded_file is None:
        return JsonResponse(
            {"status": "error", "message": "Missing file for RAG."},
            status=400
        )

    filename = uploaded_file.name.lower()
    if not (filename.endswith(".pdf") or filename.endswith(".txt")):
        return JsonResponse(
            {"status": "error", "message": "Only PDF or text files allowed."},
            status=400
        )

    # Read query
    query = request.data.get("query", "").strip()
    if not query:
        query = "Summarize this document"

    # Read bytes
    file_bytes = uploaded_file.read()
    if not file_bytes:
        return JsonResponse(
            {"status": "error", "message": "Uploaded file is empty."},
            status=400
        )

    # Run engine
    try:
        result = engine_run_rag(
            query=query,
            file_bytes=file_bytes,
            filename=uploaded_file.name,
            file_url=None   # file_url is no longer used by engine
        )
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)}, status=500
        )

    # Return JSON
    return JsonResponse(result, status=200)
