"""
Code quality MCP tools for linting, formatting, and testing.
"""

import subprocess
import os
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base import MCPTool, ToolCategory


class CodeFormatter(MCPTool):
    """Format code using various formatters like Black, isort, etc."""
    
    @property
    def name(self) -> str:
        return "format_code"
    
    @property
    def description(self) -> str:
        return "Format Python code using Black and isort formatters"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE_QUALITY
    
    async def execute(self, 
                     file_path: str,
                     formatter: str = "black",
                     dry_run: bool = True,
                     line_length: int = 88) -> Dict[str, Any]:
        """Format code file."""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File '{file_path}' does not exist"}
            
            result = {
                "file_path": file_path,
                "formatter": formatter,
                "dry_run": dry_run,
                "changes_made": False
            }
            
            if formatter == "black":
                cmd = ["black", "--line-length", str(line_length)]
                if dry_run:
                    cmd.append("--diff")
                else:
                    cmd.append("--quiet")
                cmd.append(file_path)
                
                process = subprocess.run(cmd, capture_output=True, text=True)
                result["return_code"] = process.returncode
                result["stdout"] = process.stdout
                result["stderr"] = process.stderr
                
                if dry_run and process.stdout:
                    result["changes_made"] = True
                    result["diff"] = process.stdout
                elif not dry_run and process.returncode == 0:
                    result["changes_made"] = True
                    result["message"] = "File formatted successfully"
            
            elif formatter == "isort":
                cmd = ["isort"]
                if dry_run:
                    cmd.append("--diff")
                cmd.append(file_path)
                
                process = subprocess.run(cmd, capture_output=True, text=True)
                result["return_code"] = process.returncode
                result["stdout"] = process.stdout
                result["stderr"] = process.stderr
                
                if dry_run and process.stdout:
                    result["changes_made"] = True
                    result["diff"] = process.stdout
                elif not dry_run and process.returncode == 0:
                    result["changes_made"] = True
                    result["message"] = "Imports sorted successfully"
            
            else:
                return {"error": f"Unsupported formatter: {formatter}"}
            
            return result
            
        except FileNotFoundError:
            return {"error": f"Formatter '{formatter}' not found. Please install it first."}
        except Exception as e:
            return {"error": str(e)}


class CodeLinter(MCPTool):
    """Lint code using various linters like flake8, mypy, etc."""
    
    @property
    def name(self) -> str:
        return "lint_code"
    
    @property
    def description(self) -> str:
        return "Lint Python code using flake8, mypy, or other linters to find issues"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE_QUALITY
    
    async def execute(self, 
                     file_path: str,
                     linter: str = "flake8",
                     max_line_length: int = 88) -> Dict[str, Any]:
        """Lint code file."""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File '{file_path}' does not exist"}
            
            result = {
                "file_path": file_path,
                "linter": linter,
                "issues": []
            }
            
            if linter == "flake8":
                cmd = ["flake8", "--max-line-length", str(max_line_length), file_path]
                
                process = subprocess.run(cmd, capture_output=True, text=True)
                result["return_code"] = process.returncode
                
                if process.stdout:
                    for line in process.stdout.strip().split('\n'):
                        if line:
                            parts = line.split(':', 3)
                            if len(parts) >= 4:
                                result["issues"].append({
                                    "file": parts[0],
                                    "line": int(parts[1]),
                                    "column": int(parts[2]),
                                    "message": parts[3].strip()
                                })
            
            elif linter == "mypy":
                cmd = ["mypy", file_path]
                
                process = subprocess.run(cmd, capture_output=True, text=True)
                result["return_code"] = process.returncode
                
                if process.stdout:
                    for line in process.stdout.strip().split('\n'):
                        if line and ':' in line:
                            parts = line.split(':', 2)
                            if len(parts) >= 3:
                                try:
                                    line_num = int(parts[1])
                                    result["issues"].append({
                                        "file": parts[0],
                                        "line": line_num,
                                        "message": parts[2].strip()
                                    })
                                except ValueError:
                                    result["issues"].append({
                                        "file": file_path,
                                        "message": line
                                    })
            
            else:
                return {"error": f"Unsupported linter: {linter}"}
            
            result["total_issues"] = len(result["issues"])
            result["has_issues"] = len(result["issues"]) > 0
            
            return result
            
        except FileNotFoundError:
            return {"error": f"Linter '{linter}' not found. Please install it first."}
        except Exception as e:
            return {"error": str(e)}


class TestRunner(MCPTool):
    """Run tests using pytest or unittest."""
    
    @property
    def name(self) -> str:
        return "run_tests"
    
    @property
    def description(self) -> str:
        return "Run tests using pytest or unittest and return results"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE_QUALITY
    
    async def execute(self, 
                     test_path: str,
                     test_runner: str = "pytest",
                     verbose: bool = True) -> Dict[str, Any]:
        """Run tests."""
        try:
            if not os.path.exists(test_path):
                return {"error": f"Test path '{test_path}' does not exist"}
            
            result = {
                "test_path": test_path,
                "test_runner": test_runner
            }
            
            if test_runner == "pytest":
                cmd = ["pytest", test_path, "--tb=short"]
                if verbose:
                    cmd.append("-v")
                
                process = subprocess.run(cmd, capture_output=True, text=True)
                result["return_code"] = process.returncode
                result["stdout"] = process.stdout
                result["stderr"] = process.stderr
                
                # Parse pytest output
                output_lines = process.stdout.split('\n')
                for line in output_lines:
                    if "failed" in line and "passed" in line:
                        result["summary"] = line.strip()
                        break
            
            elif test_runner == "unittest":
                cmd = ["python", "-m", "unittest", "discover", "-s", test_path]
                if verbose:
                    cmd.append("-v")
                
                process = subprocess.run(cmd, capture_output=True, text=True)
                result["return_code"] = process.returncode
                result["stdout"] = process.stdout
                result["stderr"] = process.stderr
            
            else:
                return {"error": f"Unsupported test runner: {test_runner}"}
            
            result["success"] = process.returncode == 0
            
            return result
            
        except FileNotFoundError:
            return {"error": f"Test runner '{test_runner}' not found. Please install it first."}
        except Exception as e:
            return {"error": str(e)}


# Initialize tools
code_formatter = CodeFormatter()
code_linter = CodeLinter()
test_runner = TestRunner() 