from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from saras_engine.src.mcp import handlers
from saras_engine.src.tools.tool_registry import list_tools, get_tool
from typing import Dict

app = FastAPI()

@app.get("/health")
async def health():
    # Important operation: health endpoint used by orchestrator / Cloud Run readiness checks
    return {"status": "ok"}

@app.get("/tools")
async def tools_list():
    # Important operation: list available tools and metadata for discovery
    return {"tools": list_tools()}

@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    # Important operation: dynamic routing to appropriate handlers
    payload: Dict = await request.json()
    tool = get_tool(tool_name)
    if not tool:
        return JSONResponse(status_code=404, content={"error": "tool_not_found", "tool": tool_name})
    # route to handler
    if tool_name == "google_search":
        return handlers.handle_google_search(payload)
    elif tool_name == "extract_keywords":
        return handlers.handle_extract_keywords(payload)
    elif tool_name == "outline_generator":
        return handlers.handle_outline_start(payload)
    else:
        return JSONResponse(status_code=400, content={"error": "unsupported_tool", "tool": tool_name})

@app.post("/longops/{task_id}/approve")
async def approve(task_id: str):
    # Important operation: expose an endpoint which operator can call to approve long ops
    result = None
    try:
        result = handlers.outline_generator.approve_outline(task_id)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    return result

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Important operation: start uvicorn server for local development."""
    uvicorn.run(app, host=host, port=port)
