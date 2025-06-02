from base import MCP
from file_tools import (
    read_file,
    write_file,
    list_directory,
    create_directory,
    read_json,
    write_json
)

def main():
    # Create an MCP instance
    mcp = MCP()
    
    # Register file system tools
    mcp.register_tool("read_file", read_file)
    mcp.register_tool("write_file", write_file)
    mcp.register_tool("list_directory", list_directory)
    mcp.register_tool("create_directory", create_directory)
    mcp.register_tool("read_json", read_json)
    mcp.register_tool("write_json", write_json)
    
    # Example usage
    try:
        # Create a test directory
        mcp.execute_tool("create_directory", dir_path="test_dir")
        
        # Write a test file
        mcp.execute_tool(
            "write_file",
            file_path="test_dir/test.txt",
            content="Hello, MCP!"
        )
        
        # Read the test file
        result = mcp.execute_tool("read_file", file_path="test_dir/test.txt")
        if result.success:
            print(f"File contents: {result.data}")
        
        # List directory contents
        result = mcp.execute_tool("list_directory", dir_path="test_dir")
        if result.success:
            print(f"Directory contents: {result.data}")
        
        # Create and read a JSON file
        test_data = {"name": "MCP", "version": "1.0.0"}
        mcp.execute_tool("write_json", file_path="test_dir/config.json", data=test_data)
        
        result = mcp.execute_tool("read_json", file_path="test_dir/config.json")
        if result.success:
            print(f"JSON data: {result.data}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 