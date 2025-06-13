"""
Code generation tools for MCP.
"""

from typing import Dict, List, Optional, Any
from .base import MCPTool, ToolCategory, mcp_tool
import jinja2
import os
import json

class CodeGenerator:
    """Base class for code generation tools."""
    
    def __init__(self):
        self.template_loader = jinja2.FileSystemLoader(searchpath="./templates")
        self.template_env = jinja2.Environment(loader=self.template_loader)
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context."""
        template = self.template_env.get_template(template_name)
        return template.render(**context)

@mcp_tool(
    name="generate_class",
    description="Generate a Python class from a template",
    category=ToolCategory.CODE_ANALYSIS,
    examples=[
        {
            "template_name": "class_template.py",
            "class_name": "User",
            "attributes": ["name", "email", "age"],
            "methods": ["get_name", "set_email"]
        }
    ]
)
async def generate_class(
    template_name: str,
    class_name: str,
    attributes: List[str],
    methods: List[str],
    output_path: str
) -> str:
    """Generate a Python class from a template."""
    generator = CodeGenerator()
    context = {
        "class_name": class_name,
        "attributes": attributes,
        "methods": methods
    }
    code = generator.render_template(template_name, context)
    
    with open(output_path, 'w') as f:
        f.write(code)
    
    return f"Generated class {class_name} at {output_path}"

@mcp_tool(
    name="generate_api_endpoint",
    description="Generate a REST API endpoint from a template",
    category=ToolCategory.CODE_ANALYSIS,
    examples=[
        {
            "template_name": "api_endpoint.py",
            "endpoint_name": "users",
            "methods": ["GET", "POST"],
            "model_name": "User"
        }
    ]
)
async def generate_api_endpoint(
    template_name: str,
    endpoint_name: str,
    methods: List[str],
    model_name: str,
    output_path: str
) -> str:
    """Generate a REST API endpoint from a template."""
    generator = CodeGenerator()
    context = {
        "endpoint_name": endpoint_name,
        "methods": methods,
        "model_name": model_name
    }
    code = generator.render_template(template_name, context)
    
    with open(output_path, 'w') as f:
        f.write(code)
    
    return f"Generated API endpoint {endpoint_name} at {output_path}"

@mcp_tool(
    name="generate_test",
    description="Generate unit tests from a template",
    category=ToolCategory.CODE_ANALYSIS,
    examples=[
        {
            "template_name": "test_template.py",
            "class_name": "User",
            "test_cases": ["test_creation", "test_validation"]
        }
    ]
)
async def generate_test(
    template_name: str,
    class_name: str,
    test_cases: List[str],
    output_path: str
) -> str:
    """Generate unit tests from a template."""
    generator = CodeGenerator()
    context = {
        "class_name": class_name,
        "test_cases": test_cases
    }
    code = generator.render_template(template_name, context)
    
    with open(output_path, 'w') as f:
        f.write(code)
    
    return f"Generated tests for {class_name} at {output_path}" 