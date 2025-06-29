"""
Agent generation tools for MCP.
"""

import asyncio
import json
import uuid
import time
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from .base import MCPTool, ToolCategory, mcp_tool
import threading
import queue


class AgentStatus(str, Enum):
    """Status of an agent."""
    IDLE = "idle"
    BUSY = "busy"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


class TaskPriority(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentTask:
    """Represents a task assigned to an agent."""
    id: str
    description: str
    instructions: str
    priority: TaskPriority = TaskPriority.MEDIUM
    parent_agent_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentReport:
    """Report from a sub-agent to its parent."""
    agent_id: str
    task_id: str
    status: AgentStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class SubAgent:
    """Represents a sub-agent that can execute tasks."""
    
    def __init__(self, agent_id: str, name: str, parent_agent_id: Optional[str] = None):
        self.agent_id = agent_id
        self.name = name
        self.parent_agent_id = parent_agent_id
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None
        self.completed_tasks: List[AgentTask] = []
        self.tools: List[MCPTool] = []
        self.message_queue = queue.Queue()
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        
    def add_tool(self, tool: MCPTool):
        """Add a tool to the agent's toolkit."""
        self.tools.append(tool)
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.tools]
    
    async def execute_task(self, task: AgentTask) -> AgentReport:
        """Execute a task and return a report."""
        self.status = AgentStatus.BUSY
        self.current_task = task
        start_time = time.time()
        
        try:
            # Parse instructions and execute
            result = await self._process_instructions(task.instructions)
            
            # Mark task as completed
            task.completed_at = time.time()
            task.result = result
            self.completed_tasks.append(task)
            
            self.status = AgentStatus.COMPLETED
            
            return AgentReport(
                agent_id=self.agent_id,
                task_id=task.id,
                status=AgentStatus.COMPLETED,
                result=result,
                execution_time=time.time() - start_time,
                metadata={"agent_name": self.name}
            )
            
        except Exception as e:
            task.error = str(e)
            self.status = AgentStatus.FAILED
            
            return AgentReport(
                agent_id=self.agent_id,
                task_id=task.id,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start_time,
                metadata={"agent_name": self.name}
            )
        finally:
            self.current_task = None
    
    async def _process_instructions(self, instructions: str) -> Any:
        """Process and execute instructions."""
        # This is a simplified implementation
        # In a real system, this would parse natural language instructions
        # and map them to tool calls
        
        # For now, we'll assume instructions contain tool calls in a specific format
        # Format: TOOL_NAME: {parameters}
        
        lines = instructions.strip().split('\n')
        results = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if ':' in line:
                tool_name, params_str = line.split(':', 1)
                tool_name = tool_name.strip()
                params_str = params_str.strip()
                
                # Try to parse parameters as JSON
                try:
                    params = json.loads(params_str) if params_str else {}
                except json.JSONDecodeError:
                    # If not valid JSON, treat as a simple string parameter
                    params = {"input": params_str}
                
                # Find and execute the tool
                tool = self.get_tool(tool_name)
                if tool:
                    if asyncio.iscoroutinefunction(tool.execute):
                        result = await tool.execute(**params)
                    else:
                        result = tool.execute(**params)
                    results.append(result)
                else:
                    raise ValueError(f"Tool '{tool_name}' not found")
        
        return results if len(results) > 1 else (results[0] if results else None)
    
    def start(self):
        """Start the agent's background processing."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the agent."""
        self.is_running = False
        self.status = AgentStatus.TERMINATED
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _run(self):
        """Background processing loop."""
        while self.is_running:
            try:
                # Check for messages/tasks
                try:
                    message = self.message_queue.get(timeout=1.0)
                    # Process message (implement as needed)
                except queue.Empty:
                    continue
            except Exception as e:
                print(f"Agent {self.name} error: {e}")
                time.sleep(1)


