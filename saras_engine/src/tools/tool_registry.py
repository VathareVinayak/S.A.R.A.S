from typing import Dict

# Important operation: central dictionary of tools (name -> metadata)
TOOL_REGISTRY: Dict[str, Dict] = {
    "google_search": {
        "name": "google_search",
        "description": "Searches web and returns ranked results (mock or real).",
        "long_running": False
    },
    "extract_keywords": {
        "name": "extract_keywords",
        "description": "Extracts keywords from provided text.",
        "long_running": False
    },
    "outline_generator": {
        "name": "outline_generator",
        "description": "Generates an outline for a topic. Can simulate long-running approval flow.",
        "long_running": True
    }
}

def list_tools():
    """Important operation: return available tools metadata for discovery."""
    return list(TOOL_REGISTRY.values())

def get_tool(name: str):
    """Important operation: fetch metadata for a given tool name."""
    return TOOL_REGISTRY.get(name)
