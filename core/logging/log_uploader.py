"""Log uploader for pushing logs to Databricks."""
import os
import json
from typing import Optional
from datetime import datetime


class LogUploader:
    """
    Uploads log files to Databricks for centralized monitoring and analytics.
    Logs are stored with daily partitioning by default.
    """
    
    def __init__(
        self,
        databricks_destination,
        logs_directory: str,
        table_name: str = "etl_logs"
    ):
        """
        Initialize log uploader.
        
        Args:
            databricks_destination: DatabricksDestination instance
            logs_directory: Directory containing local log files
            table_name: Name of the table in Databricks (relative path in volume)
        """
        self.destination = databricks_destination
        self.logs_directory = logs_directory
        self.table_name = table_name
        self.uploaded_logs = []
    
    def upload_logs(self, job_name: Optional[str] = None) -> bool:
        """
        Upload log files to Databricks with daily partitioning.
        
        Args:
            job_name: Optional job name to upload logs only for that job
            
        Returns:
            True if all logs uploaded successfully, False otherwise
        """
        if not os.path.exists(self.logs_directory):
            print(f"Logs directory not found: {self.logs_directory}")
            return False
        
        # Collect logs to upload
        logs_to_upload = []
        for filename in os.listdir(self.logs_directory):
            if not filename.endswith(".json"):
                continue
            
            if job_name and not filename.startswith(job_name):
                continue
            
            logs_to_upload.append(filename)
        
        if not logs_to_upload:
            print(f"No logs found to upload")
            return True
        
        print(f"Uploading {len(logs_to_upload)} log files to Databricks (daily partitioning)")
        transferred_dir = os.path.join(self.logs_directory, "transferred")
        os.makedirs(transferred_dir, exist_ok=True)
        
        success_count = 0
        for filename in logs_to_upload:
            local_file_path = os.path.join(self.logs_directory, filename)
            
            # Construct Databricks path with daily partitioning: logs_table/YYYY/MM/DD/filename
            now = datetime.now()
            databricks_relative_path = f"{self.table_name}/{now.year}/{now.month:02d}/{now.day:02d}/{filename}"
            
            try:
                success = self.destination.upload_file(
                    local_file_path,
                    databricks_relative_path=databricks_relative_path,
                    overwrite=True
                )
                
                if success:
                    self.uploaded_logs.append(filename)
                    success_count += 1
                    transferred_path = os.path.join(transferred_dir, filename)
                    os.replace(local_file_path, transferred_path)
                else:
                    print(f"Failed to upload log: {filename}")
            
            except Exception as e:
                print(f"Error uploading log {filename}: {str(e)}")
        
        print(f"Successfully uploaded {success_count}/{len(logs_to_upload)} logs")
        return success_count == len(logs_to_upload)
    
    def get_uploaded_logs(self) -> list:
        """
        Get list of successfully uploaded log files.
        
        Returns:
            List of uploaded log filenames
        """
        return self.uploaded_logs