class AgentManager:
    """Manages the creation and coordination of agents."""
    
    def __init__(self):
        self.agents: Dict[str, SubAgent] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.reports: Dict[str, List[AgentReport]] = {}
        self.primary_agent_id: Optional[str] = None
        
    def create_agent(self, name: str, parent_agent_id: Optional[str] = None) -> str:
        """Create a new sub-agent."""
        agent_id = str(uuid.uuid4())
        agent = SubAgent(agent_id, name, parent_agent_id)
        
        # Copy tools from parent agent or primary agent
        if parent_agent_id and parent_agent_id in self.agents:
            parent_agent = self.agents[parent_agent_id]
            for tool in parent_agent.tools:
                agent.add_tool(tool)
        elif self.primary_agent_id and self.primary_agent_id in self.agents:
            primary_agent = self.agents[self.primary_agent_id]
            for tool in primary_agent.tools:
                agent.add_tool(tool)
        
        self.agents[agent_id] = agent
        self.reports[agent_id] = []
        
        # Start the agent
        agent.start()
        
        return agent_id
    
    def assign_task(self, agent_id: str, task: AgentTask) -> bool:
        """Assign a task to an agent."""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        if agent.status != AgentStatus.IDLE:
            return False
        
        self.tasks[task.id] = task
        task.parent_agent_id = agent_id
        
        # Execute task asynchronously
        asyncio.create_task(self._execute_task_async(agent, task))
        
        return True
    
    async def _execute_task_async(self, agent: SubAgent, task: AgentTask):
        """Execute a task asynchronously and collect the report."""
        report = await agent.execute_task(task)
        
        # Store the report
        if agent.agent_id not in self.reports:
            self.reports[agent.agent_id] = []
        self.reports[agent.agent_id].append(report)
        
        # Send report to parent agent if exists
        if agent.parent_agent_id and agent.parent_agent_id in self.agents:
            parent_agent = self.agents[agent.parent_agent_id]
            parent_agent.message_queue.put(report)
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status information for an agent."""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "status": agent.status.value,
            "parent_agent_id": agent.parent_agent_id,
            "current_task": agent.current_task.id if agent.current_task else None,
            "completed_tasks_count": len(agent.completed_tasks),
            "available_tools": agent.get_available_tools()
        }
    
    def get_agent_reports(self, agent_id: str) -> List[AgentReport]:
        """Get reports from an agent."""
        return self.reports.get(agent_id, [])
    
    def terminate_agent(self, agent_id: str) -> bool:
        """Terminate an agent."""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        agent.stop()
        del self.agents[agent_id]
        
        return True
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get information about all agents."""
        return [self.get_agent_status(agent_id) for agent_id in self.agents.keys()]


# Global agent manager instance
_agent_manager = AgentManager()


@mcp_tool(
    name="create_sub_agent",
    description="Create a new sub-agent with access to the same tools as the primary agent",
    category=ToolCategory.AGENT_GENERATION,
    examples=[
        {
            "name": "CodeReviewAgent",
            "parent_agent_id": "primary-agent-123",
            "description": "Create a specialized agent for code review tasks"
        }
    ]
)
async def create_sub_agent(
    name: str,
    parent_agent_id: Optional[str] = None,
    description: str = ""
) -> str:
    """Create a new sub-agent with the same tool access as the parent."""
    agent_id = _agent_manager.create_agent(name, parent_agent_id)
    
    return json.dumps({
        "agent_id": agent_id,
        "name": name,
        "status": "created",
        "message": f"Sub-agent '{name}' created successfully with ID: {agent_id}"
    })


