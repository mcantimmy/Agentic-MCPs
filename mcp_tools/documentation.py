"""
Documentation MCP tools for generating and parsing documentation.
"""

import re
import ast
import markdown
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base import MCPTool, ToolCategory


class DocstringExtractor(MCPTool):
    """Extract and analyze docstrings from Python code."""
    
    @property
    def name(self) -> str:
        return "extract_docstrings"
    
    @property
    def description(self) -> str:
        return "Extract and analyze docstrings from Python code including functions, classes, and modules"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.DOCUMENTATION
    
    async def execute(self, file_path: str) -> Dict[str, Any]:
        """Extract docstrings from Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            result = {
                "file_path": file_path,
                "module_docstring": ast.get_docstring(tree),
                "functions": [],
                "classes": [],
                "coverage": {}
            }
            
            # Extract function docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    docstring = ast.get_docstring(node)
                    result["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "docstring": docstring,
                        "has_docstring": docstring is not None,
                        "args": [arg.arg for arg in node.args.args],
                        "returns": ast.unparse(node.returns) if node.returns else None
                    })
                
                elif isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    methods = []
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_docstring = ast.get_docstring(item)
                            methods.append({
                                "name": item.name,
                                "line": item.lineno,
                                "docstring": method_docstring,
                                "has_docstring": method_docstring is not None
                            })
                    
                    result["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "docstring": docstring,
                        "has_docstring": docstring is not None,
                        "methods": methods
                    })
            
            # Calculate coverage
            total_functions = len(result["functions"])
            documented_functions = sum(1 for f in result["functions"] if f["has_docstring"])
            
            total_classes = len(result["classes"])
            documented_classes = sum(1 for c in result["classes"] if c["has_docstring"])
            
            total_methods = sum(len(c["methods"]) for c in result["classes"])
            documented_methods = sum(
                sum(1 for m in c["methods"] if m["has_docstring"]) 
                for c in result["classes"]
            )
            
            result["coverage"] = {
                "module_documented": result["module_docstring"] is not None,
                "functions": {
                    "total": total_functions,
                    "documented": documented_functions,
                    "percentage": (documented_functions / total_functions * 100) if total_functions > 0 else 0
                },
                "classes": {
                    "total": total_classes,
                    "documented": documented_classes,
                    "percentage": (documented_classes / total_classes * 100) if total_classes > 0 else 0
                },
                "methods": {
                    "total": total_methods,
                    "documented": documented_methods,
                    "percentage": (documented_methods / total_methods * 100) if total_methods > 0 else 0
                }
            }
            
            return result
            
        except Exception as e:
            return {"error": str(e)}


class MarkdownParser(MCPTool):
    """Parse and analyze Markdown documents."""
    
    @property
    def name(self) -> str:
        return "parse_markdown"
    
    @property
    def description(self) -> str:
        return "Parse and analyze Markdown documents including structure, links, and content"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.DOCUMENTATION
    
    async def execute(self, file_path: str) -> Dict[str, Any]:
        """Parse Markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with markdown library
            md = markdown.Markdown(extensions=['toc', 'tables', 'fenced_code'])
            html = md.convert(content)
            
            result = {
                "file_path": file_path,
                "html": html,
                "toc": getattr(md, 'toc', ''),
                "structure": self._analyze_structure(content),
                "links": self._extract_links(content),
                "code_blocks": self._extract_code_blocks(content),
                "statistics": self._calculate_statistics(content)
            }
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze document structure."""
        lines = content.split('\n')
        headings = []
        
        for i, line in enumerate(lines):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                headings.append({
                    "level": level,
                    "title": title,
                    "line": i + 1
                })
        
        return {
            "headings": headings,
            "max_heading_level": max((h["level"] for h in headings), default=0),
            "total_headings": len(headings)
        }
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract links from markdown."""
        # Match [text](url) format
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = []
        
        for match in re.finditer(link_pattern, content):
            links.append({
                "text": match.group(1),
                "url": match.group(2),
                "is_external": match.group(2).startswith(('http://', 'https://'))
            })
        
        return links
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks from markdown."""
        # Match ```language\ncode\n``` format
        code_pattern = r'```(\w+)?\n(.*?)\n```'
        code_blocks = []
        
        for match in re.finditer(code_pattern, content, re.DOTALL):
            code_blocks.append({
                "language": match.group(1) or "text",
                "code": match.group(2)
            })
        
        return code_blocks
    
    def _calculate_statistics(self, content: str) -> Dict[str, int]:
        """Calculate document statistics."""
        lines = content.split('\n')
        words = content.split()
        
        return {
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "total_words": len(words),
            "total_characters": len(content),
            "total_characters_no_spaces": len(content.replace(' ', ''))
        }


class DocumentationGenerator(MCPTool):
    """Generate documentation from code comments and docstrings."""
    
    @property
    def name(self) -> str:
        return "generate_documentation"
    
    @property
    def description(self) -> str:
        return "Generate documentation from Python code including API docs and README content"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.DOCUMENTATION
    
    async def execute(self, 
                     file_path: str,
                     format: str = "markdown",
                     include_private: bool = False) -> Dict[str, Any]:
        """Generate documentation from Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            result = {
                "file_path": file_path,
                "format": format,
                "documentation": ""
            }
            
            if format == "markdown":
                doc_content = self._generate_markdown_docs(tree, file_path, include_private)
            else:
                return {"error": f"Unsupported format: {format}"}
            
            result["documentation"] = doc_content
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_markdown_docs(self, tree: ast.AST, file_path: str, include_private: bool) -> str:
        """Generate Markdown documentation."""
        doc_lines = []
        
        # Module header
        module_name = Path(file_path).stem
        doc_lines.append(f"# {module_name}")
        doc_lines.append("")
        
        # Module docstring
        module_docstring = ast.get_docstring(tree)
        if module_docstring:
            doc_lines.append(module_docstring)
            doc_lines.append("")
        
        # Classes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        if classes:
            doc_lines.append("## Classes")
            doc_lines.append("")
            
            for cls in classes:
                if not include_private and cls.name.startswith('_'):
                    continue
                
                doc_lines.append(f"### {cls.name}")
                doc_lines.append("")
                
                cls_docstring = ast.get_docstring(cls)
                if cls_docstring:
                    doc_lines.append(cls_docstring)
                    doc_lines.append("")
                
                # Methods
                methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
                if methods:
                    doc_lines.append("#### Methods")
                    doc_lines.append("")
                    
                    for method in methods:
                        if not include_private and method.name.startswith('_') and method.name != '__init__':
                            continue
                        
                        # Method signature
                        args = [arg.arg for arg in method.args.args]
                        signature = f"{method.name}({', '.join(args)})"
                        doc_lines.append(f"##### {signature}")
                        doc_lines.append("")
                        
                        method_docstring = ast.get_docstring(method)
                        if method_docstring:
                            doc_lines.append(method_docstring)
                            doc_lines.append("")
        
        # Functions
        functions = [node for node in ast.walk(tree) 
                    if isinstance(node, ast.FunctionDef) and 
                    not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree))]
        
        if functions:
            doc_lines.append("## Functions")
            doc_lines.append("")
            
            for func in functions:
                if not include_private and func.name.startswith('_'):
                    continue
                
                # Function signature
                args = [arg.arg for arg in func.args.args]
                signature = f"{func.name}({', '.join(args)})"
                doc_lines.append(f"### {signature}")
                doc_lines.append("")
                
                func_docstring = ast.get_docstring(func)
                if func_docstring:
                    doc_lines.append(func_docstring)
                    doc_lines.append("")
        
        return '\n'.join(doc_lines)


# Initialize tools
docstring_extractor = DocstringExtractor()
markdown_parser = MarkdownParser()
documentation_generator = DocumentationGenerator() 