#!/usr/bin/env python
"""
Test script for security middleware headers
"""
import os
import sys
import django

# Setup Django
sys.path.append('/home/xorb/Project/Django_projects/Carlhub_react/DjangoCRM/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saasCRM.settings')
os.environ.setdefault('ALLOWED_HOSTS', 'testserver,localhost,127.0.0.1')
django.setup()

from django.test import RequestFactory
from django.http import HttpResponse
from saasCRM.security_middleware import SecurityHeadersMiddleware, APISecurityMiddleware

def test_security_headers_middleware():
    """Test security headers middleware."""
    print("Testing Security Headers Middleware...")
    
    # Create middleware instance
    def dummy_get_response(request):
        response = HttpResponse("Test content")
        response['Content-Type'] = 'text/html'
        return response
    
    middleware = SecurityHeadersMiddleware(dummy_get_response)
    
    # Create test request
    factory = RequestFactory()
    request = factory.get('/test/')
    
    # Process request through middleware
    response = middleware(request)
    
    # Check for security headers
    security_headers = [
        'X-Frame-Options',
        'X-Content-Type-Options', 
        'X-XSS-Protection',
        'Referrer-Policy',
        'Permissions-Policy'
    ]
    
    print("Security headers found:")
    for header in security_headers:
        value = response.get(header)
        if value:
            print(f"  ✓ {header}: {value}")
        else:
            print(f"  ✗ {header}: Missing")
    
    # Check CSP header (might be present)
    csp = response.get('Content-Security-Policy')
    if csp:
        print(f"  ✓ Content-Security-Policy: {csp[:100]}...")
    else:
        print(f"  ? Content-Security-Policy: Not set (may be conditional)")
    
    print("✓ Security headers middleware tests completed\n")

def test_api_security_middleware():
    """Test API security middleware."""
    print("Testing API Security Middleware...")
    
    # Create middleware instance
    def dummy_get_response(request):
        response = HttpResponse('{"result": "success"}')
        response['Content-Type'] = 'application/json'
        return response
    
    middleware = APISecurityMiddleware(dummy_get_response)
    
    # Create test API request
    factory = RequestFactory()
    request = factory.get('/api/clients/')
    request.content_type = 'application/json'
    
    # Process request through middleware
    response = middleware(request)
    
    # Check for API-specific headers
    api_headers = [
        'X-API-Version',
        'X-Content-Type-Options',
        'X-Request-ID'
    ]
    
    print("API security headers found:")
    for header in api_headers:
        value = response.get(header)
        if value:
            print(f"  ✓ {header}: {value}")
        else:
            print(f"  ? {header}: Not set")
    
    # Check that Server header is removed
    server_header = response.get('Server')
    if not server_header:
        print("  ✓ Server header: Removed")
    else:
        print(f"  ✗ Server header: Still present ({server_header})")
    
    print("✓ API security middleware tests completed\n")

def test_content_type_validation():
    """Test content type validation for API requests."""
    print("Testing Content Type Validation...")
    
    def dummy_get_response(request):
        return HttpResponse('OK')
    
    middleware = APISecurityMiddleware(dummy_get_response)
    
    factory = RequestFactory()
    
    # Test valid content types
    valid_content_types = [
        'application/json',
        'application/json; charset=utf-8',
        'multipart/form-data'
    ]
    
    for content_type in valid_content_types:
        request = factory.post('/api/clients/', data='{}', content_type=content_type)
        try:
            response = middleware.process_request(request)
            if response is None:
                print(f"  ✓ {content_type}: Accepted")
            else:
                print(f"  ✗ {content_type}: Rejected ({response.status_code})")
        except Exception as e:
            print(f"  ✗ {content_type}: Error - {e}")
    
    # Test invalid content types
    invalid_content_types = [
        'text/plain',
        'application/xml',
        ''
    ]
    
    for content_type in invalid_content_types:
        request = factory.post('/api/clients/', data='test', content_type=content_type)
        try:
            response = middleware.process_request(request)
            if response is not None and response.status_code == 400:
                print(f"  ✓ {content_type}: Correctly rejected")
            else:
                print(f"  ✗ {content_type}: Should be rejected")
        except Exception as e:
            print(f"  ? {content_type}: Error - {e}")
    
    print("✓ Content type validation tests completed\n")

def test_skip_conditions():
    """Test conditions where security headers should be skipped."""
    print("Testing Skip Conditions...")
    
    def dummy_get_response(request):
        return HttpResponse("Test")
    
    middleware = SecurityHeadersMiddleware(dummy_get_response)
    
    factory = RequestFactory()
    
    # Test paths that should skip security headers
    skip_paths = [
        '/static/test.css',
        '/media/image.jpg', 
        '/api/health/',
        '/api/schema/'
    ]
    
    for path in skip_paths:
        request = factory.get(path)
        response = middleware(request)
        
        # Check if security headers are minimal
        has_security_headers = any(
            response.get(header) for header in ['X-Frame-Options', 'X-Content-Type-Options']
        )
        
        if not has_security_headers:
            print(f"  ✓ {path}: Security headers skipped")
        else:
            print(f"  ? {path}: Security headers still applied")
    
    print("✓ Skip conditions tests completed\n")

if __name__ == '__main__':
    print("Starting Security Middleware Tests...\n")
    
    test_security_headers_middleware()
    test_api_security_middleware()
    test_content_type_validation()
    test_skip_conditions()
    
    print("All security middleware tests completed!")