"""
Agentic MCP Tools - A comprehensive collection of MCP tools for coding agents.
"""

from .base import MCP, ToolResult, ToolRegistry
from .file_tools import (
    read_file,
    write_file,
    delete_file,
    list_directory,
    create_directory,
    delete_directory,
    read_json,
    write_json
)
from .code_analysis import *
from .web_scraping import *
from .system_monitoring import *
from .file_operations import *
from .git_operations import *
from .code_quality import *
from .documentation import *

__version__ = "0.1.0"
__all__ = [
    'MCP',
    'ToolResult',
    'read_file',
    'write_file',
    'delete_file',
    'list_directory',
    'create_directory',
    'delete_directory',
    'read_json',
    'write_json',
    "get_all_tools",
    "get_tool_by_name",
    "get_tools_by_category"
]