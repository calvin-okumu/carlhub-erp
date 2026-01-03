import requests
import os
import logging
import time
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

# Import circuit breaker components
try:
    from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
except ImportError:
    # Fallback for when circuit_breaker is not available
    logger.warning("Circuit breaker not available, using fallback implementation")

    class CircuitBreaker:
        def __init__(self, service_name: str, **kwargs):
            self.service_name = service_name

        def call(self, func):
            return func()

        def get_metrics(self):
            return {'service_name': self.service_name, 'state': 'unknown'}

    class CircuitBreakerOpenError(Exception):
        pass

class ServiceClient:
    """HTTP client for service-to-service communication"""

    def __init__(self, base_url: str, timeout: float = 5.0, service_name: str = None):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.service_name = service_name or os.getenv('SERVICE_NAME', 'unknown-service')
        self.session = requests.Session()

        # Service authentication
        self.service_key = os.getenv('SERVICE_API_KEY')

        # Circuit breaker for resilience
        self.circuit_breaker = CircuitBreaker(
            service_name=self.service_name or 'unknown-service',
            failure_threshold=5,
            timeout=60
        )

        # Set default headers
        self.session.headers.update({
            'X-Service-Auth': self.service_key or '',
            'X-Service-Name': self.service_name,
            'Content-Type': 'application/json',
        })

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request with circuit breaker protection"""
        def _get():
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        try:
            return self.circuit_breaker.call(_get)
        except CircuitBreakerOpenError:
            logger.warning(f"Circuit breaker open for {self.service_name}")
            raise ServiceUnavailableError(f"Service {self.service_name} temporarily unavailable")
        except requests.exceptions.RequestException as e:
            logger.error(f"Service call failed: GET {self.base_url}{endpoint} - {e}")
            raise ServiceUnavailableError(f"Service unavailable: {endpoint}")

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST request"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Service call failed: POST {url} - {e}")
            raise ServiceUnavailableError(f"Service unavailable: {endpoint}")

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT request"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.put(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Service call failed: PUT {url} - {e}")
            raise ServiceUnavailableError(f"Service unavailable: {endpoint}")

    def delete(self, endpoint: str) -> None:
        """DELETE request"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.delete(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Service call failed: DELETE {url} - {e}")
            raise ServiceUnavailableError(f"Service unavailable: {endpoint}")

class ServiceUnavailableError(Exception):
    """Raised when a service is unavailable"""
    pass