#!/usr/bin/env python3
"""
Example script demonstrating the Agent Generation system.

This script shows how to:
1. Register as the primary agent
2. Create sub-agents
3. Assign tasks to agents
4. Monitor agent status
5. Collect results from agents
"""

import asyncio
import json
import sys
import os

# Add the parent directory to the path to import mcp_tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tools.agent_generation import (
    register_as_primary_agent,
    get_primary_agent_id,
    create_sub_agent,
    assign_task_to_agent,
    get_agent_status,
    get_agent_reports,
    list_all_agents,
    terminate_agent,
    create_agent_hierarchy,
    TaskPriority
)


async def registration_example():
    """Example of registering as the primary agent."""
    print("=== Primary Agent Registration Example ===")
    
    # Register as the primary agent
    print("Registering as the primary agent...")
    result = await register_as_primary_agent(
        agent_name="ClaudeAgent",
        description="Claude AI agent accessing MCP tools"
    )
    primary_data = json.loads(result)
    primary_agent_id = primary_data["agent_id"]
    print(f"Registered as primary agent: {primary_data}")
    
    # Get primary agent ID
    print("\nGetting primary agent ID...")
    primary_id_result = await get_primary_agent_id()
    primary_id_data = json.loads(primary_id_result)
    print(f"Primary agent info: {primary_id_data}")
    
    return primary_agent_id


async def basic_agent_example(primary_agent_id: str):
    """Basic example of creating and using a single agent."""
    print("\n=== Basic Agent Example ===")
    
    # Create a sub-agent
    print("Creating a code review agent...")
    result = await create_sub_agent(
        name="CodeReviewAgent",
        description="Specialized agent for code review tasks"
    )
    agent_data = json.loads(result)
    agent_id = agent_data["agent_id"]
    print(f"Created agent: {agent_data}")
    
    # Assign a task to the agent
    print("\nAssigning a code review task...")
    task_result = await assign_task_to_agent(
        agent_id=agent_id,
        task_description="Review the main application file",
        instructions="""
        # This is a simple example - in practice, you would use actual tool names
        # analyze_code: {"file_path": "main.py", "analysis_type": "complexity"}
        # check_security: {"focus": "authentication"}
        # generate_report: {"format": "markdown"}
        """,
        priority=TaskPriority.HIGH
    )
    task_data = json.loads(task_result)
    print(f"Task assigned: {task_data}")
    
    # Wait a moment for task execution
    print("\nWaiting for task completion...")
    await asyncio.sleep(2)
    
    # Check agent status
    status = await get_agent_status(agent_id)
    status_data = json.loads(status)
    print(f"Agent status: {status_data}")
    
    # Get agent reports
    reports = await get_agent_reports(agent_id)
    reports_data = json.loads(reports)
    print(f"Agent reports: {reports_data}")
    
    # Clean up
    await terminate_agent(agent_id)
    print("Agent terminated.")


