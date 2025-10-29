#!/usr/bin/env python3
"""
Comprehensive Email Template Testing Script

This script tests all email templates in the DjangoCRM system to ensure they render correctly
and contain the expected content.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saasCRM.settings')
django.setup()

from django.template.loader import render_to_string


def test_template_rendering():
    """Test template rendering without database dependencies."""
    print("Testing email template rendering...")

    # Mock objects
    class MockTenant:
        name = 'Test Company'
        domain = 'test.com'

    class MockUser:
        email = 'test@example.com'
        first_name = 'Test'
        last_name = 'User'
        username = 'testuser'

    tenant = MockTenant()
    user = MockUser()

    # Test invitation email templates
    print("  Testing invitation templates...")
    context = {
        'email': 'invitee@example.com',
        'tenant': tenant,
        'role': 'Employee',
        'confirmation_url': 'http://example.com/confirm/test-token',
        'signup_url': 'http://example.com/signup/test-token',
        'expires_at': datetime.now() + timedelta(days=7),
        'is_resend': False,
        'site_name': 'DjangoCRM',
        'site_url': 'http://example.com',
        'support_email': 'support@example.com',
    }

    try:
        html_content = render_to_string('emails/invitation.html', context)
        text_content = render_to_string('emails/invitation.txt', context)

        # Debug: print first 200 chars of content
        print(f"      HTML content preview: {html_content[:200]}...")
        print(f"      Text content preview: {text_content[:200]}...")

        # Check HTML content
        assert 'Welcome to' in html_content
        assert tenant.name in html_content
        assert 'http://example.com/confirm/test-token' in html_content
        assert 'http://example.com/signup/test-token' in html_content

        # Check text content
        assert 'You\'re invited to join' in text_content
        assert tenant.name in text_content
        assert 'http://example.com/confirm/test-token' in text_content

        print("    ✓ Invitation email templates render correctly")
    except Exception as e:
        import traceback
        print(f"    ✗ Invitation template test failed: {e}")
        print(f"      Traceback: {traceback.format_exc()}")
        return False

    # Test welcome email templates
    print("  Testing welcome templates...")
    context = {
        'user': user,
        'tenant': tenant,
        'login_url': 'http://example.com/login/',
        'profile_url': 'http://example.com/profile/',
        'dashboard_url': 'http://example.com/dashboard/',
        'help_url': 'http://example.com/help/',
    }

    try:
        html_content = render_to_string('emails/welcome.html', context)
        text_content = render_to_string('emails/welcome.txt', context)

        # Check HTML content
        assert 'Welcome aboard' in html_content
        assert tenant.name in html_content
        assert user.first_name in html_content
        assert 'http://example.com/login/' in html_content

        # Check text content
        assert 'Welcome aboard' in text_content
        assert tenant.name in text_content
        assert user.first_name in text_content

        print("    ✓ Welcome email templates render correctly")
    except Exception as e:
        print(f"    ✗ Welcome template test failed: {e}")
        return False

    # Test password reset email templates
    print("  Testing password reset templates...")
    context = {
        'user': user,
        'reset_url': 'http://example.com/reset/test-token',
    }

    try:
        html_content = render_to_string('emails/password_reset.html', context)
        text_content = render_to_string('emails/password_reset.txt', context)

        # Check HTML content
        assert 'Password Reset Request' in html_content
        assert user.first_name in html_content
        assert 'http://example.com/reset/test-token' in html_content

        # Check text content
        assert 'Password Reset Request' in text_content
        assert user.first_name in text_content
        assert 'http://example.com/reset/test-token' in text_content

        print("    ✓ Password reset email templates render correctly")
    except Exception as e:
        print(f"    ✗ Password reset template test failed: {e}")
        return False

    # Test notification email templates
    print("  Testing notification templates...")
    context = {
        'recipient': user,
        'notification_title': 'Test Notification',
        'notification_message': 'This is a test notification message.',
        'notification_details': 'Additional details about the notification.',
        'action_url': 'http://example.com/action',
        'action_text': 'Take Action',
        'additional_info': 'Some additional information.',
        'site_name': 'DjangoCRM',
        'support_email': 'support@example.com',
    }

    try:
        html_content = render_to_string('emails/notification.html', context)
        text_content = render_to_string('emails/notification.txt', context)

        # Check HTML content
        assert 'Test Notification' in html_content
        assert 'This is a test notification message' in html_content
        assert 'Additional details' in html_content
        assert 'Take Action' in html_content
        assert 'additional information' in html_content
        assert user.first_name in html_content

        # Check text content
        assert 'Test Notification' in text_content
        assert 'This is a test notification message' in text_content
        assert 'Additional details' in text_content
        assert 'Take Action' in text_content
        assert 'additional information' in text_content
        assert user.first_name in text_content

        print("    ✓ Notification email templates render correctly")
    except Exception as e:
        print(f"    ✗ Notification template test failed: {e}")
        return False

    return True


def run_tests():
    """Run all email template tests."""
    print("🚀 Starting Email Template Tests")
    print("=" * 50)

    # Test template rendering
    if not test_template_rendering():
        print("❌ Template rendering tests failed!")
        return False

    print("=" * 50)
    print("✅ All email template tests passed!")
    return True


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)