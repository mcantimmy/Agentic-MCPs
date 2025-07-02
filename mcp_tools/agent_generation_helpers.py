"""
Helper functions for agent generation that can be called directly.
These functions bypass the MCP tool decorators for direct testing and examples.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any
from .agent_generation import (
    _agent_manager, 
    AgentTask, 
    TaskPriority,
    AgentStatus
)


async def register_as_primary_agent_helper(
    agent_name: str = "ExternalPrimaryAgent",
    description: str = ""
) -> str:
    """Helper function to register as primary agent."""
    from .agent_generation import SubAgent
    from .base import ToolRegistry
    
    # Create a new agent ID for the external agent
    external_agent_id = str(uuid.uuid4())
    
    # Create the external agent
    external_agent = SubAgent(external_agent_id, agent_name)
    
    # Add all available tools to the external agent
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


async def get_primary_agent_id_helper() -> str:
    """Helper function to get primary agent ID."""
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


async def create_sub_agent_helper(
    name: str,
    parent_agent_id: Optional[str] = None,
    description: str = ""
) -> str:
    """Helper function to create sub-agent."""
    agent_id = _agent_manager.create_agent(name, parent_agent_id)
    
    return json.dumps({
        "agent_id": agent_id,
        "name": name,
        "status": "created",
        "message": f"Sub-agent '{name}' created successfully with ID: {agent_id}"
    })


async def assign_task_to_agent_helper(
    agent_id: str,
    task_description: str,
    instructions: str,
    priority: TaskPriority = TaskPriority.MEDIUM,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Helper function to assign task to agent."""
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


async def get_agent_status_helper(agent_id: str) -> str:
    """Helper function to get agent status."""
    status = _agent_manager.get_agent_status(agent_id)
    
    if status:
        return json.dumps(status, default=str)
    else:
        return json.dumps({
            "error": f"Agent {agent_id} not found"
        })


async def get_agent_reports_helper(agent_id: str) -> str:
    """Helper function to get agent reports."""
    from .agent_generation import AgentReport
    
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


async def list_all_agents_helper() -> str:
    """Helper function to list all agents."""
    agents = _agent_manager.get_all_agents()
    
    return json.dumps({
        "agents": agents,
        "total_count": len(agents)
    }, default=str)


async def terminate_agent_helper(agent_id: str) -> str:
    """Helper function to terminate agent."""
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


async def create_agent_hierarchy_helper(
    hierarchy_config: Dict[str, Any],
    parent_agent_id: Optional[str] = None
) -> str:
    """Helper function to create agent hierarchy."""
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