"""
File operations MCP tools for advanced file manipulation, search, and monitoring.
"""

import os
import shutil
import glob
import fnmatch
import hashlib
import mimetypes
import json
from typing import Dict, List, Any, Optional, Generator
from pathlib import Path
import re
from datetime import datetime
import stat

from .base import MCPTool, ToolCategory


class AdvancedFileSearch(MCPTool):
    """Advanced file search with multiple criteria and filters."""
    
    @property
    def name(self) -> str:
        return "advanced_file_search"
    
    @property
    def description(self) -> str:
        return "Search for files using multiple criteria including name patterns, content, size, date, and file type"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE_OPERATIONS
    
    async def execute(self, 
                     directory: str,
                     name_pattern: Optional[str] = None,
                     content_pattern: Optional[str] = None,
                     file_type: Optional[str] = None,
                     min_size: Optional[int] = None,
                     max_size: Optional[int] = None,
                     modified_after: Optional[str] = None,
                     modified_before: Optional[str] = None,
                     recursive: bool = True,
                     case_sensitive: bool = False) -> Dict[str, Any]:
        """Search for files with advanced criteria."""
        try:
            results = []
            search_path = Path(directory)
            
            if not search_path.exists():
                return {"error": f"Directory '{directory}' does not exist"}
            
            pattern = "**/*" if recursive else "*"
            
            for file_path in search_path.glob(pattern):
                if not file_path.is_file():
                    continue
                
                # Apply filters
                if not self._matches_criteria(file_path, name_pattern, content_pattern, 
                                            file_type, min_size, max_size, 
                                            modified_after, modified_before, case_sensitive):
                    continue
                
                file_info = self._get_file_info(file_path)
                results.append(file_info)
            
            return {
                "directory": directory,
                "total_files": len(results),
                "files": results
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _matches_criteria(self, file_path: Path, name_pattern, content_pattern, 
                         file_type, min_size, max_size, modified_after, 
                         modified_before, case_sensitive) -> bool:
        """Check if file matches all criteria."""
        
        # Name pattern
        if name_pattern:
            name = file_path.name if case_sensitive else file_path.name.lower()
            pattern = name_pattern if case_sensitive else name_pattern.lower()
            if not fnmatch.fnmatch(name, pattern):
                return False
        
        # File type
        if file_type:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type or not mime_type.startswith(file_type):
                return False
        
        # Size filters
        try:
            size = file_path.stat().st_size
            if min_size and size < min_size:
                return False
            if max_size and size > max_size:
                return False
        except OSError:
            return False
        
        # Date filters
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if modified_after:
                after_date = datetime.fromisoformat(modified_after)
                if mtime < after_date:
                    return False
            if modified_before:
                before_date = datetime.fromisoformat(modified_before)
                if mtime > before_date:
                    return False
        except (OSError, ValueError):
            return False
        
        # Content pattern
        if content_pattern:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if case_sensitive:
                        if content_pattern not in content:
                            return False
                    else:
                        if content_pattern.lower() not in content.lower():
                            return False
            except (OSError, UnicodeDecodeError):
                return False
        
        return True
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get detailed file information."""
        try:
            stat_info = file_path.stat()
            return {
                "path": str(file_path),
                "name": file_path.name,
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "extension": file_path.suffix,
                "mime_type": mimetypes.guess_type(str(file_path))[0],
                "permissions": oct(stat_info.st_mode)[-3:]
            }
        except OSError as e:
            return {"path": str(file_path), "error": str(e)}


class FileContentAnalyzer(MCPTool):
    """Analyze file content including encoding, line counts, and statistics."""
    
    @property
    def name(self) -> str:
        return "analyze_file_content"
    
    @property
    def description(self) -> str:
        return "Analyze file content including encoding detection, line counts, character statistics, and content type"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE_OPERATIONS
    
    async def execute(self, file_path: str) -> Dict[str, Any]:
        """Analyze file content."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File '{file_path}' does not exist"}
            
            result = {
                "file_path": file_path,
                "size": path.stat().st_size,
                "mime_type": mimetypes.guess_type(file_path)[0]
            }
            
            # Try to read as text
            try:
                with open(path, 'rb') as f:
                    raw_content = f.read()
                
                # Detect encoding
                encoding = self._detect_encoding(raw_content)
                result["encoding"] = encoding
                
                # Decode content
                content = raw_content.decode(encoding, errors='ignore')
                
                # Text analysis
                lines = content.splitlines()
                result.update({
                    "total_lines": len(lines),
                    "non_empty_lines": len([line for line in lines if line.strip()]),
                    "total_characters": len(content),
                    "total_words": len(content.split()),
                    "line_endings": self._detect_line_endings(raw_content),
                    "has_bom": raw_content.startswith(b'\xef\xbb\xbf'),
                    "longest_line": max(len(line) for line in lines) if lines else 0,
                    "average_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0
                })
                
                # Language detection for code files
                if path.suffix in ['.py', '.js', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go']:
                    result["language"] = self._detect_language(path.suffix)
                    result["code_analysis"] = self._analyze_code_content(content, path.suffix)
                
            except UnicodeDecodeError:
                result["is_binary"] = True
                result["file_hash"] = hashlib.md5(raw_content).hexdigest()
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def _detect_encoding(self, raw_content: bytes) -> str:
        """Simple encoding detection."""
        # Check for BOM
        if raw_content.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig'
        if raw_content.startswith(b'\xff\xfe'):
            return 'utf-16-le'
        if raw_content.startswith(b'\xfe\xff'):
            return 'utf-16-be'
        
        # Try common encodings
        for encoding in ['utf-8', 'ascii', 'latin-1', 'cp1252']:
            try:
                raw_content.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue
        
        return 'utf-8'  # Default fallback
    
    def _detect_line_endings(self, raw_content: bytes) -> str:
        """Detect line ending style."""
        if b'\r\n' in raw_content:
            return 'CRLF (Windows)'
        elif b'\n' in raw_content:
            return 'LF (Unix/Linux)'
        elif b'\r' in raw_content:
            return 'CR (Classic Mac)'
        else:
            return 'None detected'
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from extension."""
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go'
        }
        return lang_map.get(extension, 'Unknown')
    
    def _analyze_code_content(self, content: str, extension: str) -> Dict[str, Any]:
        """Basic code content analysis."""
        lines = content.splitlines()
        
        comment_patterns = {
            '.py': r'^\s*#',
            '.js': r'^\s*//',
            '.java': r'^\s*//',
            '.cpp': r'^\s*//',
            '.c': r'^\s*//',
            '.cs': r'^\s*//',
            '.php': r'^\s*//',
            '.rb': r'^\s*#',
            '.go': r'^\s*//'
        }
        
        pattern = comment_patterns.get(extension, r'^\s*#')
        comment_lines = len([line for line in lines if re.match(pattern, line)])
        
        return {
            "comment_lines": comment_lines,
            "code_lines": len(lines) - comment_lines - len([line for line in lines if not line.strip()]),
            "comment_ratio": comment_lines / len(lines) if lines else 0
        }


class BatchFileOperations(MCPTool):
    """Perform batch operations on multiple files."""
    
    @property
    def name(self) -> str:
        return "batch_file_operations"
    
    @property
    def description(self) -> str:
        return "Perform batch operations like rename, copy, move, or delete on multiple files matching criteria"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE_OPERATIONS
    
    async def execute(self, 
                     directory: str,
                     operation: str,
                     pattern: str = "*",
                     destination: Optional[str] = None,
                     rename_pattern: Optional[str] = None,
                     dry_run: bool = True) -> Dict[str, Any]:
        """Perform batch file operations."""
        try:
            if operation not in ['copy', 'move', 'delete', 'rename']:
                return {"error": f"Invalid operation: {operation}"}
            
            source_path = Path(directory)
            if not source_path.exists():
                return {"error": f"Directory '{directory}' does not exist"}
            
            files = list(source_path.glob(pattern))
            files = [f for f in files if f.is_file()]
            
            results = []
            errors = []
            
            for file_path in files:
                try:
                    if operation == 'delete':
                        result = self._delete_file(file_path, dry_run)
                    elif operation == 'copy':
                        if not destination:
                            errors.append(f"Destination required for copy operation")
                            continue
                        result = self._copy_file(file_path, destination, dry_run)
                    elif operation == 'move':
                        if not destination:
                            errors.append(f"Destination required for move operation")
                            continue
                        result = self._move_file(file_path, destination, dry_run)
                    elif operation == 'rename':
                        if not rename_pattern:
                            errors.append(f"Rename pattern required for rename operation")
                            continue
                        result = self._rename_file(file_path, rename_pattern, dry_run)
                    
                    results.append(result)
                    
                except Exception as e:
                    errors.append(f"Error processing {file_path}: {str(e)}")
            
            return {
                "operation": operation,
                "total_files": len(files),
                "successful": len(results),
                "errors": len(errors),
                "dry_run": dry_run,
                "results": results,
                "error_details": errors
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _delete_file(self, file_path: Path, dry_run: bool) -> Dict[str, Any]:
        """Delete a file."""
        if not dry_run:
            file_path.unlink()
        return {
            "operation": "delete",
            "source": str(file_path),
            "status": "would delete" if dry_run else "deleted"
        }
    
    def _copy_file(self, file_path: Path, destination: str, dry_run: bool) -> Dict[str, Any]:
        """Copy a file."""
        dest_path = Path(destination) / file_path.name
        if not dry_run:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_path)
        return {
            "operation": "copy",
            "source": str(file_path),
            "destination": str(dest_path),
            "status": "would copy" if dry_run else "copied"
        }
    
    def _move_file(self, file_path: Path, destination: str, dry_run: bool) -> Dict[str, Any]:
        """Move a file."""
        dest_path = Path(destination) / file_path.name
        if not dry_run:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(file_path, dest_path)
        return {
            "operation": "move",
            "source": str(file_path),
            "destination": str(dest_path),
            "status": "would move" if dry_run else "moved"
        }
    
    def _rename_file(self, file_path: Path, pattern: str, dry_run: bool) -> Dict[str, Any]:
        """Rename a file using a pattern."""
        # Simple pattern replacement: {name} -> original name, {ext} -> extension
        new_name = pattern.replace('{name}', file_path.stem).replace('{ext}', file_path.suffix)
        new_path = file_path.parent / new_name
        
        if not dry_run:
            file_path.rename(new_path)
        
        return {
            "operation": "rename",
            "source": str(file_path),
            "destination": str(new_path),
            "status": "would rename" if dry_run else "renamed"
        }


class FileComparison(MCPTool):
    """Compare files for differences, similarities, and duplicates."""
    
    @property
    def name(self) -> str:
        return "compare_files"
    
    @property
    def description(self) -> str:
        return "Compare files for differences, calculate similarity, and detect duplicates using various methods"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE_OPERATIONS
    
    async def execute(self, 
                     file1: str,
                     file2: str,
                     comparison_type: str = "content") -> Dict[str, Any]:
        """Compare two files."""
        try:
            path1 = Path(file1)
            path2 = Path(file2)
            
            if not path1.exists():
                return {"error": f"File '{file1}' does not exist"}
            if not path2.exists():
                return {"error": f"File '{file2}' does not exist"}
            
            result = {
                "file1": file1,
                "file2": file2,
                "comparison_type": comparison_type
            }
            
            if comparison_type == "hash":
                result.update(self._compare_by_hash(path1, path2))
            elif comparison_type == "size":
                result.update(self._compare_by_size(path1, path2))
            elif comparison_type == "content":
                result.update(self._compare_by_content(path1, path2))
            elif comparison_type == "metadata":
                result.update(self._compare_metadata(path1, path2))
            else:
                return {"error": f"Invalid comparison type: {comparison_type}"}
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def _compare_by_hash(self, path1: Path, path2: Path) -> Dict[str, Any]:
        """Compare files by hash."""
        hash1 = self._calculate_hash(path1)
        hash2 = self._calculate_hash(path2)
        
        return {
            "hash1": hash1,
            "hash2": hash2,
            "identical": hash1 == hash2
        }
    
    def _compare_by_size(self, path1: Path, path2: Path) -> Dict[str, Any]:
        """Compare files by size."""
        size1 = path1.stat().st_size
        size2 = path2.stat().st_size
        
        return {
            "size1": size1,
            "size2": size2,
            "size_difference": abs(size1 - size2),
            "identical_size": size1 == size2
        }
    
    def _compare_by_content(self, path1: Path, path2: Path) -> Dict[str, Any]:
        """Compare files by content."""
        try:
            with open(path1, 'r', encoding='utf-8') as f1, open(path2, 'r', encoding='utf-8') as f2:
                content1 = f1.read()
                content2 = f2.read()
            
            # Calculate similarity
            similarity = self._calculate_text_similarity(content1, content2)
            
            return {
                "identical_content": content1 == content2,
                "similarity_ratio": similarity,
                "length1": len(content1),
                "length2": len(content2)
            }
        except UnicodeDecodeError:
            # Binary comparison
            with open(path1, 'rb') as f1, open(path2, 'rb') as f2:
                content1 = f1.read()
                content2 = f2.read()
            
            return {
                "identical_content": content1 == content2,
                "binary_files": True
            }
    
    def _compare_metadata(self, path1: Path, path2: Path) -> Dict[str, Any]:
        """Compare file metadata."""
        stat1 = path1.stat()
        stat2 = path2.stat()
        
        return {
            "size_match": stat1.st_size == stat2.st_size,
            "mtime_match": stat1.st_mtime == stat2.st_mtime,
            "permissions_match": stat.filemode(stat1.st_mode) == stat.filemode(stat2.st_mode),
            "metadata1": {
                "size": stat1.st_size,
                "modified": datetime.fromtimestamp(stat1.st_mtime).isoformat(),
                "permissions": stat.filemode(stat1.st_mode)
            },
            "metadata2": {
                "size": stat2.st_size,
                "modified": datetime.fromtimestamp(stat2.st_mtime).isoformat(),
                "permissions": stat.filemode(stat2.st_mode)
            }
        }
    
    def _calculate_hash(self, path: Path) -> str:
        """Calculate MD5 hash of file."""
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity ratio."""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        # Simple character-based similarity
        longer = text1 if len(text1) > len(text2) else text2
        shorter = text2 if len(text1) > len(text2) else text1
        
        if len(longer) == 0:
            return 1.0
        
        matches = sum(1 for i, char in enumerate(shorter) if i < len(longer) and char == longer[i])
        return matches / len(longer)


class DirectoryAnalyzer(MCPTool):
    """Analyze directory structure, size, and file distribution."""
    
    @property
    def name(self) -> str:
        return "analyze_directory"
    
    @property
    def description(self) -> str:
        return "Analyze directory structure including size distribution, file types, and directory statistics"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE_OPERATIONS
    
    async def execute(self, 
                     directory: str,
                     max_depth: int = 3,
                     include_hidden: bool = False) -> Dict[str, Any]:
        """Analyze directory structure."""
        try:
            path = Path(directory)
            if not path.exists():
                return {"error": f"Directory '{directory}' does not exist"}
            
            if not path.is_dir():
                return {"error": f"'{directory}' is not a directory"}
            
            analysis = {
                "directory": directory,
                "total_size": 0,
                "file_count": 0,
                "directory_count": 0,
                "file_types": {},
                "size_distribution": {},
                "largest_files": [],
                "directory_tree": {}
            }
            
            # Analyze directory
            for item in self._walk_directory(path, max_depth, include_hidden):
                if item["type"] == "file":
                    analysis["file_count"] += 1
                    analysis["total_size"] += item["size"]
                    
                    # File type analysis
                    ext = item["extension"].lower()
                    if ext not in analysis["file_types"]:
                        analysis["file_types"][ext] = {"count": 0, "size": 0}
                    analysis["file_types"][ext]["count"] += 1
                    analysis["file_types"][ext]["size"] += item["size"]
                    
                    # Track largest files
                    analysis["largest_files"].append({
                        "path": item["path"],
                        "size": item["size"]
                    })
                
                elif item["type"] == "directory":
                    analysis["directory_count"] += 1
            
            # Sort largest files
            analysis["largest_files"].sort(key=lambda x: x["size"], reverse=True)
            analysis["largest_files"] = analysis["largest_files"][:10]  # Top 10
            
            # Size distribution
            analysis["size_distribution"] = self._calculate_size_distribution(analysis["file_types"])
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _walk_directory(self, path: Path, max_depth: int, include_hidden: bool, current_depth: int = 0):
        """Walk directory tree with depth limit."""
        if current_depth > max_depth:
            return
        
        try:
            for item in path.iterdir():
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                if item.is_file():
                    try:
                        stat_info = item.stat()
                        yield {
                            "type": "file",
                            "path": str(item),
                            "name": item.name,
                            "size": stat_info.st_size,
                            "extension": item.suffix,
                            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                        }
                    except OSError:
                        continue
                
                elif item.is_dir():
                    yield {
                        "type": "directory",
                        "path": str(item),
                        "name": item.name
                    }
                    
                    # Recurse into subdirectory
                    yield from self._walk_directory(item, max_depth, include_hidden, current_depth + 1)
        
        except PermissionError:
            pass
    
    def _calculate_size_distribution(self, file_types: Dict) -> Dict[str, float]:
        """Calculate size distribution by file type."""
        total_size = sum(info["size"] for info in file_types.values())
        if total_size == 0:
            return {}
        
        return {
            ext: (info["size"] / total_size) * 100
            for ext, info in file_types.items()
        }


# Initialize tools
advanced_file_search = AdvancedFileSearch()
file_content_analyzer = FileContentAnalyzer()
batch_file_operations = BatchFileOperations()
file_comparison = FileComparison()
directory_analyzer = DirectoryAnalyzer() 