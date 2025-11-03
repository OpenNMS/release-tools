import requests
from typing import Optional, Dict, Any
import requests

class ConnectionHandler:
    def __init__(self, base_url, auth_credentials=None):
        self.base_url = base_url
        self.headers = {}
        if auth_credentials:
            self.headers['Circle-Token']=f'{auth_credentials}'

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def _default_headers(self) -> Dict:
        """Default headers for CircleCI API requests."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Circle-Token": "",
        }

    def _build_headers(self, token: str, method: str = "GET") -> Dict:
        """Construct headers with dynamic token and method-specific settings."""
        headers = self._headers.copy()
        headers["Circle-Token"] = token
        if method == "OPTIONS":
            headers.update({
                "Host": "circleci.com",
                "Origin": "https://app.circleci.com",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            })
        return headers

    def _request(self, method: str, url: str, token: str, data: Optional[Dict] = None) -> requests.Response:
        """Generic request handler for all HTTP methods."""
        headers = self._build_headers(token, method)
        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=self._timeout,
            )
            response.raise_for_status()  # Raise exceptions for HTTP errors
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def get_page(self, url: str, token: str) -> str:
        """GET request to fetch a page."""
        response = self._request("GET", url, token)
        return response.text

    def connect(self, url: str, token: str, data: Optional[Dict] = None) -> requests.Response:
        """Generic connect method for GET or POST requests."""
        return self._request("GET" if data is None else "POST", url, token, data)

    def option_connect(self, url: str, token: str) -> requests.Response:
        """OPTIONS request for preflight checks."""
        return self._request("OPTIONS", url, token)