import os
from dotenv import load_dotenv
from databricks.sdk import WorkspaceClient

# Load environment variables from .env file
load_dotenv()

workspace_url = os.getenv("DATABRICKS_WORKSPACE_URL")
token = os.getenv("DATABRICKS_TOKEN")
catalog = os.getenv("DATABRICKS_CATALOG")
schema = os.getenv("DATABRICKS_SCHEMA")
volume = os.getenv("DATABRICKS_VOLUME")

if not workspace_url or not token:
    raise ValueError("DATABRICKS_WORKSPACE_URL and DATABRICKS_TOKEN must be set in the .env file")

# Initialize Databricks WorkspaceClient
client = WorkspaceClient(host=workspace_url, token=token)


def upload_file_to_databricks(local_file_path: str, 
                              databricks_path: str = None,
                              catalog: str = None,
                              schema: str = None,
                              volume: str = None,
                              workspace_client: WorkspaceClient = None) -> bool:
    """
    Upload a file to Databricks Unity Catalog Volume.
    
    Args:
        local_file_path: Path to the local file to upload
        databricks_path: Full path in Databricks (e.g., /Volumes/catalog/schema/volume/file.json)
                        If not provided, constructs path from catalog/schema/volume parameters
        catalog: Databricks catalog name (used if databricks_path is not provided)
        schema: Databricks schema name (used if databricks_path is not provided)
        volume: Databricks volume name (used if databricks_path is not provided)
        workspace_client: WorkspaceClient instance (uses default if not provided)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use provided client or default
        upload_client = workspace_client if workspace_client else client
        
        # Construct databricks_path if not provided
        if databricks_path is None:
            cat = catalog or globals().get("catalog")
            sch = schema or globals().get("schema")
            vol = volume or globals().get("volume")
            
            if not cat or not sch or not vol:
                raise ValueError("Either databricks_path or catalog/schema/volume parameters must be provided")
            
            # Get filename from local_file_path
            filename = os.path.basename(local_file_path)
            databricks_path = f"/Volumes/{cat}/{sch}/{vol}/{filename}"
        
        # Verify local file exists
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Local file not found: {local_file_path}")
        
        # Upload file
        with open(local_file_path, "rb") as f:
            upload_client.files.upload(databricks_path, contents=f, overwrite=True)
        
        print(f"Successfully uploaded {local_file_path} to {databricks_path}")
        return True
        
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return False


if __name__ == "__main__":
    # Default upload using environment variables
    path = "pegelonline_data/live_pegel/2026-05-09/stations.json"
    local_file_path = f"volumes/raw/{path}"
    
    # Construct full Databricks path
    databricks_path = f"/Volumes/{catalog}/{schema}/{volume}/{path}"
    
    # Upload the file
    success = upload_file_to_databricks(local_file_path, databricks_path)
    
    if not success:
        exit(1)