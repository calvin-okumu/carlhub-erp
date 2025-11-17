#!/usr/bin/env python
"""
Environment Configuration Checker
Validates that required environment variables are set for DjangoCRM
"""
import os

from dotenv import load_dotenv


def check_env():
    """Check environment variables and report status"""
    load_dotenv()

    required_vars = [
        "SECRET_KEY",
        "DEBUG",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
    ]

    oauth_vars = [
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GITHUB_CLIENT_ID",
        "GITHUB_CLIENT_SECRET",
    ]

    print("🔍 Checking DjangoCRM Environment Configuration")
    print("=" * 50)

    # Check required variables
    print("\n📋 Required Variables:")
    all_required = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(
                f"✅ {var}: {'*' * len(value) if 'SECRET' in var or 'PASSWORD' in var else value}"
            )
        else:
            print(f"❌ {var}: NOT SET")
            all_required = False

    # Check OAuth variables (optional)
    print("\n🔐 OAuth Variables (Optional):")
    oauth_configured = False
    for var in oauth_vars:
        value = os.getenv(var)
        if value and value != f'your-{var.lower().replace("_", "-")}-here':
            print(f"✅ {var}: {'*' * len(value)}")
            oauth_configured = True
        else:
            print(f"⚠️  {var}: NOT CONFIGURED")

    print("\n" + "=" * 50)
    if all_required:
        print("✅ All required variables are configured!")
        if oauth_configured:
            print("✅ OAuth authentication is ready!")
        else:
            print("⚠️  OAuth authentication not configured (optional)")
        print("\n🚀 You can now run: python manage.py runserver")
    else:
        print("❌ Some required variables are missing!")
        print("Please check your .env file and ensure all required variables are set.")


if __name__ == "__main__":
    check_env()
