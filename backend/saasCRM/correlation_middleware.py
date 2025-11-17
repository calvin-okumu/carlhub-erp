"""
Request Correlation Middleware for DjangoCRM

This middleware adds unique request IDs to track requests across
different services and log entries for better debugging.
"""

import uuid
import logging
from typing import Optional

from django.utils.deprecation import MiddlewareMixin


class RequestCorrelationMiddleware(MiddlewareMixin):
    """
    Middleware to add correlation IDs to requests and log records.
    
    This ensures that all log entries for a single request can be
    correlated together, making debugging and tracing much easier.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Generate unique correlation ID for this request
        correlation_id = str(uuid.uuid4())
        request.correlation_id = correlation_id
        
        # Store correlation ID in thread-local for logging
        self._setup_correlation_logging(correlation_id, request)
        
        # Process request
        response = self.get_response(request)
        
        # Add correlation ID to response headers
        response['X-Correlation-ID'] = correlation_id
        
        # Clean up thread-local storage
        self._cleanup_correlation_logging()
        
        return response
    
    def _setup_correlation_logging(self, correlation_id: str, request):
        """Setup correlation ID for logging throughout the request."""
        # Store correlation ID in thread-local context
        import threading
        _local = threading.local()
        _local.correlation_id = correlation_id
        _local.request = request
        
        # Add correlation ID to all log records for this thread
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.correlation_id = correlation_id
            
            # Add user info if available
            if hasattr(request, 'user') and request.user.is_authenticated:
                record.user_id = str(request.user.id)
                record.user_email = request.user.email
            else:
                record.user_id = None
                record.user_email = None
            
            # Add tenant info if available
            if hasattr(request, 'tenant') and request.tenant:
                record.tenant_id = str(request.tenant.id)
            else:
                record.tenant_id = None
            
            return record
        
        logging.setLogRecordFactory(record_factory)
    
    def _cleanup_correlation_logging(self):
        """Clean up correlation logging after request."""
        # Restore original log record factory
        import logging
        logging.setLogRecordFactory(logging.getLogRecordFactory())


def get_correlation_id(request) -> Optional[str]:
    """
    Get correlation ID from request.
    
    Args:
        request: Django request object
        
    Returns:
        Correlation ID string or None
    """
    return getattr(request, 'correlation_id', None)


def get_current_correlation_id() -> Optional[str]:
    """
    Get correlation ID from current thread context.
    
    Returns:
        Correlation ID string or None
    """
    import threading
    _local = getattr(threading, '_local', None)
    if _local and hasattr(_local, 'correlation_id'):
        return _local.correlation_id
    return None