@mcp_tool(
    name="assign_task_to_agent",
    description="Assign a task to a specific agent for execution",
    category=ToolCategory.AGENT_GENERATION,
    examples=[
        {
            "agent_id": "agent-123",
            "task_description": "Review the user authentication code",
            "instructions": "Analyze the security of the login system and report any vulnerabilities",
            "priority": "high"
        }
    ]
)
async def assign_task_to_agent(
    agent_id: str,
    task_description: str,
    instructions: str,
    priority: TaskPriority = TaskPriority.MEDIUM,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Assign a task to a specific agent."""
    task = AgentTask(
        id=str(uuid.uuid4()),
        description=task_description,
        instructions=instructions,
        priority=priority,
        metadata=metadata or {}
    )
    
    success = _agent_manager.assign_task(agent_id, task)
    
    if success:
        return json.dumps({
            "task_id": task.id,
            "agent_id": agent_id,
            "status": "assigned",
            "message": f"Task '{task_description}' assigned to agent {agent_id}"
        })
    else:
        return json.dumps({
            "status": "failed",
            "error": f"Failed to assign task to agent {agent_id}. Agent may not exist or be busy."
        })


@mcp_tool(
    name="get_agent_status",
    description="Get the current status and information about an agent",
    category=ToolCategory.AGENT_GENERATION,
    examples=[
        {
            "agent_id": "agent-123"
        }
    ]
)
async def get_agent_status(agent_id: str) -> str:
    """Get status information for a specific agent."""
    status = _agent_manager.get_agent_status(agent_id)
    
    if status:
        return json.dumps(status, default=str)
    else:
        return json.dumps({
            "error": f"Agent {agent_id} not found"
        })


@mcp_tool(
    name="get_agent_reports",
    description="Get all reports from a specific agent",
    category=ToolCategory.AGENT_GENERATION,
    examples=[
        {
            "agent_id": "agent-123"
        }
    ]
)
async def get_agent_reports(agent_id: str) -> str:
    """Get all reports from a specific agent."""
    reports = _agent_manager.get_agent_reports(agent_id)
    
    # Convert reports to serializable format
    serializable_reports = []
    for report in reports:
        serializable_reports.append({
            "agent_id": report.agent_id,
            "task_id": report.task_id,
            "status": report.status.value,
            "result": report.result,
            "error": report.error,
            "execution_time": report.execution_time,
            "metadata": report.metadata,
            "timestamp": report.timestamp
        })
    
    return json.dumps(serializable_reports, default=str)


@mcp_tool(
    name="list_all_agents",
    description="List all active agents and their status",
    category=ToolCategory.AGENT_GENERATION,
    examples=[
        {}
    ]
)
async def list_all_agents() -> str:
    """List all active agents and their status."""
    agents = _agent_manager.get_all_agents()
    
    return json.dumps({
        "agents": agents,
        "total_count": len(agents)
    }, default=str)


@mcp_tool(
    name="terminate_agent",
    description="Terminate a specific agent and clean up its resources",
    category=ToolCategory.AGENT_GENERATION,
    examples=[
        {
            "agent_id": "agent-123"
        }
    ]
)
async def terminate_agent(agent_id: str) -> str:
    """Terminate a specific agent."""
    success = _agent_manager.terminate_agent(agent_id)
    
    if success:
        return json.dumps({
            "status": "terminated",
            "message": f"Agent {agent_id} terminated successfully"
        })
    else:
        return json.dumps({
            "status": "failed",
            "error": f"Failed to terminate agent {agent_id}. Agent may not exist."
        })


@mcp_tool(
    name="create_agent_hierarchy",
    description="Create a hierarchy of agents for complex task decomposition",
    category=ToolCategory.AGENT_GENERATION,
    examples=[
        {
            "hierarchy_config": {
                "coordinator": "TaskCoordinator",
                "sub_agents": [
                    {"name": "CodeReviewer", "role": "code_review"},
                    {"name": "Tester", "role": "testing"},
                    {"name": "Documenter", "role": "documentation"}
                ]
            }
        }
    ]
)
async def create_agent_hierarchy(
    hierarchy_config: Dict[str, Any],
    parent_agent_id: Optional[str] = None
) -> str:
    """Create a hierarchy of agents for complex task decomposition."""
    created_agents = []
    
    # Create coordinator agent
    coordinator_name = hierarchy_config.get("coordinator", "Coordinator")
    coordinator_id = _agent_manager.create_agent(coordinator_name, parent_agent_id)
    created_agents.append({
        "agent_id": coordinator_id,
        "name": coordinator_name,
        "role": "coordinator",
        "parent_agent_id": parent_agent_id
    })
    
    # Create sub-agents
    sub_agents_config = hierarchy_config.get("sub_agents", [])
    for sub_agent_config in sub_agents_config:
        name = sub_agent_config.get("name", f"SubAgent_{len(created_agents)}")
        role = sub_agent_config.get("role", "general")
        
        sub_agent_id = _agent_manager.create_agent(name, coordinator_id)
        created_agents.append({
            "agent_id": sub_agent_id,
            "name": name,
            "role": role,
            "parent_agent_id": coordinator_id
        })
    
    return json.dumps({
        "hierarchy_created": True,
        "coordinator_id": coordinator_id,
        "agents": created_agents,
        "message": f"Created agent hierarchy with {len(created_agents)} agents"
    })


@mcp_tool(
    name="register_as_primary_agent",
    description="Register the external agent as the primary agent and get its ID",
    category=ToolCategory.AGENT_GENERATION,
    examples=[
        {
            "agent_name": "ClaudeAgent",
            "description": "Register Claude as the primary agent"
        }
    ]
)
async def register_as_primary_agent(
    agent_name: str = "ExternalPrimaryAgent",
    description: str = ""
) -> str:
    """Register the external agent as the primary agent.
    
    This allows the external agent (Claude, GPT, etc.) to identify itself
    as the primary agent and create sub-agents that inherit its tool access.
    """
    # Create a new agent ID for the external agent
    external_agent_id = str(uuid.uuid4())
    
    # Create the external agent
    external_agent = SubAgent(external_agent_id, agent_name)
    
    # Add all available tools to the external agent
    from .base import ToolRegistry
    all_tools = ToolRegistry.get_all_tools()
    for tool in all_tools:
        external_agent.add_tool(tool)
    
    # Register the external agent
    _agent_manager.agents[external_agent_id] = external_agent
    _agent_manager.primary_agent_id = external_agent_id
    _agent_manager.reports[external_agent_id] = []
    
    # Start the external agent
    external_agent.start()
    
    return json.dumps({
        "agent_id": external_agent_id,
        "name": agent_name,
        "status": "registered_as_primary",
        "message": f"External agent '{agent_name}' registered as primary agent with ID: {external_agent_id}",
        "available_tools_count": len(all_tools)
    })


@mcp_tool(
    name="get_primary_agent_id",
    description="Get the ID of the current primary agent",
    category=ToolCategory.AGENT_GENERATION,
    examples=[
        {}
    ]
)
async def get_primary_agent_id() -> str:
    """Get the ID of the current primary agent."""
    primary_id = _agent_manager.primary_agent_id
    
    if primary_id:
        # Get agent info
        agent_info = _agent_manager.get_agent_status(primary_id)
        if agent_info:
            return json.dumps({
                "primary_agent_id": primary_id,
                "agent_info": agent_info
            })
        else:
            return json.dumps({
                "primary_agent_id": primary_id,
                "message": "Primary agent ID found but agent not in registry"
            })
    else:
        return json.dumps({
            "error": "No primary agent registered"
        }) 


# Initialize primary agent when the module is loaded
def initialize_primary_agent():
    """Initialize the primary agent with all available tools.
    
    Note: This creates an internal primary agent that serves as a template
    for sub-agents. The actual "primary agent" is the external agent
    (Claude, GPT, etc.) that accesses this MCP server and uses these tools
    to create sub-agents.
    """
    from .base import ToolRegistry
    
    primary_agent_id = str(uuid.uuid4())
    primary_agent = SubAgent(primary_agent_id, "InternalPrimaryAgent")
    
    # Add all available tools to the primary agent
    all_tools = ToolRegistry.get_all_tools()
    for tool in all_tools:
        primary_agent.add_tool(tool)
    
    _agent_manager.agents[primary_agent_id] = primary_agent
    _agent_manager.primary_agent_id = primary_agent_id
    _agent_manager.reports[primary_agent_id] = []
    
    # Start the primary agent
    primary_agent.start()
    
    return primary_agent_id


def get_external_primary_agent_id() -> str:
    """Get the ID of the external primary agent (the one accessing the MCP server).
    
    This function allows the external agent to identify itself as the primary
    and create sub-agents that inherit its tool access.
    """
    return _agent_manager.primary_agent_id


def set_external_primary_agent_id(agent_id: str):
    """Set the external primary agent ID.
    
    This allows the external agent to register itself as the primary agent
    when it first accesses the MCP server.
    """
    _agent_manager.primary_agent_id = agent_id


# Initialize the primary agent when the module is imported
_primary_agent_id = initialize_primary_agent()