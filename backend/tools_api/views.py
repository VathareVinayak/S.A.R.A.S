from django.http import JsonResponse
from rest_framework.decorators import api_view


@api_view(["GET"])
def list_tools(request):
    mock_tools = [
        {
            "name": "google_search",
            "description": "Performs online search and returns results.",
            "long_running": False,
            "used_by": ["ResearchAgent"]
        },
        {
            "name": "extract_keywords",
            "description": "Extracts keywords from user query.",
            "long_running": False,
            "used_by": ["ResearchAgent"]
        },
        {
            "name": "outline_generator",
            "description": "Long-running operation for generating structured outlines.",
            "long_running": True,
            "used_by": ["WriterAgent"]
        },
        {
            "name": "pdf_extractor",
            "description": "Extracts text from uploaded PDF files.",
            "long_running": False,
            "used_by": ["ResearchAgent"]
        }
    ]

    return JsonResponse({
        "status": "success",
        "tool_count": len(mock_tools),
        "tools": mock_tools
    })
