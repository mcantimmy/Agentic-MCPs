"""
Base classes for MCP tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Callable
from pydantic import BaseModel, Field
from enum import Enum
import inspect
import json


class ToolCategory(str, Enum):
    """Categories for organizing MCP tools."""
    CODE_ANALYSIS = "code_analysis"
    FILE_OPERATIONS = "file_operations"
    WEB_SCRAPING = "web_scraping"
    SYSTEM_MONITORING = "system_monitoring"
    GIT_OPERATIONS = "git_operations"
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"


class ParameterSchema(BaseModel):
    """Schema for tool parameters."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum_values: Optional[List[str]] = None


class ToolSchema(BaseModel):
    """Schema for MCP tool definition."""
    name: str
    description: str
    category: ToolCategory
    parameters: List[ParameterSchema]
    returns: str
    examples: List[Dict[str, Any]] = []
    tags: List[str] = []


class MCPTool(ABC):
    """Base class for all MCP tools."""
    
    def __init__(self):
        self._schema = self._build_schema()
        ToolRegistry.register(self)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @property
    @abstractmethod
    def category(self) -> ToolCategory:
        """Tool category."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    def _build_schema(self) -> ToolSchema:
        """Build the tool schema from the execute method signature."""
        sig = inspect.signature(self.execute)
        parameters = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_type = str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any"
            required = param.default == inspect.Parameter.empty
            default = param.default if param.default != inspect.Parameter.empty else None
            
            parameters.append(ParameterSchema(
                name=param_name,
                type=param_type,
                description=f"Parameter {param_name}",
                required=required,
                default=default
            ))
        
        return ToolSchema(
            name=self.name,
            description=self.description,
            category=self.category,
            parameters=parameters,
            returns=str(sig.return_annotation) if sig.return_annotation != inspect.Parameter.empty else "Any"
        )
    
    @property
    def schema(self) -> ToolSchema:
        """Get the tool schema."""
        return self._schema
    
    def to_mcp_format(self) -> Dict[str, Any]:
        """Convert tool to MCP format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {
                    param.name: {
                        "type": param.type.lower(),
                        "description": param.description,
                        **({"enum": param.enum_values} if param.enum_values else {})
                    }
                    for param in self.schema.parameters
                },
                "required": [param.name for param in self.schema.parameters if param.required]
            }
        }


class ToolRegistry:
    """Registry for managing MCP tools."""
    
    _tools: Dict[str, MCPTool] = {}
    _categories: Dict[ToolCategory, List[MCPTool]] = {}
    
    @classmethod
    def register(cls, tool: MCPTool):
        """Register a tool."""
        cls._tools[tool.name] = tool
        
        if tool.category not in cls._categories:
            cls._categories[tool.category] = []
        cls._categories[tool.category].append(tool)
    
    @classmethod
    def get_tool(cls, name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return cls._tools.get(name)
    
    @classmethod
    def get_all_tools(cls) -> List[MCPTool]:
        """Get all registered tools."""
        return list(cls._tools.values())
    
    @classmethod
    def get_tools_by_category(cls, category: ToolCategory) -> List[MCPTool]:
        """Get tools by category."""
        return cls._categories.get(category, [])
    
    @classmethod
    def get_tool_names(cls) -> List[str]:
        """Get all tool names."""
        return list(cls._tools.keys())
    
    @classmethod
    def get_categories(cls) -> List[ToolCategory]:
        """Get all categories."""
        return list(cls._categories.keys())
    
    @classmethod
    def search_tools(cls, query: str) -> List[MCPTool]:
        """Search tools by name or description."""
        query = query.lower()
        results = []
        
        for tool in cls._tools.values():
            if (query in tool.name.lower() or 
                query in tool.description.lower() or
                any(query in tag.lower() for tag in getattr(tool.schema, 'tags', []))):
                results.append(tool)
        
        return results


def mcp_tool(name: str, description: str, category: ToolCategory, 
             examples: List[Dict[str, Any]] = None, tags: List[str] = None):
    """Decorator for creating MCP tools from functions."""
    
    def decorator(func: Callable):
        class DecoratedTool(MCPTool):
            @property
            def name(self) -> str:
                return name
            
            @property
            def description(self) -> str:
                return description
            
            @property
            def category(self) -> ToolCategory:
                return category
            
            async def execute(self, **kwargs) -> Any:
                if inspect.iscoroutinefunction(func):
                    return await func(**kwargs)
                else:
                    return func(**kwargs)
        
        tool_instance = DecoratedTool()
        if examples:
            tool_instance.schema.examples = examples
        if tags:
            tool_instance.schema.tags = tags
            
        return tool_instance
    
    return decorator 