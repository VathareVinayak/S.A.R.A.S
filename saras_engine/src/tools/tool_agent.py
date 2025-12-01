import requests
import os
from typing import Any, Dict, Callable

# Important operation: decide default mode using environment variable (MCP usage)
USE_MCP = os.getenv("USE_MCP", "false").lower() in ("1", "true", "yes")
MCP_BASE = os.getenv("MCP_BASE", "http://127.0.0.1:8000")  # default MCP local dev server

def call_local(func: Callable, *args, **kwargs) -> Dict:
    """Important operation: call local python function safely and catch exceptions."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # Important operation: return structured error (don't raise to agent)
        return {"error": str(e)}

def call_mcp(tool_name: str, payload: Dict, timeout: int = 15) -> Dict:
    """Important operation: call MCP server endpoint for the given tool name."""
    url = f"{MCP_BASE}/tools/{tool_name}"
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        return resp.json()
    except Exception as e:
        # Important operation: convert network error into structured dict for agent handling
        return {"error": f"mcp_call_failed: {str(e)}"}

def invoke(tool_name: str, local_func: Callable = None, payload: Dict = None, timeout: int = 15) -> Dict:
    """
    Important operation:
    - If mode is MCP, attempt remote call first and fall back to local_func if available.
    - If mode is local, call function directly.
    """
    payload = payload or {}
    if USE_MCP:
        result = call_mcp(tool_name, payload, timeout=timeout)
        # Important operation: if remote call failed and local function exists, fallback
        if result.get("error") and local_func is not None:
            return call_local(local_func, **payload)
        return result
    else:
        if local_func is None:
            return {"error": "no_local_function_provided"}
        return call_local(local_func, **payload)



class ToolAgent:
    """
    Wrapper class to maintain backward compatibility.
    Provides invoke(), call_local(), call_mcp() as methods.
    Agents expect this class to exist.
    """

    def __init__(self):
        pass

    def invoke(self, tool_name: str, local_func=None, payload=None, timeout: int = 15):
        return invoke(tool_name, local_func=local_func, payload=payload, timeout=timeout)

    def call_local(self, func, *args, **kwargs):
        return call_local(func, *args, **kwargs)

    def call_mcp(self, tool_name: str, payload: dict, timeout: int = 15):
        return call_mcp(tool_name, payload, timeout)
