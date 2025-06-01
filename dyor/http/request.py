import requests
from typing import Dict, Optional, Union
from urllib.parse import urlencode

class HttpClient:
    """
    Utility class for making HTTP requests
    """
    def __init__(self, base_url: str = "", headers: Optional[Dict] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        
    def get(self, path: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Make GET request
        
        Args:
            path: API endpoint path
            params: Optional query parameters
            
        Returns:
            Response object
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        if params:
            url = f"{url}?{urlencode(params)}"
        return requests.get(url, headers=self.headers)

    def post(self, path: str, data: Optional[Union[Dict, str]] = None) -> requests.Response:
        """
        Make POST request
        
        Args:
            path: API endpoint path
            data: Request payload (dict will be sent as JSON)
            
        Returns:
            Response object
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        return requests.post(url, json=data if isinstance(data, dict) else data, headers=self.headers)

    def put(self, path: str, data: Optional[Union[Dict, str]] = None) -> requests.Response:
        """
        Make PUT request
        
        Args:
            path: API endpoint path
            data: Request payload (dict will be sent as JSON)
            
        Returns:
            Response object
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        return requests.put(url, json=data if isinstance(data, dict) else data, headers=self.headers)

    def delete(self, path: str) -> requests.Response:
        """
        Make DELETE request
        
        Args:
            path: API endpoint path
            
        Returns:
            Response object
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        return requests.delete(url, headers=self.headers)
