import time
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser


from saras_engine_integration.engine_runner import run_non_rag as engine_run_non_rag


@api_view(["POST"])
@parser_classes([JSONParser])
def run_non_rag(request):
    
    # Expects JSON: { "query": "<text>" }

    query = request.data.get("query", "")
    if not query:
        return JsonResponse({"status": "error", "message": "Missing query field."}, status=400)

    result = engine_run_non_rag(query=query)

    return JsonResponse(result)
