# Agentic MCP Tools

A comprehensive collection of Model Context Protocol (MCP) tools designed to enhance coding agents with powerful capabilities for code analysis, file operations, web scraping, system monitoring, and more.

## Features

### Core MCP Tools
- **Code Analysis Tools**: AST parsing, complexity analysis, dependency detection
- **File Operations**: Advanced file manipulation, search, and monitoring
- **Web Scraping**: Extract content from web pages and APIs
- **System Monitoring**: Process monitoring, resource usage tracking
- **Git Operations**: Repository analysis and version control operations
- **Code Quality**: Linting, formatting, and testing utilities
- **Documentation**: Generate and parse documentation

### Interactive Interface
- Web-based tool browser with search functionality
- Real-time tool testing and execution
- Detailed documentation for each tool
- Usage examples and parameter descriptions

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Agentic-MCPs
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the interactive interface:
```bash
python run_interface.py
```

4. Open your browser to `http://localhost:8000` to explore the tools

## Usage

### As MCP Server
```python
from mcp_tools.server import MCPServer

server = MCPServer()
server.start()
```

### Individual Tool Usage
```python
from mcp_tools.code_analysis import analyze_code_complexity

result = analyze_code_complexity("path/to/file.py")
print(result)
```

## Tool Categories

1. **Code Analysis** - Parse, analyze, and understand code structure
2. **File Operations** - Advanced file and directory manipulation
3. **Web & API** - Web scraping and API interaction tools
4. **System Monitoring** - Monitor processes and system resources
5. **Git Operations** - Version control and repository analysis
6. **Code Quality** - Linting, formatting, and testing
7. **Documentation** - Generate and parse various documentation formats

## Contributing

Feel free to add new tools or improve existing ones. Each tool should follow the MCP protocol specification and include proper documentation.

## License

MIT License 