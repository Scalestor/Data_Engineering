"""Local storage handler for ETL pipeline."""
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional


class LocalStorage:
    """
    Handles local file storage with flexible partitioning strategies.
    """
    
    def __init__(self, base_path: str):
        """
        Initialize local storage.
        
        Args:
            base_path: Base directory path for storing files
        """
        self.base_path = base_path
    
    def save_json(
        self,
        data: Dict[str, Any],
        filename: str,
        partition_path: str = None,
        ensure_ascii: bool = False,
        indent: int = 2
    ) -> str:
        """
        Save JSON data to local file.
        
        Args:
            data: Data to save
            filename: Name of the file
            partition_path: Optional partition path (e.g., 'YYYY/MM/DD' or 'dataset_name/YYYY-MM-DD')
            ensure_ascii: Whether to escape non-ASCII characters
            indent: JSON indentation level
            
        Returns:
            Full path to saved file
        """
        # Construct full directory path
        if partition_path:
            full_dir = os.path.join(self.base_path, partition_path)
        else:
            full_dir = self.base_path
        
        # Create directory if it doesn't exist
        os.makedirs(full_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(full_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
        
        return file_path
    
    def save_json_with_date_partition(
        self,
        data: Dict[str, Any],
        filename: str,
        dataset_name: str,
        date_format: str = "%Y-%m-%d",
        date_obj: Optional[datetime] = None,
        ensure_ascii: bool = False,
        indent: int = 2
    ) -> str:
        """
        Save JSON data with date-based partitioning.
        
        Args:
            data: Data to save
            filename: Name of the file
            dataset_name: Dataset/source name for partition structure
            date_format: Date format string (default: YYYY-MM-DD)
            date_obj: Date object to use (defaults to current date)
            ensure_ascii: Whether to escape non-ASCII characters
            indent: JSON indentation level
            
        Returns:
            Full path to saved file
        """
        if date_obj is None:
            date_obj = datetime.now()
        
        date_str = date_obj.strftime(date_format)
        partition_path = os.path.join(dataset_name, date_str)
        
        return self.save_json(
            data,
            filename,
            partition_path=partition_path,
            ensure_ascii=ensure_ascii,
            indent=indent
        )
    
    def get_file_size(self, file_path: str) -> int:
        """
        Get file size in bytes.
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in bytes
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return os.path.getsize(file_path)
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.exists(file_path)
    
    def get_partition_directory(
        self,
        dataset_name: str,
        date_obj: Optional[datetime] = None,
        date_format: str = "%Y-%m-%d"
    ) -> str:
        """
        Get full partition directory path.
        
        Args:
            dataset_name: Dataset/source name
            date_obj: Date object (defaults to current date)
            date_format: Date format string
            
        Returns:
            Full partition directory path
        """
        if date_obj is None:
            date_obj = datetime.now()
        
        date_str = date_obj.strftime(date_format)
        return os.path.join(self.base_path, dataset_name, date_str)
