"""Data validation utilities for ETL pipeline."""
import os
from typing import Any, Dict


def validate_response(data: Any) -> bool:
    """
    Validate REST API response.
    
    Args:
        data: Data to validate
        
    Returns:
        True if response is valid (not empty), False otherwise
    """
    if data is None:
        return False
    
    if isinstance(data, dict) and len(data) == 0:
        return False
    
    if isinstance(data, list) and len(data) == 0:
        return False
    
    return True


def validate_file(file_path: str) -> bool:
    """
    Validate that file exists and is readable.
    
    Args:
        file_path: Path to file to validate
        
    Returns:
        True if file exists and is readable, False otherwise
    """
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        if not os.access(file_path, os.R_OK):
            print(f"File is not readable: {file_path}")
            return False
        
        # Try to read a small portion of the file
        with open(file_path, "r", encoding="utf-8") as f:
            f.read(1)
        
        return True
    
    except Exception as e:
        print(f"Error validating file {file_path}: {str(e)}")
        return False


def validate_databricks_config(config: Dict[str, str]) -> bool:
    """
    Validate Databricks configuration.
    
    Args:
        config: Databricks configuration dictionary with keys:
               - workspace_url, token, catalog, schema, volume
        
    Returns:
        True if all required fields are present, False otherwise
    """
    required_keys = ["workspace_url", "token", "catalog", "schema", "volume"]
    
    for key in required_keys:
        if key not in config or not config[key]:
            print(f"Missing or empty Databricks config: {key}")
            return False
    
    return True
