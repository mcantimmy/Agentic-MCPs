"""
Code analysis MCP tools for parsing, analyzing, and understanding code structure.
"""

import ast
import os
import re
import json
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import importlib.util

from .base import MCPTool, ToolCategory


class CodeComplexityAnalyzer(MCPTool):
    """Analyze code complexity metrics including cyclomatic complexity."""
    
    @property
    def name(self) -> str:
        return "analyze_code_complexity"
    
    @property
    def description(self) -> str:
        return "Analyze code complexity metrics including cyclomatic complexity, lines of code, and function complexity"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE_ANALYSIS
    
    async def execute(self, file_path: str) -> Dict[str, Any]:
        """Analyze code complexity for a given file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            complexity_visitor = ComplexityVisitor()
            complexity_visitor.visit(tree)
            
            return {
                "file_path": file_path,
                "total_lines": len(content.splitlines()),
                "total_complexity": complexity_visitor.total_complexity,
                "functions": complexity_visitor.functions,
                "classes": complexity_visitor.classes,
                "imports": complexity_visitor.imports,
                "average_complexity": complexity_visitor.average_complexity()
            }
        except Exception as e:
            return {"error": str(e)}


class ASTParser(MCPTool):
    """Parse Python code into Abstract Syntax Tree and extract structure information."""
    
    @property
    def name(self) -> str:
        return "parse_ast"
    
    @property
    def description(self) -> str:
        return "Parse Python code into AST and extract detailed structure information including functions, classes, and variables"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE_ANALYSIS
    
    async def execute(self, file_path: str, include_body: bool = False) -> Dict[str, Any]:
        """Parse file into AST and extract structure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            extractor = StructureExtractor(include_body=include_body)
            extractor.visit(tree)
            
            return {
                "file_path": file_path,
                "functions": extractor.functions,
                "classes": extractor.classes,
                "imports": extractor.imports,
                "variables": extractor.variables,
                "decorators": extractor.decorators,
                "docstrings": extractor.docstrings
            }
        except Exception as e:
            return {"error": str(e)}


class DependencyAnalyzer(MCPTool):
    """Analyze dependencies and imports in Python code."""
    
    @property
    def name(self) -> str:
        return "analyze_dependencies"
    
    @property
    def description(self) -> str:
        return "Analyze dependencies, imports, and module relationships in Python code"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE_ANALYSIS
    
    async def execute(self, file_path: str) -> Dict[str, Any]:
        """Analyze dependencies in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analyzer = DependencyVisitor()
            analyzer.visit(tree)
            
            return {
                "file_path": file_path,
                "standard_library": list(analyzer.stdlib_imports),
                "third_party": list(analyzer.third_party_imports),
                "local_imports": list(analyzer.local_imports),
                "import_details": analyzer.import_details,
                "unused_imports": analyzer.find_unused_imports(content)
            }
        except Exception as e:
            return {"error": str(e)}


class CodePatternDetector(MCPTool):
    """Detect common code patterns, anti-patterns, and design patterns."""
    
    @property
    def name(self) -> str:
        return "detect_code_patterns"
    
    @property
    def description(self) -> str:
        return "Detect design patterns, anti-patterns, and common code patterns in Python code"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE_ANALYSIS
    
    async def execute(self, file_path: str) -> Dict[str, Any]:
        """Detect patterns in code."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            detector = PatternDetector()
            detector.visit(tree)
            
            return {
                "file_path": file_path,
                "design_patterns": detector.design_patterns,
                "anti_patterns": detector.anti_patterns,
                "code_smells": detector.code_smells,
                "suggestions": detector.suggestions
            }
        except Exception as e:
            return {"error": str(e)}


