"""
Git operations MCP tools for repository analysis and version control.
"""

import git
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .base import MCPTool, ToolCategory


class GitRepositoryAnalyzer(MCPTool):
    """Analyze Git repository information and statistics."""
    
    @property
    def name(self) -> str:
        return "analyze_git_repository"
    
    @property
    def description(self) -> str:
        return "Analyze Git repository including commit history, branches, and repository statistics"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.GIT_OPERATIONS
    
    async def execute(self, repo_path: str, max_commits: int = 100) -> Dict[str, Any]:
        """Analyze Git repository."""
        try:
            repo = git.Repo(repo_path)
            
            # Basic repo info
            result = {
                "repo_path": repo_path,
                "is_bare": repo.bare,
                "is_dirty": repo.is_dirty(),
                "active_branch": repo.active_branch.name if not repo.head.is_detached else "HEAD detached",
                "remotes": [remote.name for remote in repo.remotes],
                "branches": {
                    "local": [branch.name for branch in repo.branches],
                    "remote": [ref.name for ref in repo.remote().refs] if repo.remotes else []
                }
            }
            
            # Commit history
            commits = []
            for i, commit in enumerate(repo.iter_commits(max_count=max_commits)):
                commits.append({
                    "sha": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat(),
                    "files_changed": len(commit.stats.files)
                })
            
            result["commits"] = commits
            result["total_commits_analyzed"] = len(commits)
            
            # Repository statistics
            if commits:
                authors = {}
                for commit in commits:
                    author = commit["author"]
                    if author not in authors:
                        authors[author] = 0
                    authors[author] += 1
                
                result["statistics"] = {
                    "unique_authors": len(authors),
                    "top_authors": sorted(authors.items(), key=lambda x: x[1], reverse=True)[:5],
                    "first_commit": commits[-1]["date"] if commits else None,
                    "last_commit": commits[0]["date"] if commits else None
                }
            
            return result
            
        except git.InvalidGitRepositoryError:
            return {"error": f"'{repo_path}' is not a valid Git repository"}
        except Exception as e:
            return {"error": str(e)}


class GitStatusChecker(MCPTool):
    """Check Git repository status and changes."""
    
    @property
    def name(self) -> str:
        return "check_git_status"
    
    @property
    def description(self) -> str:
        return "Check Git repository status including staged, unstaged, and untracked files"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.GIT_OPERATIONS
    
    async def execute(self, repo_path: str) -> Dict[str, Any]:
        """Check Git status."""
        try:
            repo = git.Repo(repo_path)
            
            result = {
                "repo_path": repo_path,
                "is_dirty": repo.is_dirty(),
                "active_branch": repo.active_branch.name if not repo.head.is_detached else "HEAD detached",
                "staged_files": [],
                "unstaged_files": [],
                "untracked_files": list(repo.untracked_files)
            }
            
            # Get staged and unstaged files
            for item in repo.index.diff("HEAD"):
                result["staged_files"].append({
                    "file": item.a_path,
                    "change_type": item.change_type
                })
            
            for item in repo.index.diff(None):
                result["unstaged_files"].append({
                    "file": item.a_path,
                    "change_type": item.change_type
                })
            
            result["summary"] = {
                "staged_count": len(result["staged_files"]),
                "unstaged_count": len(result["unstaged_files"]),
                "untracked_count": len(result["untracked_files"])
            }
            
            return result
            
        except git.InvalidGitRepositoryError:
            return {"error": f"'{repo_path}' is not a valid Git repository"}
        except Exception as e:
            return {"error": str(e)}


# Initialize tools
git_repository_analyzer = GitRepositoryAnalyzer()
git_status_checker = GitStatusChecker() 