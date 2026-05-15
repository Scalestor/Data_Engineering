"""Base ETL job class for orchestrating data pipeline."""
import time
from datetime import datetime
from typing import Dict, Any, Optional
from core.logging import JSONLogger


class ETLJob:
    """
    Base class for ETL jobs that orchestrates source -> storage -> destination flow.
    """
    
    def __init__(
        self,
        job_name: str,
        source,
        storage,
        destination=None,
        logger: Optional[JSONLogger] = None
    ):
        """
        Initialize ETL job.
        
        Args:
            job_name: Name of the job
            source: Data source (implements fetch method)
            storage: Local storage handler
            destination: Optional destination (implements upload_file method)
            logger: Optional JSON logger instance
        """
        self.job_name = job_name
        self.source = source
        self.storage = storage
        self.destination = destination
        self.logger = logger
        
        self.start_time = None
        self.end_time = None
        self.records_processed = 0
        self.error_message = None
        self.status = "pending"
    
    def run(
        self,
        source_params: Optional[Dict[str, Any]] = None,
        local_filename: str = "data.json",
        storage_partition: str = None,
        databricks_relative_path: str = None,
        overwrite: bool = True
    ) -> bool:
        """
        Execute ETL job: fetch -> store -> upload.
        
        Args:
            source_params: Optional parameters for REST source
            local_filename: Name for local file
            storage_partition: Partition path in local storage
            databricks_relative_path: Relative path for Databricks upload
            overwrite: Whether to overwrite existing file in Databricks
            
        Returns:
            True if successful, False otherwise
        """
        self.start_time = datetime.now()
        self.status = "running"
        
        try:
            # Step 1: Fetch data from source
            print(f"[{self.job_name}] Fetching data from source...")
            if source_params:
                data = self.source.fetch_with_params(source_params)
            else:
                data = self.source.fetch()
            
            # Count records (assuming data is dict or list)
            if isinstance(data, list):
                self.records_processed = len(data)
            elif isinstance(data, dict):
                self.records_processed = len(data)
            else:
                self.records_processed = 1
            
            print(f"[{self.job_name}] Fetched {self.records_processed} records")
            
            # Step 2: Save to local storage
            print(f"[{self.job_name}] Saving data to local storage...")
            local_file_path = self.storage.save_json(
                data,
                local_filename,
                partition_path=storage_partition
            )
            print(f"[{self.job_name}] Saved to {local_file_path}")
            
            # Step 3: Upload to Databricks (if destination configured)
            if self.destination:
                print(f"[{self.job_name}] Uploading to Databricks (overwrite={overwrite})...")
                success = self.destination.upload_file(
                    local_file_path,
                    databricks_relative_path=databricks_relative_path,
                    overwrite=overwrite
                )
                if not success:
                    raise Exception("Failed to upload to Databricks")
            
            self.status = "success"
            self.end_time = datetime.now()
            
            # Log success
            if self.logger:
                self.logger.log_job_completion(
                    job_name=self.job_name,
                    status="success",
                    records_processed=self.records_processed,
                    duration_seconds=(self.end_time - self.start_time).total_seconds(),
                    error_message=None,
                    source_config={"endpoint": str(self.source.endpoint_url)},
                    destination_config={"type": "databricks", "overwrite": overwrite} if self.destination else None
                )
            
            print(f"[{self.job_name}] Job completed successfully")
            return True
        
        except Exception as e:
            self.status = "failed"
            self.error_message = str(e)
            self.end_time = datetime.now()
            
            print(f"[{self.job_name}] Job failed: {str(e)}")
            
            # Log failure
            if self.logger:
                self.logger.log_job_completion(
                    job_name=self.job_name,
                    status="failed",
                    records_processed=self.records_processed,
                    duration_seconds=(self.end_time - self.start_time).total_seconds(),
                    error_message=str(e),
                    source_config={"endpoint": str(self.source.endpoint_url)},
                    destination_config={"type": "databricks", "overwrite": overwrite} if self.destination else None
                )
            
            return False
    
    def get_job_status(self) -> Dict[str, Any]:
        """
        Get current job status.
        
        Returns:
            Dictionary with job status information
        """
        return {
            "job_name": self.job_name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "records_processed": self.records_processed,
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None,
            "error_message": self.error_message
        }
