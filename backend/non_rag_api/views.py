import time
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser


from saras_engine_integration.engine_runner import run_non_rag as engine_run_non_rag


@api_view(["POST"])
@parser_classes([JSONParser])
def run_non_rag(request):

    start = time.time()

    # Validate JSON body
    query = request.data.get("query")
    if not query or not isinstance(query, str):
        return JsonResponse({
            "status": "error",
            "message": "Invalid or missing 'query'. Expected JSON: { 'query': '<text>' }"
        }, status=400)

    # Call engine
    result = engine_run_non_rag(query=query)

    # Add server timing
    result["server_time_ms"] = round((time.time() - start) * 1000, 2)

    return JsonResponse(result)
