"""Abstract base class for REST API data sources."""
from abc import ABC, abstractmethod
import requests
from typing import Dict, Any, Optional
import os
import time


class RESTSource(ABC):
    """
    Abstract base class for fetching data from REST endpoints.
    
    Handles HTTP requests with retry logic, response validation, and configurable headers.
    """
    
    def __init__(
        self,
        endpoint_url: str,
        auth_type: Optional[str] = None,
        auth_credentials: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        """
        Initialize REST source.
        
        Args:
            endpoint_url: Full URL of the REST endpoint
            auth_type: Type of authentication ('bearer', 'basic', 'api_key', or None)
            auth_credentials: Authentication credentials (token, username:password, or api_key)
            headers: Additional headers to include in request
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Seconds to wait between retries
        """
        self.endpoint_url = endpoint_url
        self.auth_type = auth_type
        self.auth_credentials = auth_credentials
        self.headers = headers or {}
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Set authorization header if provided
        if auth_type and auth_credentials:
            self._set_auth_header()
    
    def _set_auth_header(self):
        """Set authorization header based on auth_type."""
        if self.auth_type == "bearer":
            self.headers["Authorization"] = f"Bearer {self.auth_credentials}"
        elif self.auth_type == "basic":
            import base64
            encoded = base64.b64encode(self.auth_credentials.encode()).decode()
            self.headers["Authorization"] = f"Basic {encoded}"
        elif self.auth_type == "api_key":
            self.headers["X-API-Key"] = self.auth_credentials
    
    def fetch(self) -> Dict[str, Any]:
        """
        Fetch data from REST endpoint with retry logic.
        
        Returns:
            Parsed JSON response
            
        Raises:
            Exception: If fetch fails after all retries
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    self.endpoint_url,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    print(f"REST fetch failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"REST fetch failed after {self.max_retries} attempts")
        
        raise last_exception or Exception("Failed to fetch from REST endpoint")
    
    def fetch_with_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch data with query parameters.
        
        Args:
            params: Query parameters to include in request
            
        Returns:
            Parsed JSON response
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    self.endpoint_url,
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    print(f"REST fetch failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"REST fetch failed after {self.max_retries} attempts")
        
        raise last_exception or Exception("Failed to fetch from REST endpoint")
