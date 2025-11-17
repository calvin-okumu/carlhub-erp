"""
Enhanced Rate Limiting for DjangoCRM

This module provides advanced rate limiting with different strategies
for various types of endpoints and user tiers.
"""

import time
import logging
from typing import Dict, Optional, Tuple
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import Throttled


logger = logging.getLogger(__name__)


class RateLimitExceeded(PermissionDenied):
    """Custom exception for rate limit exceeded."""
    pass


class EnhancedRateLimitMiddleware:
    """
    Enhanced rate limiting middleware with different strategies for different endpoints.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rate limit configurations (requests per minute)
        self.rate_limits = {
            # Authentication endpoints - very strict
            'auth_login': {'requests': 5, 'window': 300, 'burst': 3},  # 5 per 5 min, max 3 burst
            'auth_register': {'requests': 3, 'window': 900, 'burst': 1},  # 3 per 15 min, max 1 burst
            'auth_password_reset': {'requests': 3, 'window': 900, 'burst': 1},  # 3 per 15 min
            'auth_password_change': {'requests': 10, 'window': 3600, 'burst': 5},  # 10 per hour
            
            # API endpoints - moderate
            'api_general': {'requests': 100, 'window': 60, 'burst': 20},  # 100 per minute
            'api_search': {'requests': 30, 'window': 60, 'burst': 10},  # 30 per minute
            'api_upload': {'requests': 10, 'window': 60, 'burst': 3},  # 10 per minute
            
            # Admin endpoints - very strict
            'admin_general': {'requests': 50, 'window': 60, 'burst': 10},  # 50 per minute
            'admin_bulk': {'requests': 5, 'window': 60, 'burst': 2},  # 5 per minute
        }
        
        # IP-based blocking for repeated violations
        self.violation_threshold = 10  # Number of violations before temporary block
        self.block_duration = 3600  # 1 hour block for repeated violations
    
    def __call__(self, request):
        # Skip rate limiting for health checks and static files
        if self._should_skip_rate_limiting(request):
            return self.get_response(request)
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Check if client is blocked
        if self._is_client_blocked(client_id):
            return self._rate_limit_response("Client temporarily blocked due to repeated violations")
        
        # Determine rate limit category
        rate_limit_key = self._get_rate_limit_category(request)
        
        if rate_limit_key:
            # Check rate limit
            if not self._check_rate_limit(client_id, rate_limit_key):
                self._record_violation(client_id)
                return self._rate_limit_response(f"Rate limit exceeded for {rate_limit_key}")
        
        response = self.get_response(request)
        
        # Add rate limit headers
        if rate_limit_key:
            self._add_rate_limit_headers(response, client_id, rate_limit_key)
        
        return response
    
    def _should_skip_rate_limiting(self, request) -> bool:
        """Skip rate limiting for certain requests."""
        skip_paths = [
            '/api/health/',
            '/static/',
            '/media/',
            '/admin/jsi18n/',
        ]
        
        return any(request.path.startswith(path) for path in skip_paths)
    
    def _get_client_identifier(self, request) -> str:
        """Get unique client identifier."""
        # Try to get authenticated user ID first
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}"
        
        # Fall back to IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        return f"ip:{ip}"
    
    def _get_rate_limit_category(self, request) -> Optional[str]:
        """Determine rate limit category based on request path and method."""
        path = request.path
        method = request.method
        
        # Authentication endpoints
        if path.endswith('/login/') and method == 'POST':
            return 'auth_login'
        elif path.endswith('/signup/') and method == 'POST':
            return 'auth_register'
        elif '/password-reset/' in path and method == 'POST':
            return 'auth_password_reset'
        elif '/password-change/' in path and method == 'POST':
            return 'auth_password_change'
        
        # Admin endpoints
        elif path.startswith('/admin/'):
            if method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                return 'admin_bulk'
            else:
                return 'admin_general'
        
        # API endpoints
        elif path.startswith('/api/'):
            if method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                return 'api_general'
            elif 'search' in path or 'filter' in path:
                return 'api_search'
            elif 'upload' in path or 'file' in path:
                return 'api_upload'
            else:
                return 'api_general'
        
        return None
    
    def _check_rate_limit(self, client_id: str, category: str) -> bool:
        """Check if client has exceeded rate limit."""
        config = self.rate_limits.get(category)
        if not config:
            return True
        
        # Cache keys
        key = f"rate_limit:{category}:{client_id}"
        burst_key = f"rate_limit_burst:{category}:{client_id}"
        
        now = int(time.time())
        window = config['window']
        max_requests = config['requests']
        burst_limit = config.get('burst', max_requests)
        
        # Get current request count
        requests = cache.get(key, [])
        
        # Remove old requests outside the window
        requests = [req_time for req_time in requests if now - req_time < window]
        
        # Check if adding current request would exceed limit
        if len(requests) >= max_requests:
            return False
        
        # Check burst limit (requests in last 10 seconds)
        recent_requests = [req_time for req_time in requests if now - req_time < 10]
        if len(recent_requests) >= burst_limit:
            return False
        
        # Add current request
        requests.append(now)
        cache.set(key, requests, window)
        
        return True
    
    def _is_client_blocked(self, client_id: str) -> bool:
        """Check if client is temporarily blocked."""
        block_key = f"rate_limit_block:{client_id}"
        return cache.get(block_key, False)
    
    def _record_violation(self, client_id: str):
        """Record a rate limit violation."""
        violation_key = f"rate_limit_violations:{client_id}"
        violations = cache.get(violation_key, 0) + 1
        cache.set(violation_key, violations, self.block_duration)
        
        # Block client if threshold exceeded
        if violations >= self.violation_threshold:
            block_key = f"rate_limit_block:{client_id}"
            cache.set(block_key, True, self.block_duration)
            
            logger.warning(f"Client {client_id} blocked due to {violations} rate limit violations")
    
    def _add_rate_limit_headers(self, response, client_id: str, category: str):
        """Add rate limit information to response headers."""
        config = self.rate_limits.get(category)
        if not config:
            return
        
        key = f"rate_limit:{category}:{client_id}"
        requests = cache.get(key, [])
        
        now = int(time.time())
        window = config['window']
        max_requests = config['requests']
        
        # Count requests in current window
        current_requests = len([req_time for req_time in requests if now - req_time < window])
        
        response['X-RateLimit-Limit'] = str(max_requests)
        response['X-RateLimit-Remaining'] = str(max(0, max_requests - current_requests))
        response['X-RateLimit-Reset'] = str(now + window)
    
    def _rate_limit_response(self, message: str):
        """Return rate limit error response."""
        return JsonResponse({
            'error': 'Rate limit exceeded',
            'message': message,
            'retry_after': 60  # Suggest retry after 1 minute
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)


class CustomThrottle:
    """
    Custom throttle class for DRF that integrates with our enhanced rate limiting.
    """
    
    def __init__(self, rate_limit_category: str):
        self.rate_limit_category = rate_limit_category
        self.rate_limits = {
            'auth_login': {'requests': 5, 'window': 300},
            'auth_register': {'requests': 3, 'window': 900},
            'api_general': {'requests': 100, 'window': 60},
            'api_search': {'requests': 30, 'window': 60},
        }
    
    def allow_request(self, request, view):
        """Check if request should be allowed."""
        client_id = self._get_client_identifier(request)
        config = self.rate_limits.get(self.rate_limit_category)
        
        if not config:
            return True
        
        # Similar logic to EnhancedRateLimitMiddleware but for DRF
        key = f"drf_throttle:{self.rate_limit_category}:{client_id}"
        requests = cache.get(key, [])
        
        now = int(time.time())
        window = config['window']
        max_requests = config['requests']
        
        # Remove old requests
        requests = [req_time for req_time in requests if now - req_time < window]
        
        if len(requests) >= max_requests:
            return False
        
        requests.append(now)
        cache.set(key, requests, window)
        
        return True
    
    def wait(self):
        """Returns recommended retry after time."""
        return 60
    
    def _get_client_identifier(self, request) -> str:
        """Get unique client identifier."""
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}"
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        return f"ip:{ip}"