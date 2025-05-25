"""
FastAPI application for the MCP Tools interactive interface.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
import sys
import os

# Add parent directory to path to import mcp_tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tools import get_all_tools, get_tool_by_name, get_tools_by_category
from mcp_tools.base import ToolCategory, ToolRegistry

app = FastAPI(title="MCP Tools Interface", description="Interactive interface for MCP tools")

# Setup templates and static files
templates = Jinja2Templates(directory="interface/templates")
app.mount("/static", StaticFiles(directory="interface/static"), name="static")


class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with tool browser."""
    tools = get_all_tools()
    categories = {}
    
    for tool in tools:
        category = tool.category.value
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "name": tool.name,
            "description": tool.description,
            "schema": tool.schema.dict()
        })
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "categories": categories,
        "total_tools": len(tools)
    })


@app.get("/api/tools")
async def get_tools():
    """Get all available tools."""
    tools = get_all_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "schema": tool.schema.dict(),
                "mcp_format": tool.to_mcp_format()
            }
            for tool in tools
        ]
    }


@app.get("/api/tools/{tool_name}")
async def get_tool_details(tool_name: str):
    """Get details for a specific tool."""
    tool = get_tool_by_name(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return {
        "name": tool.name,
        "description": tool.description,
        "category": tool.category.value,
        "schema": tool.schema.dict(),
        "mcp_format": tool.to_mcp_format()
    }


@app.get("/api/categories")
async def get_categories():
    """Get all tool categories."""
    categories = {}
    tools = get_all_tools()
    
    for tool in tools:
        category = tool.category.value
        if category not in categories:
            categories[category] = {
                "name": category,
                "tools": [],
                "count": 0
            }
        categories[category]["tools"].append({
            "name": tool.name,
            "description": tool.description
        })
        categories[category]["count"] += 1
    
    return {"categories": list(categories.values())}


@app.get("/api/categories/{category_name}")
async def get_tools_by_category_api(category_name: str):
    """Get tools in a specific category."""
    try:
        category = ToolCategory(category_name)
        tools = get_tools_by_category(category)
        
        return {
            "category": category_name,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "schema": tool.schema.dict()
                }
                for tool in tools
            ]
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Category not found")


@app.post("/api/tools/{tool_name}/execute")
async def execute_tool(tool_name: str, request: ToolExecutionRequest):
    """Execute a tool with given parameters."""
    tool = get_tool_by_name(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    try:
        result = await tool.execute(**request.parameters)
        return {
            "tool_name": tool_name,
            "parameters": request.parameters,
            "result": result,
            "success": "error" not in result
        }
    except Exception as e:
        return {
            "tool_name": tool_name,
            "parameters": request.parameters,
            "result": {"error": str(e)},
            "success": False
        }


@app.get("/api/search")
async def search_tools(q: str):
    """Search tools by name or description."""
    tools = ToolRegistry.search_tools(q)
    
    return {
        "query": q,
        "results": [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "relevance_score": 1.0  # Simple relevance for now
            }
            for tool in tools
        ]
    }


@app.get("/tool/{tool_name}", response_class=HTMLResponse)
async def tool_detail_page(request: Request, tool_name: str):
    """Tool detail page."""
    tool = get_tool_by_name(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return templates.TemplateResponse("tool_detail.html", {
        "request": request,
        "tool": {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category.value,
            "schema": tool.schema.dict(),
            "mcp_format": tool.to_mcp_format()
        }
    })


@app.get("/category/{category_name}", response_class=HTMLResponse)
async def category_page(request: Request, category_name: str):
    """Category page showing all tools in a category."""
    try:
        category = ToolCategory(category_name)
        tools = get_tools_by_category(category)
        
        return templates.TemplateResponse("category.html", {
            "request": request,
            "category_name": category_name,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "schema": tool.schema.dict()
                }
                for tool in tools
            ]
        })
    except ValueError:
        raise HTTPException(status_code=404, detail="Category not found")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "total_tools": len(get_all_tools()),
        "categories": len(ToolCategory)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 