class FunctionAnalyzer(MCPTool):
    """Analyze individual functions for complexity, parameters, and return types."""
    
    @property
    def name(self) -> str:
        return "analyze_function"
    
    @property
    def description(self) -> str:
        return "Analyze individual functions for complexity, parameters, return types, and documentation"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE_ANALYSIS
    
    async def execute(self, file_path: str, function_name: str) -> Dict[str, Any]:
        """Analyze a specific function."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analyzer = FunctionVisitor(function_name)
            analyzer.visit(tree)
            
            if not analyzer.found_function:
                return {"error": f"Function '{function_name}' not found"}
            
            return analyzer.function_info
        except Exception as e:
            return {"error": str(e)}


# Helper classes for AST analysis

class ComplexityVisitor(ast.NodeVisitor):
    """Calculate cyclomatic complexity."""
    
    def __init__(self):
        self.total_complexity = 1  # Base complexity
        self.functions = []
        self.classes = []
        self.imports = []
        self.current_function = None
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        func_complexity = 1
        func_visitor = ComplexityVisitor()
        func_visitor.visit(node)
        
        self.functions.append({
            "name": node.name,
            "line": node.lineno,
            "complexity": func_visitor.total_complexity,
            "args": len(node.args.args),
            "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
        })
        
        self.total_complexity += func_visitor.total_complexity
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.classes.append({
            "name": node.name,
            "line": node.lineno,
            "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
            "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
        })
        self.generic_visit(node)
    
    def visit_If(self, node):
        self.total_complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.total_complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.total_complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.total_complexity += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        self.total_complexity += 1
        self.generic_visit(node)
    
    def average_complexity(self):
        if not self.functions:
            return 0
        return sum(f["complexity"] for f in self.functions) / len(self.functions)


class StructureExtractor(ast.NodeVisitor):
    """Extract code structure information."""
    
    def __init__(self, include_body=False):
        self.include_body = include_body
        self.functions = []
        self.classes = []
        self.imports = []
        self.variables = []
        self.decorators = []
        self.docstrings = []
    
    def visit_FunctionDef(self, node):
        func_info = {
            "name": node.name,
            "line": node.lineno,
            "args": [arg.arg for arg in node.args.args],
            "defaults": len(node.args.defaults),
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "returns": ast.unparse(node.returns) if node.returns else None,
            "docstring": ast.get_docstring(node)
        }
        
        if self.include_body:
            func_info["body"] = ast.unparse(node)
        
        self.functions.append(func_info)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        class_info = {
            "name": node.name,
            "line": node.lineno,
            "bases": [ast.unparse(base) for base in node.bases],
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "methods": [],
            "docstring": ast.get_docstring(node)
        }
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info["methods"].append(item.name)
        
        self.classes.append(class_info)
        self.generic_visit(node)
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({
                "type": "import",
                "module": alias.name,
                "alias": alias.asname,
                "line": node.lineno
            })
    
    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imports.append({
                "type": "from_import",
                "module": node.module,
                "name": alias.name,
                "alias": alias.asname,
                "line": node.lineno
            })
    
    def _get_decorator_name(self, decorator):
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            return ast.unparse(decorator)
        else:
            return ast.unparse(decorator)


class DependencyVisitor(ast.NodeVisitor):
    """Analyze dependencies and imports."""
    
    def __init__(self):
        self.stdlib_imports = set()
        self.third_party_imports = set()
        self.local_imports = set()
        self.import_details = []
        self.all_names = set()
    
    def visit_Import(self, node):
        for alias in node.names:
            module_name = alias.name.split('.')[0]
            self._categorize_import(module_name)
            self.import_details.append({
                "type": "import",
                "module": alias.name,
                "alias": alias.asname,
                "line": node.lineno
            })
            if alias.asname:
                self.all_names.add(alias.asname)
            else:
                self.all_names.add(alias.name)
    
    def visit_ImportFrom(self, node):
        if node.module:
            module_name = node.module.split('.')[0]
            self._categorize_import(module_name)
        
        for alias in node.names:
            self.import_details.append({
                "type": "from_import",
                "module": node.module,
                "name": alias.name,
                "alias": alias.asname,
                "line": node.lineno
            })
            if alias.asname:
                self.all_names.add(alias.asname)
            else:
                self.all_names.add(alias.name)
    
    def _categorize_import(self, module_name):
        # Simple categorization - could be enhanced with more sophisticated logic
        stdlib_modules = {
            'os', 'sys', 'json', 'ast', 're', 'pathlib', 'typing', 'collections',
            'itertools', 'functools', 'datetime', 'time', 'math', 'random',
            'urllib', 'http', 'email', 'html', 'xml', 'csv', 'sqlite3'
        }
        
        if module_name in stdlib_modules:
            self.stdlib_imports.add(module_name)
        elif module_name.startswith('.'):
            self.local_imports.add(module_name)
        else:
            self.third_party_imports.add(module_name)
    
    def find_unused_imports(self, content):
        # Simple unused import detection
        used_names = set()
        for line in content.split('\n'):
            for name in self.all_names:
                if name in line and not line.strip().startswith(('import ', 'from ')):
                    used_names.add(name)
        
        return list(self.all_names - used_names)


class PatternDetector(ast.NodeVisitor):
    """Detect design patterns and anti-patterns."""
    
    def __init__(self):
        self.design_patterns = []
        self.anti_patterns = []
        self.code_smells = []
        self.suggestions = []
        self.class_methods = {}
    
    def visit_ClassDef(self, node):
        # Detect Singleton pattern
        if self._is_singleton(node):
            self.design_patterns.append({
                "pattern": "Singleton",
                "class": node.name,
                "line": node.lineno
            })
        
        # Detect Factory pattern
        if self._is_factory(node):
            self.design_patterns.append({
                "pattern": "Factory",
                "class": node.name,
                "line": node.lineno
            })
        
        # Detect God Class anti-pattern
        if len(node.body) > 20:  # Arbitrary threshold
            self.anti_patterns.append({
                "pattern": "God Class",
                "class": node.name,
                "line": node.lineno,
                "reason": f"Class has {len(node.body)} members"
            })
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        # Detect long functions
        if len(node.body) > 15:  # Arbitrary threshold
            self.code_smells.append({
                "smell": "Long Function",
                "function": node.name,
                "line": node.lineno,
                "reason": f"Function has {len(node.body)} statements"
            })
        
        # Detect too many parameters
        if len(node.args.args) > 5:
            self.code_smells.append({
                "smell": "Too Many Parameters",
                "function": node.name,
                "line": node.lineno,
                "reason": f"Function has {len(node.args.args)} parameters"
            })
        
        self.generic_visit(node)
    
    def _is_singleton(self, node):
        # Simple singleton detection
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__new__':
                return True
        return False
    
    def _is_factory(self, node):
        # Simple factory detection
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and 'create' in item.name.lower():
                return True
        return False


class FunctionVisitor(ast.NodeVisitor):
    """Analyze a specific function."""
    
    def __init__(self, function_name):
        self.function_name = function_name
        self.found_function = False
        self.function_info = {}
    
    def visit_FunctionDef(self, node):
        if node.name == self.function_name:
            self.found_function = True
            
            complexity_visitor = ComplexityVisitor()
            complexity_visitor.visit(node)
            
            self.function_info = {
                "name": node.name,
                "line": node.lineno,
                "complexity": complexity_visitor.total_complexity,
                "args": [arg.arg for arg in node.args.args],
                "defaults": len(node.args.defaults),
                "decorators": [ast.unparse(d) for d in node.decorator_list],
                "returns": ast.unparse(node.returns) if node.returns else None,
                "docstring": ast.get_docstring(node),
                "body_lines": len(node.body),
                "local_variables": self._extract_variables(node)
            }
        
        self.generic_visit(node)
    
    def _extract_variables(self, node):
        variables = []
        for item in ast.walk(node):
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
        return list(set(variables))


# Initialize tools
code_complexity_analyzer = CodeComplexityAnalyzer()
ast_parser = ASTParser()
dependency_analyzer = DependencyAnalyzer()
code_pattern_detector = CodePatternDetector()
function_analyzer = FunctionAnalyzer() 