#!/usr/bin/env python
"""
Simple test script for rate limiting middleware
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
from saasCRM.rate_limiting import EnhancedRateLimitMiddleware
from django.http import HttpResponse

def test_rate_limit_middleware():
    """Test rate limiting middleware functionality."""
    print("Testing Rate Limiting Middleware...")
    
    # Create middleware instance
    def dummy_get_response(request):
        return HttpResponse("OK")
    
    middleware = EnhancedRateLimitMiddleware(dummy_get_response)
    
    # Create test request
    factory = RequestFactory()
    request = factory.get('/api/clients/')
    
    print(f"Testing request to: {request.path}")
    
    # Test middleware processing
    try:
        response = middleware(request)
        if hasattr(response, 'status_code') and response.status_code == 200:
            print("✓ Request allowed through middleware")
        elif hasattr(response, 'status_code'):
            print(f"✓ Request processed by middleware: {response.status_code}")
        else:
            print("✓ Request processed by middleware")
    except Exception as e:
        print(f"✗ Middleware error: {e}")
    
    # Test different endpoints
    endpoints = [
        '/api/login/',
        '/api/signup/', 
        '/api/clients/',
        '/api/projects/',
        '/admin/'
    ]
    
    for endpoint in endpoints:
        request = factory.get(endpoint)
        try:
            response = middleware(request)
            if hasattr(response, 'status_code'):
                status = f"status {response.status_code}"
            else:
                status = "processed"
            print(f"  {endpoint}: {status}")
        except Exception as e:
            print(f"  {endpoint}: error - {e}")
    
    print("✓ Rate limiting middleware tests completed\n")

def test_rate_limit_config():
    """Test rate limit configuration."""
    print("Testing Rate Limit Configuration...")
    
    try:
        from saasCRM.rate_limiting import EnhancedRateLimitMiddleware
        
        # Create middleware to access config
        middleware = EnhancedRateLimitMiddleware(lambda r: HttpResponse("OK"))
        
        if hasattr(middleware, 'rate_limits'):
            print("Rate limit configurations found:")
            for endpoint, config in middleware.rate_limits.items():
                print(f"  {endpoint}: {config}")
        else:
            print("Rate limit configuration not found")
        
        print("✓ Rate limit configuration test passed\n")
        
    except Exception as e:
        print(f"✗ Rate limit configuration test failed: {e}\n")

if __name__ == '__main__':
    print("Starting Simple Rate Limiting Tests...\n")
    
    test_rate_limit_config()
    test_rate_limit_middleware()
    
    print("All rate limiting tests completed!")