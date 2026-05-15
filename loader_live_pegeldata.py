"""Example ETL job using the framework directly."""
import os
from datetime import datetime
from dotenv import load_dotenv
from core.sources import RESTSource
from core.storage import LocalStorage
from core.destinations import DatabricksDestination
from core.logging import JSONLogger, LogUploader
from core.etl_job import ETLJob

# Load environment variables
load_dotenv()

# REST endpoint URL
url = "https://pegelonline.wsv.de/webservices/rest-api/v2/stations.json?includeTimeseries=true"

# Get configuration from environment
databricks_url = os.getenv("DATABRICKS_WORKSPACE_URL")
databricks_token = os.getenv("DATABRICKS_TOKEN")
databricks_catalog = os.getenv("DATABRICKS_CATALOG")
databricks_schema = os.getenv("DATABRICKS_SCHEMA")
databricks_volume = os.getenv("DATABRICKS_VOLUME")
logs_path = os.getenv("LOGS_PATH", "logs")

# Initialize components
source = RESTSource(endpoint_url=url)
storage = LocalStorage("volumes/raw")
destination = DatabricksDestination(
    workspace_url=databricks_url,
    token=databricks_token,
    catalog=databricks_catalog,
    schema=databricks_schema,
    volume=databricks_volume
)

# Initialize logger
logger = JSONLogger(logs_path)

# Create and run ETL job
job = ETLJob(
    job_name="pegel_live",
    source=source,
    storage=storage,
    destination=destination,
    logger=logger
)

# Execute job with date-based partitioning
today = datetime.now().strftime("%Y-%m-%d")
success = job.run(
    local_filename="stations.json",
    storage_partition=f"pegelonline_data/live_pegel/{today}",
    databricks_relative_path=f"pegelonline_data/live_pegel/{today}/stations.json"
)

# Upload logs to Databricks
if success or True:  # Upload logs regardless of success/failure
    log_uploader = LogUploader(destination, logs_path)
    log_uploader.upload_logs(job_name="pegel_live")

exit(0 if success else 1)