"""
Security Middleware for DjangoCRM

This middleware adds comprehensive security headers to all HTTP responses
to protect against common web vulnerabilities.
"""

import os
from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to HTTP responses.
    
    Headers added:
    - X-Frame-Options: Prevent clickjacking
    - X-Content-Type-Options: Prevent MIME-type sniffing
    - X-XSS-Protection: Enable XSS protection
    - Strict-Transport-Security: Enforce HTTPS (production only)
    - Content-Security-Policy: Prevent XSS and data injection
    - Referrer-Policy: Control referrer information
    - Permissions-Policy: Control browser features
    """
    
    def process_response(self, request, response):
        # Skip for static files and health checks
        if self._should_skip_security_headers(request, response):
            return response
            
        # Frame protection
        response['X-Frame-Options'] = 'DENY'
        
        # MIME type protection
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS protection (legacy but still useful)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # HTTPS enforcement (production only)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Content Security Policy
        csp = self._build_csp()
        if csp:
            response['Content-Security-Policy'] = csp
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature Policy)
        permissions_policy = self._build_permissions_policy()
        if permissions_policy:
            response['Permissions-Policy'] = permissions_policy
        
        return response
    
    def _should_skip_security_headers(self, request, response):
        """Skip security headers for certain requests."""
        # Skip for static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return True
        
        # Skip for health checks
        if request.path.startswith('/api/health/'):
            return True
        
        # Skip for API documentation
        if request.path.startswith('/api/schema/'):
            return True
        
        # Skip for non-HTML responses
        if not isinstance(response, HttpResponse):
            return True
            
        content_type = response.get('Content-Type', '').lower()
        if content_type and not any(ct in content_type for ct in ['text/html', 'application/json']):
            return True
        
        return False
    
    def _build_csp(self):
        """Build Content Security Policy based on environment."""
        if settings.DEBUG:
            # Development CSP - more permissive
            directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://localhost:3000",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data: https:",
                "connect-src 'self' https://localhost:8000 https://localhost:3000 ws://localhost:8000 ws://localhost:3000",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
        else:
            # Production CSP - strict
            frontend_url = getattr(settings, 'FRONTEND_URL', 'https://localhost:3000')
            directives = [
                "default-src 'self'",
                "script-src 'self'",
                "style-src 'self' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data: https:",
                f"connect-src 'self' {frontend_url}",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
                "object-src 'none'",
                "media-src 'self'",
                "manifest-src 'self'",
            ]
        
        return '; '.join(directives)
    
    def _build_permissions_policy(self):
        """Build Permissions Policy to control browser features."""
        directives = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
            "ambient-light-sensor=()",
            "autoplay=(self)",
            "encrypted-media=(self)",
            "fullscreen=(self)",
            "picture-in-picture=(self)",
        ]
        
        return ', '.join(directives)


class APISecurityMiddleware(MiddlewareMixin):
    """
    Additional security middleware specifically for API endpoints.
    """
    
    def process_request(self, request):
        """Add API-specific security measures."""
        if request.path.startswith('/api/'):
            # Validate Content-Type for POST/PUT/PATCH requests
            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.content_type or ''
                if not content_type.startswith('application/json') and not content_type.startswith('multipart/form-data'):
                    from django.http import JsonResponse
                    return JsonResponse(
                        {'error': 'Invalid Content-Type. Expected application/json or multipart/form-data'},
                        status=400
                    )
            
            # Add request ID for tracking
            import uuid
            request.id = str(uuid.uuid4())
    
    def process_response(self, request, response):
        """Add API-specific security headers."""
        if request.path.startswith('/api/'):
            # API-specific headers
            response['X-API-Version'] = getattr(settings, 'API_VERSION', 'v1')
            response['X-Content-Type-Options'] = 'nosniff'
            
            # Add request ID if available
            if hasattr(request, 'id'):
                response['X-Request-ID'] = request.id
            
            # Remove server information
            if 'Server' in response:
                del response['Server']
        
        return response