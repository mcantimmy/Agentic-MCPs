# Agent Generation System

The Agent Generation system allows primary agents to create sub-agents with the same tool access and capabilities, enabling complex task decomposition and parallel execution.

## Overview

The system consists of several key components:

- **SubAgent**: Individual agents that can execute tasks
- **AgentManager**: Central coordinator for agent lifecycle management
- **AgentTask**: Represents tasks assigned to agents
- **AgentReport**: Reports from sub-agents to their parents
- **MCP Tools**: Tools for creating and managing agents

## Key Features

### 1. Agent Creation and Management
- Create sub-agents with full tool access
- Hierarchical agent structures
- Automatic tool inheritance from parent agents
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
- Sub-agents inherit all tools from parent agents
- Dynamic tool discovery and execution
- Tool parameter parsing and validation

## Available MCP Tools

### 1. `create_sub_agent`
Creates a new sub-agent with access to the same tools as the parent.

**Parameters:**
- `name` (str): Name of the agent
- `parent_agent_id` (str, optional): ID of the parent agent
- `description` (str, optional): Description of the agent's purpose

**Example:**
```python
await create_sub_agent(
    name="CodeReviewAgent",
    parent_agent_id="primary-agent-123",
    description="Specialized agent for code review tasks"
)
```

### 2. `assign_task_to_agent`
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

### 3. `get_agent_status`
Gets the current status and information about an agent.

**Parameters:**
- `agent_id` (str): ID of the agent

**Returns:**
- Agent status, current task, completed tasks count, available tools

### 4. `get_agent_reports`
Gets all reports from a specific agent.

**Parameters:**
- `agent_id` (str): ID of the agent

**Returns:**
- List of task execution reports with results and metadata

### 5. `list_all_agents`
Lists all active agents and their status.

**Returns:**
- Complete list of all agents with their current status

### 6. `terminate_agent`
Terminates a specific agent and cleans up its resources.

**Parameters:**
- `agent_id` (str): ID of the agent to terminate

### 7. `create_agent_hierarchy`
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

## Usage Examples

### Basic Agent Creation and Task Assignment

```python
# Create a sub-agent
result = await create_sub_agent("TestAgent", "primary-123")
agent_data = json.loads(result)
agent_id = agent_data["agent_id"]

# Assign a task
task_result = await assign_task_to_agent(
    agent_id=agent_id,
    task_description="Test file analysis",
    instructions="analyze_file: {\"path\": \"test.py\"}"
)

# Check status
status = await get_agent_status(agent_id)
print(f"Agent status: {status}")
```

### Complex Task Decomposition

```python
# Create a hierarchy of specialized agents
hierarchy_result = await create_agent_hierarchy({
    "coordinator": "ProjectManager",
    "sub_agents": [
        {"name": "CodeAnalyzer", "role": "code_analysis"},
        {"name": "SecurityAuditor", "role": "security"},
        {"name": "PerformanceTester", "role": "performance"}
    ]
})

hierarchy_data = json.loads(hierarchy_result)
coordinator_id = hierarchy_data["coordinator_id"]

# Assign different tasks to different agents
for agent in hierarchy_data["agents"]:
    if agent["role"] == "code_analysis":
        await assign_task_to_agent(
            agent_id=agent["agent_id"],
            task_description="Analyze code quality",
            instructions="analyze_codebase: {\"directory\": \"src/\"}"
        )
    elif agent["role"] == "security":
        await assign_task_to_agent(
            agent_id=agent["agent_id"],
            task_description="Security audit",
            instructions="security_scan: {\"target\": \"auth.py\"}"
        )
```

### Monitoring and Reporting

```python
# List all agents
agents = await list_all_agents()
agents_data = json.loads(agents)

for agent in agents_data["agents"]:
    print(f"Agent: {agent['name']} - Status: {agent['status']}")
    
    # Get reports for each agent
    reports = await get_agent_reports(agent["agent_id"])
    reports_data = json.loads(reports)
    
    for report in reports_data:
        print(f"  Task {report['task_id']}: {report['status']}")
        if report['result']:
            print(f"    Result: {report['result']}")
```

## Architecture

### Agent Lifecycle

1. **Creation**: Agent is created with inherited tools
2. **Initialization**: Agent starts background processing
3. **Task Assignment**: Tasks are assigned to idle agents
4. **Execution**: Agent processes task instructions
5. **Reporting**: Results are reported back to parent
6. **Termination**: Agent is cleaned up when no longer needed

### Communication Flow

```
Primary Agent
    ↓ creates
Sub-Agent 1
    ↓ creates
Sub-Agent 1.1
    ↓ reports back
Sub-Agent 1
    ↓ reports back
Primary Agent
```

### Tool Inheritance

- Primary agent has access to all MCP tools
- Sub-agents inherit tools from their parent
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