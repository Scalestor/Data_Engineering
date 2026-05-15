"""Factory for initializing ETL sources."""
import os
from typing import Dict, Optional
from core.sources import RESTSource


class SourceFactory:
    """Creates and configures source instances."""
    
    @staticmethod
    def create_rest_source(source_config: Dict) -> RESTSource:
        """
        Create a RESTSource instance from configuration.
        
        Args:
            source_config: Source configuration from job YAML
                - endpoint_url: REST API endpoint
                - auth_credential_key: Key for looking up auth in environment (optional)
                - timeout: Request timeout in seconds (default: 30)
                - max_retries: Number of retry attempts (default: 3)
        
        Returns:
            Configured RESTSource instance
        """
        endpoint_url = source_config.get("endpoint_url")
        auth_key = source_config.get("auth_credential_key")
        auth_type = None
        auth_credentials = None
        
        # Load authentication from environment if specified
        if auth_key:
            auth_type = os.getenv(f"{auth_key.upper()}_AUTH_TYPE")
            auth_credentials = os.getenv(f"{auth_key.upper()}_AUTH_CREDENTIALS")
        
        # Create source with config
        source = RESTSource(
            endpoint_url=endpoint_url,
            auth_type=auth_type,
            auth_credentials=auth_credentials,
            timeout=source_config.get("timeout", 30),
            max_retries=source_config.get("max_retries", 3)
        )
        
        return source
