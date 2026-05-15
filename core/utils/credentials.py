"""Databricks credentials management and validation."""
import os
from typing import Dict, Tuple


class DatabricksCredentials:
    """Handles loading and validating Databricks credentials."""
    
    @staticmethod
    def load_from_sources(
        config_dict: Dict,
        cmd_url: str = None,
        cmd_token: str = None,
        cmd_catalog: str = None,
        cmd_schema: str = None,
        cmd_volume: str = None
    ) -> Tuple[str, str, str, str, str]:
        """
        Load Databricks credentials from multiple sources with priority order.
        
        Priority:
        1. Command-line arguments (highest priority)
        2. Environment variables
        3. Job configuration (lowest priority, only catalog/schema/volume)
        
        Args:
            config_dict: Destination config from job YAML
            cmd_url: Workspace URL from CLI args
            cmd_token: Token from CLI args
            cmd_catalog: Catalog from CLI args
            cmd_schema: Schema from CLI args
            cmd_volume: Volume from CLI args
            
        Returns:
            Tuple of (workspace_url, token, catalog, schema, volume)
        """
        # Workspace URL and Token - only from CLI args or environment
        workspace_url = cmd_url or os.getenv("DATABRICKS_WORKSPACE_URL")
        token = cmd_token or os.getenv("DATABRICKS_TOKEN")
        
        # Catalog, Schema, Volume - priority: CLI args > job config > env vars
        catalog = cmd_catalog or config_dict.get("catalog") or os.getenv("DATABRICKS_CATALOG")
        schema = cmd_schema or config_dict.get("schema") or os.getenv("DATABRICKS_SCHEMA")
        volume = cmd_volume or config_dict.get("volume") or os.getenv("DATABRICKS_VOLUME")
        
        return workspace_url, token, catalog, schema, volume
    
    @staticmethod
    def validate(workspace_url: str, token: str, catalog: str, schema: str, volume: str) -> Tuple[bool, str]:
        """
        Validate Databricks credentials are complete.
        
        Args:
            workspace_url: Databricks workspace URL
            token: Databricks API token
            catalog: Databricks catalog name
            schema: Databricks schema name
            volume: Databricks volume name
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        missing = []
        
        if not workspace_url:
            missing.append("workspace_url")
        if not token:
            missing.append("token")
        if not catalog:
            missing.append("catalog")
        if not schema:
            missing.append("schema")
        if not volume:
            missing.append("volume")
        
        if missing:
            error_msg = f"Missing Databricks configuration: {', '.join(missing)}"
            return False, error_msg
        
        return True, ""
    
    @staticmethod
    def get_status_report(workspace_url: str, token: str, catalog: str, schema: str, volume: str) -> Dict[str, bool]:
        """
        Get status report of each credential component.
        
        Args:
            workspace_url: Databricks workspace URL
            token: Databricks API token
            catalog: Databricks catalog name
            schema: Databricks schema name
            volume: Databricks volume name
            
        Returns:
            Dictionary with status of each credential
        """
        return {
            "workspace_url": bool(workspace_url),
            "token": bool(token),
            "catalog": bool(catalog),
            "schema": bool(schema),
            "volume": bool(volume)
        }
