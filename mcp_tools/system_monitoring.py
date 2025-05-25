"""
System monitoring MCP tools for process monitoring and resource tracking.
"""

import psutil
import os
import platform
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base import MCPTool, ToolCategory


class ProcessMonitor(MCPTool):
    """Monitor system processes and their resource usage."""
    
    @property
    def name(self) -> str:
        return "monitor_processes"
    
    @property
    def description(self) -> str:
        return "Monitor system processes including CPU, memory usage, and process details"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.SYSTEM_MONITORING
    
    async def execute(self, 
                     sort_by: str = "cpu_percent",
                     limit: int = 10,
                     filter_name: Optional[str] = None) -> Dict[str, Any]:
        """Monitor system processes."""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'create_time', 'status', 'username']):
                try:
                    proc_info = proc.info
                    
                    # Filter by name if specified
                    if filter_name and filter_name.lower() not in proc_info['name'].lower():
                        continue
                    
                    # Add additional info
                    proc_info['memory_mb'] = proc_info['memory_info'].rss / 1024 / 1024
                    proc_info['created'] = datetime.fromtimestamp(proc_info['create_time']).isoformat()
                    
                    processes.append(proc_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort processes
            if sort_by in ['cpu_percent', 'memory_percent', 'memory_mb']:
                processes.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
            elif sort_by == 'name':
                processes.sort(key=lambda x: x.get('name', '').lower())
            
            # Limit results
            processes = processes[:limit]
            
            return {
                "timestamp": datetime.now().isoformat(),
                "total_processes": len(list(psutil.process_iter())),
                "filtered_processes": len(processes),
                "processes": processes
            }
            
        except Exception as e:
            return {"error": str(e)}


class SystemResourceMonitor(MCPTool):
    """Monitor system resources like CPU, memory, disk, and network."""
    
    @property
    def name(self) -> str:
        return "monitor_system_resources"
    
    @property
    def description(self) -> str:
        return "Monitor system resources including CPU, memory, disk usage, and network statistics"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.SYSTEM_MONITORING
    
    async def execute(self, include_network: bool = True, include_disk: bool = True) -> Dict[str, Any]:
        """Monitor system resources."""
        try:
            result = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "count_logical": psutil.cpu_count(logical=True),
                    "per_cpu": psutil.cpu_percent(interval=1, percpu=True)
                },
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "used": psutil.virtual_memory().used,
                    "percent": psutil.virtual_memory().percent,
                    "total_gb": round(psutil.virtual_memory().total / 1024**3, 2),
                    "available_gb": round(psutil.virtual_memory().available / 1024**3, 2),
                    "used_gb": round(psutil.virtual_memory().used / 1024**3, 2)
                },
                "swap": {
                    "total": psutil.swap_memory().total,
                    "used": psutil.swap_memory().used,
                    "percent": psutil.swap_memory().percent,
                    "total_gb": round(psutil.swap_memory().total / 1024**3, 2),
                    "used_gb": round(psutil.swap_memory().used / 1024**3, 2)
                }
            }
            
            if include_disk:
                disk_usage = []
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_usage.append({
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": (usage.used / usage.total) * 100,
                            "total_gb": round(usage.total / 1024**3, 2),
                            "used_gb": round(usage.used / 1024**3, 2),
                            "free_gb": round(usage.free / 1024**3, 2)
                        })
                    except PermissionError:
                        continue
                
                result["disk"] = disk_usage
            
            if include_network:
                net_io = psutil.net_io_counters()
                result["network"] = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "bytes_sent_mb": round(net_io.bytes_sent / 1024**2, 2),
                    "bytes_recv_mb": round(net_io.bytes_recv / 1024**2, 2)
                }
            
            return result
            
        except Exception as e:
            return {"error": str(e)}


class SystemInfoCollector(MCPTool):
    """Collect comprehensive system information."""
    
    @property
    def name(self) -> str:
        return "collect_system_info"
    
    @property
    def description(self) -> str:
        return "Collect comprehensive system information including OS, hardware, and environment details"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.SYSTEM_MONITORING
    
    async def execute(self) -> Dict[str, Any]:
        """Collect system information."""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "platform": platform.platform(),
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "architecture": platform.architecture(),
                    "hostname": platform.node(),
                    "boot_time": boot_time.isoformat(),
                    "uptime_seconds": (datetime.now() - boot_time).total_seconds()
                },
                "python": {
                    "version": platform.python_version(),
                    "implementation": platform.python_implementation(),
                    "compiler": platform.python_compiler()
                },
                "environment": {
                    "user": os.getenv('USER') or os.getenv('USERNAME'),
                    "home": os.getenv('HOME') or os.getenv('USERPROFILE'),
                    "path": os.getenv('PATH', '').split(os.pathsep)[:10],  # First 10 paths
                    "shell": os.getenv('SHELL') or os.getenv('COMSPEC'),
                    "terminal": os.getenv('TERM'),
                    "lang": os.getenv('LANG'),
                    "timezone": os.getenv('TZ')
                }
            }
            
            # Add CPU info
            try:
                cpu_freq = psutil.cpu_freq()
                result["cpu"] = {
                    "physical_cores": psutil.cpu_count(logical=False),
                    "logical_cores": psutil.cpu_count(logical=True),
                    "max_frequency": cpu_freq.max if cpu_freq else None,
                    "min_frequency": cpu_freq.min if cpu_freq else None,
                    "current_frequency": cpu_freq.current if cpu_freq else None
                }
            except:
                result["cpu"] = {"cores": psutil.cpu_count()}
            
            # Add memory info
            memory = psutil.virtual_memory()
            result["memory"] = {
                "total_gb": round(memory.total / 1024**3, 2),
                "available_gb": round(memory.available / 1024**3, 2)
            }
            
            return result
            
        except Exception as e:
            return {"error": str(e)}


# Initialize tools
process_monitor = ProcessMonitor()
system_resource_monitor = SystemResourceMonitor()
system_info_collector = SystemInfoCollector() 