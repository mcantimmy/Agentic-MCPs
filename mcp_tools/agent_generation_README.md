# Agent Generation System

The Agent Generation system allows **external agents** (like Claude, GPT, etc.) that access the MCP server to create sub-agents with the same tool access and capabilities, enabling complex task decomposition and parallel execution.

## Overview

The system consists of several key components:

- **External Primary Agent**: The agent (Claude, GPT, etc.) that accesses the MCP server and uses these tools
- **SubAgent**: Individual agents created by the external agent to execute tasks
- **AgentManager**: Central coordinator for agent lifecycle management
- **AgentTask**: Represents tasks assigned to agents
- **AgentReport**: Reports from sub-agents to their parents
- **MCP Tools**: Tools for creating and managing agents

## Key Concepts

### Primary Agent vs External Agent

- **External Agent**: The AI agent (Claude, GPT, etc.) that connects to the MCP server and uses these tools
- **Primary Agent**: A representation of the external agent within the system that can create sub-agents
- **Sub-Agents**: Agents created by the primary agent that inherit its tool access

### Tool Inheritance Flow

```
External Agent (Claude/GPT) 
    ↓ accesses MCP server
    ↓ registers as primary agent
Primary Agent (with all MCP tools)
    ↓ creates sub-agents
SubAgents (inherit all tools from primary)
    ↓ execute tasks
    ↓ report back to primary
Primary Agent
    ↓ reports to external agent
External Agent
```

## Key Features

### 1. Agent Registration and Management
- External agents can register themselves as the primary agent
- Create sub-agents with full tool access
- Hierarchical agent structures
- Automatic tool inheritance from primary agent
- Agent lifecycle management (create, monitor, terminate)

### 2. Task Assignment and Execution
- Assign tasks to specific agents
- Priority-based task scheduling
- Asynchronous task execution
- Task result collection and reporting

### 3. Communication and Reporting
- Parent-child agent communication
- Task completion reports
- Error handling and reporting
- Execution time tracking

### 4. Tool Access
- Sub-agents inherit all tools from the primary agent
- Dynamic tool discovery and execution
- Tool parameter parsing and validation

## Available MCP Tools

### 1. `register_as_primary_agent`
Registers the external agent as the primary agent in the system.

**Parameters:**
- `agent_name` (str): Name of the external agent
- `description` (str, optional): Description of the agent's purpose

**Example:**
```python
await register_as_primary_agent(
    agent_name="ClaudeAgent",
    description="Claude AI agent accessing MCP tools"
)
```

### 2. `get_primary_agent_id`
Gets the ID of the current primary agent.

**Returns:**
- Primary agent ID and information

### 3. `create_sub_agent`
Creates a new sub-agent with access to the same tools as the primary agent.

**Parameters:**
- `name` (str): Name of the agent
- `parent_agent_id` (str, optional): ID of the parent agent (defaults to primary agent)
- `description` (str, optional): Description of the agent's purpose

**Example:**
```python
await create_sub_agent(
    name="CodeReviewAgent",
    description="Specialized agent for code review tasks"
)
```

### 4. `assign_task_to_agent`
Assigns a task to a specific agent for execution.

**Parameters:**
- `agent_id` (str): ID of the target agent
- `task_description` (str): Human-readable task description
- `instructions` (str): Detailed instructions for the agent
- `priority` (TaskPriority): Task priority (low, medium, high, critical)
- `metadata` (dict, optional): Additional task metadata

**Example:**
```python
await assign_task_to_agent(
    agent_id="agent-123",
    task_description="Review the user authentication code",
    instructions="""
    analyze_code: {"file_path": "auth.py"}
    check_security: {"focus": "authentication"}
    generate_report: {"format": "markdown"}
    """,
    priority="high"
)
```

### 5. `get_agent_status`
Gets the current status and information about an agent.

**Parameters:**
- `agent_id` (str): ID of the agent

**Returns:**
- Agent status, current task, completed tasks count, available tools

### 6. `get_agent_reports`
Gets all reports from a specific agent.

**Parameters:**
- `agent_id` (str): ID of the agent

**Returns:**
- List of task execution reports with results and metadata

### 7. `list_all_agents`
Lists all active agents and their status.

**Returns:**
- Complete list of all agents with their current status

### 8. `terminate_agent`
Terminates a specific agent and cleans up its resources.

**Parameters:**
- `agent_id` (str): ID of the agent to terminate

### 9. `create_agent_hierarchy`
Creates a hierarchy of agents for complex task decomposition.

**Parameters:**
- `hierarchy_config` (dict): Configuration for the agent hierarchy
- `parent_agent_id` (str, optional): Parent agent ID

