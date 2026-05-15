"""Job configuration for ETL pipeline."""
from typing import Dict, Any, Optional
import yaml
import os


class JobConfig:
    """
    Manages job configuration for ETL pipelines.
    Configuration can be loaded from YAML files or dictionaries.
    """
    
    def __init__(self):
        """Initialize job configuration."""
        self.config = {}
    
    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load job configuration from YAML file.
        
        Args:
            file_path: Path to YAML configuration file
            
        Returns:
            Configuration dictionary
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        
        return self.config
    
    def load_from_dict(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load job configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Configuration dictionary
        """
        self.config = config_dict
        return self.config
    
    def get_source_config(self) -> Dict[str, Any]:
        """Get source configuration."""
        return self.config.get("source", {})
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration."""
        return self.config.get("storage", {})
    
    def get_destination_config(self) -> Dict[str, Any]:
        """Get destination configuration."""
        return self.config.get("destination", {})
    
    def get_job_name(self) -> str:
        """Get job name."""
        return self.config.get("job_name", "unnamed_job")
    
    def validate(self) -> bool:
        """
        Validate configuration has all required sections.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        required_keys = ["job_name", "source", "storage"]
        
        for key in required_keys:
            if key not in self.config:
                print(f"Missing required configuration: {key}")
                return False
        
        source = self.config["source"]
        if "endpoint_url" not in source:
            print("Missing source.endpoint_url in configuration")
            return False
        
        storage = self.config["storage"]
        if "base_path" not in storage:
            print("Missing storage.base_path in configuration")
            return False
        
        return True
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return str(self.config)
    
    def __repr__(self) -> str:
        """Representation of configuration."""
        return f"JobConfig({self.get_job_name()})"
