#!/usr/bin/env python3
"""
Generate sample data for all microservices.
Development tool only - DO NOT USE IN PRODUCTION.
"""
import os
import sys

def print_success(msg):
    print(f"✅ {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def print_header(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")

# Configuration
NUM_TENANTS = int(os.getenv('NUM_TENANTS', '3'))
NUM_USERS = int(os.getenv('NUM_USERS', '10'))
NUM_PROJECTS = int(os.getenv('NUM_PROJECTS', '5'))
NUM_TASKS = int(os.getenv('NUM_TASKS', '20'))
NUM_INVOICES = int(os.getenv('NUM_INVOICES', '8'))
NUM_LEADS = int(os.getenv('NUM_LEADS', '10'))
NUM_LEAVE_REQUESTS = int(os.getenv('NUM_LEAVE_REQUESTS', '5'))

print_header("🚀 Sample Data Generator for Microservices")
print(f"⚙️  Configuration:")
print(f"   - Tenants: {NUM_TENANTS}")
print(f"   - Users: {NUM_USERS}")
print(f"   - Projects: {NUM_PROJECTS}")
print(f"   - Tasks: {NUM_TASKS}")
print(f"   - Invoices: {NUM_INVOICES}")
print(f"   - Leads: {NUM_LEADS}")
print(f"   - Leave Requests: {NUM_LEAVE_REQUESTS}")

print_warning("\nNote: For microservices, generate sample data per service:")
print_warning("  cd services/identity-service")
print_warning("  source venv/bin/activate")
print_warning("  python manage.py shell -c \"from identity.factories import *; TenantFactory.create_batch(3)\"")
print_warning("\nOr use monolithic backend:")
print_warning("  cd toremove/backend")
print_warning("  python manage.py generate_sample_data")

print_header("✅ Sample Data Generator Ready")
