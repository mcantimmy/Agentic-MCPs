"""
Debugging and testing tools for MCP.
"""

from typing import Dict, List, Optional, Any, Callable
from .base import MCPTool, ToolCategory, mcp_tool
import sys
import traceback
import logging
import unittest
import coverage
import time
import inspect

class Debugger:
    """Base class for debugging tools."""
    
    def __init__(self):
        self.logger = logging.getLogger('mcp_debugger')
        self.logger.setLevel(logging.DEBUG)
        
        # Add console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

@mcp_tool(
    name="debug_function",
    description="Debug a function with detailed logging",
    category=ToolCategory.CODE_ANALYSIS,
    examples=[
        {
            "function_name": "process_data",
            "args": [1, 2, 3],
            "kwargs": {"key": "value"}
        }
    ]
)
async def debug_function(
    function_name: str,
    args: List[Any],
    kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """Debug a function with detailed logging."""
    debugger = Debugger()
    result = {
        "success": False,
        "output": None,
        "error": None,
        "traceback": None,
        "execution_time": 0
    }
    
    try:
        # Get the function object
        frame = inspect.currentframe()
        while frame:
            if function_name in frame.f_locals:
                func = frame.f_locals[function_name]
                break
            frame = frame.f_back
        else:
            raise NameError(f"Function {function_name} not found")
        
        # Execute the function with timing
        start_time = time.time()
        output = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        result.update({
            "success": True,
            "output": output,
            "execution_time": execution_time
        })
        
        debugger.logger.info(f"Function {function_name} executed successfully")
        debugger.logger.debug(f"Arguments: {args}, {kwargs}")
        debugger.logger.debug(f"Output: {output}")
        debugger.logger.debug(f"Execution time: {execution_time:.2f}s")
        
    except Exception as e:
        result.update({
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        
        debugger.logger.error(f"Error in function {function_name}: {str(e)}")
        debugger.logger.debug(f"Traceback: {traceback.format_exc()}")
    
    return result

@mcp_tool(
    name="run_tests",
    description="Run unit tests for a Python module",
    category=ToolCategory.CODE_ANALYSIS,
    examples=[
        {
            "test_file": "test_example.py",
            "coverage": True
        }
    ]
)
async def run_tests(
    test_file: str,
    coverage: bool = True
) -> Dict[str, Any]:
    """Run unit tests for a Python module."""
    result = {
        "success": False,
        "tests_run": 0,
        "failures": [],
        "errors": [],
        "coverage": None
    }
    
    # Set up coverage if requested
    if coverage:
        cov = coverage.Coverage()
        cov.start()
    
    try:
        # Load and run tests
        loader = unittest.TestLoader()
        suite = loader.discover('.', pattern=test_file)
        runner = unittest.TextTestRunner(verbosity=2)
        test_result = runner.run(suite)
        
        result.update({
            "success": test_result.wasSuccessful(),
            "tests_run": test_result.testsRun,
            "failures": [str(f[0]) for f in test_result.failures],
            "errors": [str(e[0]) for e in test_result.errors]
        })
        
        # Get coverage if requested
        if coverage:
            cov.stop()
            cov.save()
            result["coverage"] = {
                "statements": cov.report(),
                "missing": cov.get_missing()
            }
    
    except Exception as e:
        result["errors"].append(str(e))
    
    return result

@mcp_tool(
    name="profile_function",
    description="Profile a function's performance",
    category=ToolCategory.CODE_ANALYSIS,
    examples=[
        {
            "function_name": "process_data",
            "args": [1, 2, 3],
            "kwargs": {"key": "value"},
            "iterations": 1000
        }
    ]
)
async def profile_function(
    function_name: str,
    args: List[Any],
    kwargs: Dict[str, Any],
    iterations: int = 1000
) -> Dict[str, Any]:
    """Profile a function's performance."""
    result = {
        "success": False,
        "execution_times": [],
        "average_time": 0,
        "min_time": 0,
        "max_time": 0
    }
    
    try:
        # Get the function object
        frame = inspect.currentframe()
        while frame:
            if function_name in frame.f_locals:
                func = frame.f_locals[function_name]
                break
            frame = frame.f_back
        else:
            raise NameError(f"Function {function_name} not found")
        
        # Run the function multiple times
        execution_times = []
        for _ in range(iterations):
            start_time = time.time()
            func(*args, **kwargs)
            execution_time = time.time() - start_time
            execution_times.append(execution_time)
        
        result.update({
            "success": True,
            "execution_times": execution_times,
            "average_time": sum(execution_times) / len(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times)
        })
    
    except Exception as e:
        result["error"] = str(e)
    
    return result 