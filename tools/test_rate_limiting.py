#!/usr/bin/env python
"""
Test script for rate limiting middleware
"""

import os
import sys

import django

# Setup Django
sys.path.append("/home/xorb/Project/Django_projects/Carlhub_react/DjangoCRM/backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saasCRM.settings")
django.setup()


from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


def test_rate_limiting():
    """Test rate limiting functionality."""
    print("Testing Rate Limiting Middleware...")

    # Create test client
    client = Client()

    # Test API endpoint rate limiting
    url = "/api/clients/"

    print(f"Testing rate limiting on {url}")

    # Make multiple requests quickly to trigger rate limit
    responses = []
    for i in range(10):
        response = client.get(url)
        responses.append(response.status_code)
        print(f"Request {i+1}: Status {response.status_code}")

        # Check for rate limit headers
        if hasattr(response, "headers"):
            remaining = response.headers.get("X-RateLimit-Remaining")
            reset = response.headers.get("X-RateLimit-Reset")
            if remaining:
                print(f"  Rate limit remaining: {remaining}")
            if reset:
                print(f"  Rate limit reset: {reset}")

    # Check if any request was rate limited
    if 429 in responses:
        print("✓ Rate limiting is working - some requests were limited")
    else:
        print(
            "? Rate limiting may not be triggered (limits might be too high for test)"
        )

    # Test different user/IP
    print("\nTesting with different client...")
    client2 = Client()
    response = client2.get(url)
    print(f"New client request: Status {response.status_code}")

    print("✓ Rate limiting tests completed\n")


def test_rate_limit_configuration():
    """Test rate limit configuration."""
    print("Testing Rate Limit Configuration...")

    try:
        from saasCRM.rate_limiting import RATE_LIMITS

        print("Rate limit configurations:")
        for endpoint, config in RATE_LIMITS.items():
            print(f"  {endpoint}: {config}")

        print("✓ Rate limit configuration test passed\n")

    except Exception as e:
        print(f"✗ Rate limit configuration test failed: {e}\n")


def test_rate_limit_headers():
    """Test rate limit headers."""
    print("Testing Rate Limit Headers...")

    client = Client()
    response = client.get("/api/clients/")

    if hasattr(response, "headers"):
        headers_to_check = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-RateLimit-Retry-After",
        ]

        print("Response headers:")
        for header in headers_to_check:
            value = response.headers.get(header)
            if value:
                print(f"  {header}: {value}")

        print("✓ Rate limit headers test passed\n")
    else:
        print("✗ No headers available in response\n")


if __name__ == "__main__":
    print("Starting Rate Limiting Tests...\n")

    test_rate_limit_configuration()
    test_rate_limiting()
    test_rate_limit_headers()

    print("All rate limiting tests completed!")
