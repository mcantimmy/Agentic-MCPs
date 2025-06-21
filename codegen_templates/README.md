# Code Generation Templates

This directory contains Jinja2 templates for generating Python code using the MCP code generation tools.

## Templates

### 1. `class_template.py`
Generates Python classes with attributes and methods.

**Usage Example:**
```python
from mcp_tools.code_generation import generate_class

await generate_class(
    template_name="class_template.py",
    class_name="User",
    attributes=["name", "email", "age"],
    methods=["get_name", "set_email", "validate"],
    output_path="generated_user.py"
)
```

**Generated Output:**
- Python class with specified attributes
- Constructor with all attributes
- Getter/setter methods for attributes starting with "get_" or "set_"
- Placeholder methods for other method names
- String representation methods
- Example usage code

### 2. `api_endpoint.py`
Generates Flask REST API endpoints with specified HTTP methods.

**Usage Example:**
```python
from mcp_tools.code_generation import generate_api_endpoint

await generate_api_endpoint(
    template_name="api_endpoint.py",
    endpoint_name="users",
    methods=["GET", "POST", "PUT", "DELETE"],
    model_name="User",
    output_path="generated_users_api.py"
)
```

**Generated Output:**
- Flask application with specified endpoint
- HTTP method handlers (GET, POST, PUT, DELETE)
- Mock database for demonstration
- Input validation
- Error handling
- Individual item retrieval endpoint
- Error handlers for 404 and 500

### 3. `test_template.py`
Generates unit tests for Python classes.

**Usage Example:**
```python
from mcp_tools.code_generation import generate_test

await generate_test(
    template_name="test_template.py",
    class_name="User",
    test_cases=["test_creation", "test_validation", "test_methods"],
    output_path="test_user.py"
)
```

**Generated Output:**
- Unit test class with specified test cases
- Setup and teardown methods
- Specific test implementations for common test cases
- Integration test class
- Test runner function
- Placeholder tests for custom test cases

## Template Variables

### Class Template Variables
- `class_name`: Name of the class to generate
- `attributes`: List of attribute names
- `methods`: List of method names

### API Endpoint Template Variables
- `endpoint_name`: Name of the API endpoint
- `methods`: List of HTTP methods (GET, POST, PUT, DELETE)
- `model_name`: Name of the data model

### Test Template Variables
- `class_name`: Name of the class to test
- `test_cases`: List of test case method names

## Customization

You can customize these templates by:

1. **Modifying the templates**: Edit the Jinja2 template files to add more functionality
2. **Adding new templates**: Create new `.py` files with Jinja2 syntax
3. **Extending the code generator**: Add new template variables and logic

## Dependencies

The generated code may require these dependencies:
- `flask` (for API endpoints)
- `jinja2` (for template rendering)
- Standard Python libraries (unittest, typing, etc.)

## Usage with MCP Tools

These templates are designed to work with the MCP code generation tools in `mcp_tools/code_generation.py`. The templates use Jinja2 syntax and will be rendered with the provided context variables.

## Example Generated Files

After running the code generation tools, you'll get fully functional Python files that you can:

1. **Import and use** (for classes)
2. **Run as a Flask application** (for API endpoints)
3. **Execute as unit tests** (for test files)

## Notes

- The templates include placeholder code and comments to guide customization
- Error handling and validation are included where appropriate
- Generated files include example usage and documentation
- Templates are designed to be production-ready with minimal modifications 