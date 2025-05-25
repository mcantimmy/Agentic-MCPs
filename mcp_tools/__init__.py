"""
Agentic MCP Tools - A comprehensive collection of MCP tools for coding agents.
"""

from .base import MCPTool, ToolRegistry
from .code_analysis import *
from .file_operations import *
from .web_scraping import *
from .system_monitoring import *
from .git_operations import *
from .code_quality import *
from .documentation import *

__version__ = "1.0.0"
__all__ = [
    "MCPTool",
    "ToolRegistry",
    "get_all_tools",
    "get_tool_by_name",
    "get_tools_by_category"
]

def get_all_tools():
    """Get all registered MCP tools."""
    return ToolRegistry.get_all_tools()

def get_tool_by_name(name: str):
    """Get a specific tool by name."""
    return ToolRegistry.get_tool(name)

def get_tools_by_category(category: str):
    """Get all tools in a specific category."""
    return ToolRegistry.get_tools_by_category(category) 