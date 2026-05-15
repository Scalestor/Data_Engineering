"""Partition strategy utilities for ETL data paths."""
from datetime import datetime
from typing import Optional


class PartitionStrategy:
    """Handles path partitioning based on strategy."""
    
    STRATEGY_NONE = "none"
    STRATEGY_DAILY = "daily"
    STRATEGY_TIMESTAMP = "timestamp"
    VALID_STRATEGIES = {STRATEGY_NONE, STRATEGY_DAILY, STRATEGY_TIMESTAMP}
    
    @staticmethod
    def apply(base_path: str, strategy: str, filename: Optional[str] = None) -> str:
        """
        Apply partitioning strategy to a base path.
        
        Args:
            base_path: The base directory path
            strategy: Partitioning strategy ('none', 'daily', 'timestamp')
            filename: Optional filename to append after partitioning
            
        Returns:
            Path with partitioning applied
        """
        strategy = strategy.lower()
        
        if strategy == PartitionStrategy.STRATEGY_NONE:
            # No partitioning
            if filename:
                return f"{base_path}/{filename}"
            return base_path
        
        elif strategy == PartitionStrategy.STRATEGY_DAILY:
            # Daily partitioning: YYYY-MM-DD
            date_partition = datetime.now().strftime("%Y-%m-%d")
            if filename:
                return f"{base_path}/{date_partition}/{filename}"
            return f"{base_path}/{date_partition}"
        
        elif strategy == PartitionStrategy.STRATEGY_TIMESTAMP:
            # Timestamp partitioning: YYYY/MM/DD/HHmmss
            ts_partition = datetime.now().strftime("%Y/%m/%d/%H%M%S")
            if filename:
                return f"{base_path}/{ts_partition}/{filename}"
            return f"{base_path}/{ts_partition}"
        
        else:
            # Unknown strategy - default to daily
            print(f"Unknown partition_strategy: {strategy}. Using 'daily'")
            date_partition = datetime.now().strftime("%Y-%m-%d")
            if filename:
                return f"{base_path}/{date_partition}/{filename}"
            return f"{base_path}/{date_partition}"
    
    @staticmethod
    def construct_databricks_path(
        config_path: str,
        partition_strategy: str,
        dataset_name: str,
        job_name: str,
        filename: str
    ) -> str:
        """
        Construct Databricks relative path with partitioning.
        
        Args:
            config_path: Path from job config (may contain base path + filename)
            partition_strategy: Partitioning strategy to apply
            dataset_name: Dataset name (fallback default)
            job_name: Job name (fallback default)
            filename: Filename from job config
            
        Returns:
            Full Databricks relative path with partitioning applied
        """
        if config_path:
            # Extract base path and filename from config
            path_parts = config_path.rsplit("/", 1)
            if len(path_parts) == 2:
                base_path, _ = path_parts
                return PartitionStrategy.apply(base_path, partition_strategy, filename)
            else:
                return PartitionStrategy.apply(config_path, partition_strategy)
        else:
            # Default: construct from dataset_name + job_name
            default_base = f"{dataset_name}/{job_name}"
            return PartitionStrategy.apply(default_base, partition_strategy, filename)
