"""Databricks destination handler for ETL pipeline."""
import os
import requests
from urllib.parse import urljoin
from databricks.sdk import WorkspaceClient


class DatabricksDestination:
    """
    Handles uploading files to Databricks Unity Catalog volumes.
    """
    
    def __init__(
        self,
        workspace_url: str,
        token: str,
        catalog: str,
        schema: str,
        volume: str
    ):
        """
        Initialize Databricks destination.
        
        Args:
            workspace_url: Databricks workspace URL
            token: Databricks API token
            catalog: Databricks catalog name
            schema: Databricks schema name
            volume: Databricks volume name
        """
        self.workspace_url = workspace_url
        self.token = token
        self.catalog = catalog
        self.schema = schema
        self.volume = volume
        
        # Initialize Databricks client
        self.client = WorkspaceClient(host=workspace_url, token=token)
    
    def upload_file(
        self,
        local_file_path: str,
        databricks_relative_path: str = None,
        overwrite: bool = True
    ) -> bool:
        """
        Upload a file to Databricks Unity Catalog volume.
        
        Args:
            local_file_path: Path to local file to upload
            databricks_relative_path: Relative path in volume (e.g., 'dataset/2026-05-09/file.json')
                                     If not provided, uses filename from local_file_path
            overwrite: Whether to overwrite existing file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify local file exists
            if not os.path.exists(local_file_path):
                raise FileNotFoundError(f"Local file not found: {local_file_path}")
            
            # Construct Databricks path
            if databricks_relative_path is None:
                databricks_relative_path = os.path.basename(local_file_path)
            
            databricks_path = f"/Volumes/{self.catalog}/{self.schema}/{self.volume}/{databricks_relative_path}"
            print(f"Uploading {local_file_path} to {databricks_path}")
            
            # Upload file
            with open(local_file_path, "rb") as f:
                self.client.files.upload(databricks_path, contents=f, overwrite=overwrite)
            
            print(f"Successfully uploaded {local_file_path} to {databricks_path}")
            return True
        
        except Exception as e:
            error_message = f"Error uploading file to Databricks path {databricks_path}: {str(e)}"
            print(error_message)
            return False
    
    def get_databricks_path(self, relative_path: str) -> str:
        """
        Get full Databricks path for a relative path.
        
        Args:
            relative_path: Relative path in volume
            
        Returns:
            Full Databricks path
        """
        return f"/Volumes/{self.catalog}/{self.schema}/{self.volume}/{relative_path}"
