"""Log cleanup utility for ETL pipeline."""
import os
from datetime import datetime, timedelta
from typing import Dict


class LogCleanup:
    """
    Manages cleanup of old log files based on retention policy.
    """
    
    def __init__(self, logs_directory: str, retention_days: int):
        """
        Initialize log cleanup.
        
        Args:
            logs_directory: Directory containing log files
            retention_days: Number of days to retain logs
        """
        self.logs_directory = logs_directory
        self.retention_days = retention_days
    
    def cleanup(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Delete logs older than retention period.
        
        Args:
            dry_run: If True, only report what would be deleted without deleting
            
        Returns:
            Dictionary with cleanup statistics
        """
        if not os.path.exists(self.logs_directory):
            print(f"Logs directory not found: {self.logs_directory}")
            return {"deleted": 0, "failed": 0, "total_checked": 0}
        
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        failed_count = 0
        total_checked = 0
        
        print(f"Starting log cleanup with retention period: {self.retention_days} days")
        print(f"Cutoff date: {cutoff_date.isoformat()}")
        
        for filename in os.listdir(self.logs_directory):
            if not filename.endswith(".json"):
                continue
            
            total_checked += 1
            file_path = os.path.join(self.logs_directory, filename)
            
            # Get file modification time
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_mtime < cutoff_date:
                if dry_run:
                    print(f"[DRY RUN] Would delete: {filename} (modified: {file_mtime.isoformat()})")
                    deleted_count += 1
                else:
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {filename} (modified: {file_mtime.isoformat()})")
                        deleted_count += 1
                    except Exception as e:
                        print(f"Failed to delete {filename}: {str(e)}")
                        failed_count += 1
        
        result = {
            "deleted": deleted_count if not dry_run else 0,
            "failed": failed_count,
            "total_checked": total_checked,
            "dry_run": dry_run
        }
        
        print(f"Cleanup complete: {result}")
        return result
