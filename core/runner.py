"""ETL job runner - main entry point for executing ETL jobs."""
import sys
import os
from typing import Optional
from core.config import JobConfig
from core.storage import LocalStorage
from core.destinations import DatabricksDestination
from core.logging import JSONLogger, LogUploader
from core.etl_job import ETLJob
from core.utils import PartitionStrategy, DatabricksCredentials, SourceFactory, CLIParser


def run_job(
    config_path: str,
    databricks_url: str = None,
    databricks_token: str = None,
    databricks_catalog: str = None,
    databricks_schema: str = None,
    databricks_volume: str = None,
    logs_path: str = "logs"
) -> bool:
    """
    Run an ETL job from configuration file.
    
    Args:
        config_path: Path to job configuration YAML file
        databricks_url: Optional Databricks workspace URL (overrides job config)
        databricks_token: Optional Databricks API token (overrides job config)
        databricks_catalog: Optional Databricks catalog (overrides job config)
        databricks_schema: Optional Databricks schema (overrides job config)
        databricks_volume: Optional Databricks volume (overrides job config)
        logs_path: Path for storing log files
        
    Returns:
        True if job succeeded, False otherwise
    """
    try:
        # Load configuration
        print(f"Loading job configuration from {config_path}")
        config = JobConfig()
        config.load_from_file(config_path)
        
        # Validate configuration
        if not config.validate():
            print("Configuration validation failed")
            return False
        
        job_name = config.get_job_name()
        print(f"Running job: {job_name}")
        
        # Initialize logger
        logger = JSONLogger(logs_path)
        
        # Get configurations
        source_config = config.get_source_config()
        storage_config = config.get_storage_config()
        destination_config = config.get_destination_config()
        
        # Initialize source using factory
        source = SourceFactory.create_rest_source(source_config)
        
        # Initialize storage
        storage_base_path = storage_config.get("base_path", "volumes/raw")
        storage = LocalStorage(storage_base_path)
        
        # Get Databricks credentials from multiple sources
        dest_url, dest_token, dest_catalog, dest_schema, dest_volume = DatabricksCredentials.load_from_sources(
            destination_config,
            cmd_url=databricks_url,
            cmd_token=databricks_token,
            cmd_catalog=databricks_catalog,
            cmd_schema=databricks_schema,
            cmd_volume=databricks_volume
        )
        
        # Validate Databricks credentials
        is_valid, error_msg = DatabricksCredentials.validate(dest_url, dest_token, dest_catalog, dest_schema, dest_volume)
        if not is_valid:
            print(f"Error: {error_msg}")
            status = DatabricksCredentials.get_status_report(dest_url, dest_token, dest_catalog, dest_schema, dest_volume)
            for key, value in status.items():
                print(f"  {key}: {value}")
            return False
        
        # Initialize destination
        destination = DatabricksDestination(
            workspace_url=dest_url,
            token=dest_token,
            catalog=dest_catalog,
            schema=dest_schema,
            volume=dest_volume
        )
        
        # Create and run ETL job
        job = ETLJob(
            job_name=job_name,
            source=source,
            storage=storage,
            destination=destination,
            logger=logger
        )
        
        # Get job parameters
        dataset_name = source_config.get("dataset_name", "default")
        local_filename = source_config.get("filename", "data.json")
        storage_partition = source_config.get("partition")
        
        if storage_partition is None:
            # Use default partition: dataset_name/job_name
            storage_partition = f"{dataset_name}/{job_name}"
        
        # Get partition strategy
        partition_strategy = destination_config.get("partition_strategy", "daily").lower()
        
        # Apply partitioning to storage path
        storage_partition_with_partition = PartitionStrategy.apply(storage_partition, partition_strategy)
        
        # Construct Databricks path with partitioning
        config_path = destination_config.get("databricks_relative_path")
        databricks_relative_path = PartitionStrategy.construct_databricks_path(
            config_path,
            partition_strategy,
            dataset_name,
            job_name,
            local_filename
        )
        
        # Get upload settings
        overwrite = destination_config.get("overwrite", True)
        
        # Execute job
        success = job.run(
            local_filename=local_filename,
            storage_partition=storage_partition_with_partition,
            databricks_relative_path=databricks_relative_path,
            overwrite=overwrite
        )
        
        # Upload logs to Databricks
        if success or destination_config.get("upload_logs_on_failure", True):
            print(f"Uploading logs for job {job_name}")
            log_uploader = LogUploader(destination, logs_path)
            log_uploader.upload_logs(job_name=job_name)
        
        return success
    
    except Exception as e:
        print(f"Error running job: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Parse command-line arguments
    kwargs = CLIParser.parse_args(sys.argv[1:])
    
    # Run job
    success = run_job(**kwargs)
    
    sys.exit(0 if success else 1)
