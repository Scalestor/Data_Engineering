"""Command-line argument parsing for ETL runner."""
import os
import sys
from typing import Dict


class CLIParser:
    """Parses command-line arguments for the ETL runner."""
    
    @staticmethod
    def parse_args(args: list) -> Dict[str, str]:
        """
        Parse command-line arguments.
        
        Usage:
            python runner.py <config_path> [--databricks-url URL] [--databricks-token TOKEN]
                           [--databricks-catalog CATALOG] [--databricks-schema SCHEMA]
                           [--databricks-volume VOLUME] [--logs-path PATH]
        
        Args:
            args: sys.argv[1:] - command-line arguments excluding script name
            
        Returns:
            Dictionary of parsed arguments with defaults applied
            
        Raises:
            SystemExit: If config_path is not provided
        """
        if not args:
            CLIParser._print_usage()
            sys.exit(1)
        
        kwargs = {
            'config_path': args[0],
            'logs_path': os.getenv("LOGS_PATH", "logs")
        }
        
        i = 1
        while i < len(args):
            arg = args[i]
            
            if arg == '--databricks-url' and i + 1 < len(args):
                kwargs['databricks_url'] = args[i + 1]
                i += 2
            elif arg == '--databricks-token' and i + 1 < len(args):
                kwargs['databricks_token'] = args[i + 1]
                i += 2
            elif arg == '--databricks-catalog' and i + 1 < len(args):
                kwargs['databricks_catalog'] = args[i + 1]
                i += 2
            elif arg == '--databricks-schema' and i + 1 < len(args):
                kwargs['databricks_schema'] = args[i + 1]
                i += 2
            elif arg == '--databricks-volume' and i + 1 < len(args):
                kwargs['databricks_volume'] = args[i + 1]
                i += 2
            elif arg == '--logs-path' and i + 1 < len(args):
                kwargs['logs_path'] = args[i + 1]
                i += 2
            else:
                i += 1
        
        return kwargs
    
    @staticmethod
    def _print_usage():
        """Print usage information."""
        print("Usage: python runner.py <config_path> [--databricks-url URL] [--databricks-token TOKEN] [--databricks-catalog CATALOG] [--databricks-schema SCHEMA] [--databricks-volume VOLUME] [--logs-path PATH]")
        print("Example: python runner.py jobs/pegel_job.yaml")
        print("\nNote: Databricks settings can be specified in the job config file or via command-line arguments or environment variables.")