async def hierarchy_example(primary_agent_id: str):
    """Example of creating a hierarchy of agents."""
    print("\n=== Agent Hierarchy Example ===")
    
    # Create a hierarchy of specialized agents
    print("Creating agent hierarchy...")
    hierarchy_result = await create_agent_hierarchy({
        "coordinator": "ProjectManager",
        "sub_agents": [
            {"name": "CodeAnalyzer", "role": "code_analysis"},
            {"name": "SecurityAuditor", "role": "security"},
            {"name": "PerformanceTester", "role": "performance"}
        ]
    })
    
    hierarchy_data = json.loads(hierarchy_result)
    print(f"Created hierarchy: {hierarchy_data}")
    
    # Assign different tasks to different agents
    print("\nAssigning specialized tasks...")
    for agent in hierarchy_data["agents"]:
        if agent["role"] == "code_analysis":
            await assign_task_to_agent(
                agent_id=agent["agent_id"],
                task_description="Analyze code quality and complexity",
                instructions="""
                # analyze_codebase: {"directory": "src/", "metrics": ["complexity", "maintainability"]}
                # generate_metrics_report: {"format": "json"}
                """,
                priority=TaskPriority.MEDIUM
            )
        elif agent["role"] == "security":
            await assign_task_to_agent(
                agent_id=agent["agent_id"],
                task_description="Perform security audit",
                instructions="""
                # security_scan: {"target": "auth.py", "scan_type": "vulnerabilities"}
                # check_dependencies: {"package_manager": "pip"}
                # generate_security_report: {"format": "markdown"}
                """,
                priority=TaskPriority.HIGH
            )
        elif agent["role"] == "performance":
            await assign_task_to_agent(
                agent_id=agent["agent_id"],
                task_description="Test application performance",
                instructions="""
                # performance_test: {"endpoint": "/api/users", "load": "medium"}
                # benchmark_code: {"target": "database_queries.py"}
                # generate_performance_report: {"format": "html"}
                """,
                priority=TaskPriority.MEDIUM
            )
    
    # Wait for tasks to complete
    print("\nWaiting for tasks to complete...")
    await asyncio.sleep(3)
    
    # Monitor all agents
    print("\nMonitoring all agents...")
    agents = await list_all_agents()
    agents_data = json.loads(agents)
    
    for agent in agents_data["agents"]:
        print(f"\nAgent: {agent['name']} ({agent['agent_id']})")
        print(f"  Status: {agent['status']}")
        print(f"  Completed tasks: {agent['completed_tasks_count']}")
        print(f"  Available tools: {len(agent['available_tools'])}")
        
        # Get reports for this agent
        reports = await get_agent_reports(agent["agent_id"])
        reports_data = json.loads(reports)
        
        for report in reports_data:
            print(f"  Task {report['task_id'][:8]}...: {report['status']}")
            if report['execution_time']:
                print(f"    Execution time: {report['execution_time']:.2f}s")
    
    # Clean up all agents
    print("\nCleaning up agents...")
    for agent in agents_data["agents"]:
        await terminate_agent(agent["agent_id"])
    print("All agents terminated.")


async def monitoring_example(primary_agent_id: str):
    """Example of monitoring agent activities."""
    print("\n=== Agent Monitoring Example ===")
    
    # Create multiple agents
    agents = []
    for i in range(3):
        result = await create_sub_agent(f"WorkerAgent_{i+1}")
        agent_data = json.loads(result)
        agents.append(agent_data["agent_id"])
    
    print(f"Created {len(agents)} worker agents")
    
    # Assign simple tasks to each agent
    for i, agent_id in enumerate(agents):
        await assign_task_to_agent(
            agent_id=agent_id,
            task_description=f"Task {i+1}",
            instructions=f"# process_data: {{\"task_id\": {i+1}}}",
            priority=TaskPriority.LOW
        )
    
    # Monitor agents in real-time
    print("\nMonitoring agents in real-time...")
    for _ in range(5):  # Monitor for 5 iterations
        all_agents = await list_all_agents()
        agents_data = json.loads(all_agents)
        
        print(f"\n--- Status Update ---")
        for agent in agents_data["agents"]:
            status = await get_agent_status(agent["agent_id"])
            status_data = json.loads(status)
            print(f"{agent['name']}: {status_data['status']}")
        
        await asyncio.sleep(1)
    
    # Clean up
    for agent_id in agents:
        await terminate_agent(agent_id)
    print("Monitoring example completed.")


async def main():
    """Run all examples."""
    print("Agent Generation System Examples")
    print("=" * 50)
    
    try:
        # Step 1: Register as primary agent
        primary_agent_id = await registration_example()
        
        # Step 2: Run basic example
        await basic_agent_example(primary_agent_id)
        
        # Step 3: Run hierarchy example
        await hierarchy_example(primary_agent_id)
        
        # Step 4: Run monitoring example
        await monitoring_example(primary_agent_id)
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Create examples directory if it doesn't exist
    os.makedirs("examples", exist_ok=True)
    
    # Run the examples
    asyncio.run(main()) 