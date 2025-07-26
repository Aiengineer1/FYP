"""
File utilities for AI solutions
Common file operations and path management
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

class FileUtils:
    """Utility class for file operations"""
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> bool:
        """Ensure a directory exists, create if it doesn't"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False
    
    @staticmethod
    def safe_save_json(data: Dict, filepath: Union[str, Path], indent: int = 2) -> bool:
        """Safely save JSON data to file with error handling"""
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, default=str)
            return True
        except Exception as e:
            print(f"Error saving JSON to {filepath}: {e}")
            return False
    
    @staticmethod
    def safe_load_json(filepath: Union[str, Path]) -> Optional[Dict]:
        """Safely load JSON data from file with error handling"""
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                print(f"File not found: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {filepath}: {e}")
            return None
    
    @staticmethod
    def get_file_size_mb(filepath: Union[str, Path]) -> float:
        """Get file size in megabytes"""
        try:
            filepath = Path(filepath)
            if filepath.exists():
                return filepath.stat().st_size / (1024 * 1024)
            return 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def backup_file(filepath: Union[str, Path], backup_suffix: str = None) -> Optional[Path]:
        """Create a backup of a file"""
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                return None
            
            if backup_suffix is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_suffix = f"backup_{timestamp}"
            
            backup_path = filepath.with_suffix(f".{backup_suffix}{filepath.suffix}")
            shutil.copy2(filepath, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error creating backup of {filepath}: {e}")
            return None
    
    @staticmethod
    def clean_directory(directory: Union[str, Path], pattern: str = "*", 
                       max_age_days: int = None) -> int:
        """Clean files from directory based on pattern and age"""
        try:
            directory = Path(directory)
            if not directory.exists():
                return 0
            
            deleted_count = 0
            current_time = datetime.now()
            
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    should_delete = False
                    
                    if max_age_days is not None:
                        file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_age.days > max_age_days:
                            should_delete = True
                    else:
                        should_delete = True
                    
                    if should_delete:
                        file_path.unlink()
                        deleted_count += 1
            
            return deleted_count
        except Exception as e:
            print(f"Error cleaning directory {directory}: {e}")
            return 0
    
    @staticmethod
    def find_files_by_extension(directory: Union[str, Path], extensions: List[str]) -> List[Path]:
        """Find files with specific extensions in directory"""
        try:
            directory = Path(directory)
            if not directory.exists():
                return []
            
            found_files = []
            for ext in extensions:
                found_files.extend(directory.glob(f"*{ext}"))
            
            return found_files
        except Exception as e:
            print(f"Error finding files in {directory}: {e}")
            return []
    
    @staticmethod
    def get_directory_size_mb(directory: Union[str, Path]) -> float:
        """Get total size of directory in megabytes"""
        try:
            directory = Path(directory)
            if not directory.exists():
                return 0.0
            
            total_size = 0
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size / (1024 * 1024)
        except Exception as e:
            print(f"Error calculating directory size for {directory}: {e}")
            return 0.0 