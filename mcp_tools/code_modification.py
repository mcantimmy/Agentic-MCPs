"""
Code modification tools for MCP.
"""

from typing import Dict, List, Optional, Any
from .base import MCPTool, ToolCategory, mcp_tool
import ast
import autopep8
import black
import isort
import re

class CodeModifier:
    """Base class for code modification tools."""
    
    @staticmethod
    def parse_code(code: str) -> ast.Module:
        """Parse Python code into an AST."""
        return ast.parse(code)
    
    @staticmethod
    def unparse_code(tree: ast.Module) -> str:
        """Convert AST back to Python code."""
        return ast.unparse(tree)

@mcp_tool(
    name="format_code",
    description="Format Python code using black and isort",
    category=ToolCategory.CODE_MODIFICATION,
    examples=[
        {
            "file_path": "example.py",
            "line_length": 88,
            "use_black": True,
            "use_isort": True
        }
    ]
)
async def format_code(
    file_path: str,
    line_length: int = 88,
    use_black: bool = True,
    use_isort: bool = True
) -> str:
    """Format Python code using black and isort."""
    with open(file_path, 'r') as f:
        code = f.read()
    
    if use_isort:
        code = isort.code(code, line_length=line_length)
    
    if use_black:
        code = black.format_str(code, line_length=line_length)
    
    with open(file_path, 'w') as f:
        f.write(code)
    
    return f"Formatted code in {file_path}"

@mcp_tool(
    name="refactor_imports",
    description="Refactor and organize imports in Python code",
    category=ToolCategory.CODE_MODIFICATION,
    examples=[
        {
            "file_path": "example.py",
            "group_by_package": True,
            "sort_imports": True
        }
    ]
)
async def refactor_imports(
    file_path: str,
    group_by_package: bool = True,
    sort_imports: bool = True
) -> str:
    """Refactor and organize imports in Python code."""
    with open(file_path, 'r') as f:
        code = f.read()
    
    # Parse the code
    tree = CodeModifier.parse_code(code)
    
    # Group imports by package
    if group_by_package:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(f"import {name.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for name in node.names:
                    imports.append(f"from {module} import {name.name}")
        
        # Sort imports
        if sort_imports:
            imports.sort()
        
        # Reconstruct the code with organized imports
        new_code = '\n'.join(imports) + '\n\n'
        new_code += CodeModifier.unparse_code(tree)
        
        with open(file_path, 'w') as f:
            f.write(new_code)
    
    return f"Refactored imports in {file_path}"

@mcp_tool(
    name="rename_variable",
    description="Rename a variable throughout a Python file",
    category=ToolCategory.CODE_MODIFICATION,
    examples=[
        {
            "file_path": "example.py",
            "old_name": "old_var",
            "new_name": "new_var"
        }
    ]
)
async def rename_variable(
    file_path: str,
    old_name: str,
    new_name: str
) -> str:
    """Rename a variable throughout a Python file."""
    with open(file_path, 'r') as f:
        code = f.read()
    
    # Parse the code
    tree = CodeModifier.parse_code(code)
    
    # Create a visitor to rename variables
    class RenameVisitor(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == old_name:
                return ast.Name(id=new_name, ctx=node.ctx)
            return node
    
    # Apply the transformation
    new_tree = RenameVisitor().visit(tree)
    new_code = CodeModifier.unparse_code(new_tree)
    
    with open(file_path, 'w') as f:
        f.write(new_code)
    
    return f"Renamed variable {old_name} to {new_name} in {file_path}"

@mcp_tool(
    name="extract_method",
    description="Extract a code block into a new method",
    category=ToolCategory.CODE_MODIFICATION,
    examples=[
        {
            "file_path": "example.py",
            "start_line": 10,
            "end_line": 20,
            "new_method_name": "process_data"
        }
    ]
)
async def extract_method(
    file_path: str,
    start_line: int,
    end_line: int,
    new_method_name: str
) -> str:
    """Extract a code block into a new method."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Extract the code block
    code_block = ''.join(lines[start_line-1:end_line])
    
    # Create the new method
    new_method = f"\n    def {new_method_name}(self):\n"
    new_method += ''.join('    ' + line for line in code_block.splitlines(True))
    new_method += "        pass\n"
    
    # Insert the new method
    lines.insert(end_line, new_method)
    
    # Replace the original code block with a method call
    lines[start_line-1:end_line] = [f"        self.{new_method_name}()\n"]
    
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    return f"Extracted code block into method {new_method_name} in {file_path}" 