**Example:**
```python
await create_agent_hierarchy({
    "coordinator": "TaskCoordinator",
    "sub_agents": [
        {"name": "CodeReviewer", "role": "code_review"},
        {"name": "Tester", "role": "testing"},
        {"name": "Documenter", "role": "documentation"}
    ]
})
```

## Usage Workflow

### Step 1: Register as Primary Agent
When an external agent first accesses the MCP server, it should register itself:

```python
# Register as the primary agent
result = await register_as_primary_agent("ClaudeAgent")
primary_data = json.loads(result)
primary_agent_id = primary_data["agent_id"]
print(f"Registered as primary agent: {primary_agent_id}")
```

### Step 2: Create Sub-Agents
Create specialized agents for different tasks:

```python
# Create a code review agent
code_review_agent = await create_sub_agent("CodeReviewAgent")
code_review_data = json.loads(code_review_agent)
code_review_id = code_review_data["agent_id"]

# Create a testing agent
testing_agent = await create_sub_agent("TestingAgent")
testing_data = json.loads(testing_agent)
testing_id = testing_data["agent_id"]
```

### Step 3: Assign Tasks
Assign specific tasks to each agent:

```python
# Assign code review task
await assign_task_to_agent(
    agent_id=code_review_id,
    task_description="Review authentication code",
    instructions="analyze_code: {\"file_path\": \"auth.py\"}",
    priority="high"
)

# Assign testing task
await assign_task_to_agent(
    agent_id=testing_id,
    task_description="Run unit tests",
    instructions="run_tests: {\"directory\": \"tests/\"}",
    priority="medium"
)
```

### Step 4: Monitor and Collect Results
Monitor agent progress and collect results:

```python
# Check status of all agents
agents = await list_all_agents()
agents_data = json.loads(agents)

for agent in agents_data["agents"]:
    print(f"Agent: {agent['name']} - Status: {agent['status']}")
    
    # Get reports
    reports = await get_agent_reports(agent["agent_id"])
    reports_data = json.loads(reports)
    
    for report in reports_data:
        if report["status"] == "completed":
            print(f"  Task completed: {report['result']}")
```

## Agent Task Instructions Format

Tasks are executed using a specific instruction format that maps to tool calls:

```
TOOL_NAME: {"param1": "value1", "param2": "value2"}
```

**Example Instructions:**
```
# Analyze a Python file
analyze_code: {"file_path": "main.py", "analysis_type": "complexity"}

# Generate documentation
generate_docs: {"input_file": "api.py", "output_format": "markdown"}

# Run tests
run_tests: {"test_directory": "tests/", "verbose": true}
```

## Agent States

Agents can be in the following states:

- **IDLE**: Agent is available for new tasks
- **BUSY**: Agent is currently executing a task
- **COMPLETED**: Agent has successfully completed its task
- **FAILED**: Agent encountered an error during task execution
- **TERMINATED**: Agent has been stopped and cleaned up

## Task Priorities

Tasks can be assigned different priority levels:

- **LOW**: Background tasks, non-critical
- **MEDIUM**: Standard tasks (default)
- **HIGH**: Important tasks requiring attention
- **CRITICAL**: Urgent tasks requiring immediate execution

## Architecture

### Agent Lifecycle

1. **Registration**: External agent registers as primary agent
2. **Creation**: Sub-agents are created with inherited tools
3. **Initialization**: Agents start background processing
4. **Task Assignment**: Tasks are assigned to idle agents
5. **Execution**: Agent processes task instructions
6. **Reporting**: Results are reported back to parent
7. **Termination**: Agent is cleaned up when no longer needed

### Communication Flow

```
External Agent (Claude/GPT)
    ↓ registers as primary
Primary Agent
    ↓ creates
Sub-Agent 1
    ↓ creates
Sub-Agent 1.1
    ↓ reports back
Sub-Agent 1
    ↓ reports back
Primary Agent
    ↓ reports to external agent
External Agent
```

### Tool Inheritance

- External agent has access to all MCP tools
- Primary agent represents the external agent in the system
- Sub-agents inherit tools from the primary agent
- Each agent maintains its own tool registry
- Tools can be executed asynchronously

## Error Handling

- Task execution errors are captured and reported
- Agent failures don't affect other agents
- Graceful degradation when tools are unavailable
- Automatic cleanup of failed agents

## Performance Considerations

- Agents run in separate threads for parallel execution
- Task queuing prevents resource contention
- Asynchronous execution for non-blocking operations
- Memory management for long-running agents

## Security

- Agent isolation prevents cross-contamination
- Tool access is inherited, not shared
- No direct agent-to-agent communication (only through parent)
- Resource limits prevent abuse

## Future Enhancements

- Agent-to-agent direct communication
- Dynamic tool loading and unloading
- Agent specialization and learning
- Distributed agent execution
- Advanced task scheduling algorithms 