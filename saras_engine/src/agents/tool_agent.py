import os
import requests
from typing import Any, Dict, Callable, Optional

# Important operation: choose mode (MCP vs local) via environment variable for dev/prod flexibility
USE_MCP = os.getenv("USE_MCP", "false").lower() in ("1", "true", "yes")
MCP_BASE = os.getenv("MCP_BASE", "http://127.0.0.1:9000")  # change if your MCP server runs elsewhere
DEFAULT_TIMEOUT = int(os.getenv("TOOL_TIMEOUT", "15"))


def call_local(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Important operation: call a local function and return a structured result (never raise)."""
    try:
        result = func(*args, **kwargs)
        # If the function returns a list/string/etc, normalize to a dict for consistency.
        if isinstance(result, dict):
            return result
        return {"result": result}
    except Exception as e:
        # Important: return structured error for agent to consume
        return {"error": f"local_call_failed: {str(e)}"}


def call_mcp(tool_name: str, payload: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """Important operation: call remote MCP endpoint and return JSON or structured error."""
    url = f"{MCP_BASE.rstrip('/')}/tools/{tool_name}"
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        # Try to parse JSON safely
        try:
            return resp.json()
        except Exception:
            return {"error": "mcp_response_not_json", "raw": resp.text}
    except Exception as e:
        return {"error": f"mcp_call_failed: {str(e)}"}


def invoke(tool_name: str, local_func: Optional[Callable] = None, payload: Optional[Dict[str, Any]] = None, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Unified entrypoint: attempt MCP remote call if USE_MCP is true, otherwise call localfunc.
    Important behavior:
    - If MCP call fails but local_func provided, fallback to local_func.
    - If neither is available, return structured error.
    """
    payload = payload or {}

    if USE_MCP:
        # Try remote first
        result = call_mcp(tool_name, payload, timeout=timeout)
        # If remote failed and local exists, fallback
        if isinstance(result, dict) and result.get("error") and local_func is not None:
            return call_local(local_func, **payload)
        return result
    else:
        # Local-first mode
        if local_func is None:
            return {"error": "no_local_function_provided", "tool_name": tool_name}
        return call_local(local_func, **payload)


  
# Compatibility wrapper: many parts of engine expect a ToolAgent class.
# Provide a simple class that delegates to the functions above.
  
class ToolAgent:
    """Compatibility wrapper exposing methods agents expect."""

    def __init__(self):
        # Important operation: no heavy initialization here
        pass

    def invoke(self, tool_name: str, local_func: Optional[Callable] = None, payload: Optional[Dict[str, Any]] = None, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Call a tool (MCP or local)."""
        return invoke(tool_name=tool_name, local_func=local_func, payload=payload, timeout=timeout)

    def call_local(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Direct local call wrapper."""
        return call_local(func, *args, **kwargs)

    def call_mcp(self, tool_name: str, payload: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Direct MCP call wrapper."""
        return call_mcp(tool_name, payload, timeout=timeout)
