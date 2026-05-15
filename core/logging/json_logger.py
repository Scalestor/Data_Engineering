"""JSON logger for ETL pipeline operations."""
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional


class JSONLogger:
    """
    Structured JSON logging for ETL operations.
    Writes logs to a central directory for monitoring and analysis.
    """
    
    def __init__(self, logs_directory: str):
        """
        Initialize JSON logger.
        
        Args:
            logs_directory: Directory to store JSON log files
        """
        self.logs_directory = logs_directory
        os.makedirs(logs_directory, exist_ok=True)
    
    def log_job_completion(
        self,
        job_name: str,
        status: str,
        records_processed: int,
        duration_seconds: float,
        error_message: Optional[str] = None,
        source_config: Optional[Dict[str, Any]] = None,
        destination_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log job completion with structured JSON.
        
        Args:
            job_name: Name of the job
            status: Job status ('success' or 'failed')
            records_processed: Number of records processed
            duration_seconds: Job duration in seconds
            error_message: Error message if job failed
            source_config: Source configuration details
            destination_config: Destination configuration details
            
        Returns:
            Path to the log file
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "job_name": job_name,
            "status": status,
            "records_processed": records_processed,
            "duration_seconds": duration_seconds,
            "error_message": error_message,
            "source_config": source_config or {},
            "destination_config": destination_config or {}
        }
        
        # Generate log filename with timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"{job_name}_{timestamp}.json"
        log_path = os.path.join(self.logs_directory, log_filename)
        
        # Write log to file
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
        
        print(f"Log written to {log_path}")
        return log_path
    
    def log_event(
        self,
        event_type: str,
        job_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        level: str = "INFO"
    ) -> str:
        """
        Log an event with structured JSON.
        
        Args:
            event_type: Type of event (e.g., 'fetch_start', 'upload_complete')
            job_name: Name of the job
            message: Event message
            details: Additional event details
            level: Log level (INFO, WARNING, ERROR)
            
        Returns:
            Path to the log file
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "job_name": job_name,
            "level": level,
            "message": message,
            "details": details or {}
        }
        
        # Generate log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        log_filename = f"{job_name}_event_{timestamp}.json"
        log_path = os.path.join(self.logs_directory, log_filename)
        
        # Write log to file
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
        
        return log_path
    
    def get_logs_for_job(self, job_name: str) -> list:
        """
        Get all logs for a specific job.
        
        Args:
            job_name: Name of the job
            
        Returns:
            List of log file paths
        """
        logs = []
        for filename in os.listdir(self.logs_directory):
            if filename.startswith(job_name) and filename.endswith(".json"):
                logs.append(os.path.join(self.logs_directory, filename))
        
        return sorted(logs, reverse=True)  # Most recent first
    
    def get_all_logs(self) -> list:
        """
        Get all log files.
        
        Returns:
            List of all log file paths
        """
        logs = []
        for filename in os.listdir(self.logs_directory):
            if filename.endswith(".json"):
                logs.append(os.path.join(self.logs_directory, filename))
        
        return sorted(logs, reverse=True)  # Most recent first
