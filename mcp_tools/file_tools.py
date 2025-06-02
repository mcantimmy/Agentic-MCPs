from pathlib import Path
from typing import List, Optional, Union
import json
import shutil

def read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """Read the contents of a file."""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {str(e)}")

def write_file(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
    """Write content to a file."""
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise Exception(f"Error writing to file {file_path}: {str(e)}")

def delete_file(file_path: Union[str, Path]) -> None:
    """Delete a file."""
    try:
        Path(file_path).unlink()
    except Exception as e:
        raise Exception(f"Error deleting file {file_path}: {str(e)}")

def list_directory(dir_path: Union[str, Path], pattern: str = "*") -> List[str]:
    """List files in a directory matching the given pattern."""
    try:
        return [str(p) for p in Path(dir_path).glob(pattern)]
    except Exception as e:
        raise Exception(f"Error listing directory {dir_path}: {str(e)}")

def create_directory(dir_path: Union[str, Path]) -> None:
    """Create a directory if it doesn't exist."""
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise Exception(f"Error creating directory {dir_path}: {str(e)}")

def delete_directory(dir_path: Union[str, Path]) -> None:
    """Delete a directory and all its contents."""
    try:
        shutil.rmtree(dir_path)
    except Exception as e:
        raise Exception(f"Error deleting directory {dir_path}: {str(e)}")

def read_json(file_path: Union[str, Path]) -> dict:
    """Read and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error reading JSON file {file_path}: {str(e)}")

def write_json(file_path: Union[str, Path], data: dict) -> None:
    """Write data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise Exception(f"Error writing JSON file {file_path}: {str(e)}") 