#!/usr/bin/env python
"""
Debug milestone creation
"""
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saasCRM.settings")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from accounts.models import CustomUser, Tenant, UserTenant
from project.models import Client, Project
from project.serializers import MilestoneSerializer

# Get or create test data
tenant = Tenant.objects.filter(name="Test Tenant").first()
if not tenant:
    tenant = Tenant.objects.create(name="Test Tenant", domain="test.com")

user = CustomUser.objects.filter(email="test@example.com").first()
if not user:
    user = CustomUser.objects.create(email="test@example.com", first_name="Test", last_name="User")

UserTenant.objects.get_or_create(
    user=user, tenant=tenant, defaults={"is_owner": True, "is_approved": True}
)

client = Client.objects.filter(name="Test Client", tenant=tenant).first()
if not client:
    client = Client.objects.create(name="Test Client", email="client@test.com", tenant=tenant)

project = Project.objects.filter(name="Test Project", tenant=tenant).first()
if not project:
    project = Project.objects.create(
        name="Test Project", client=client, tenant=tenant, status="active"
    )

print(f"Created project with slug: {project.slug}")

# Test milestone creation
data = {
    "name": "New Milestone",
    "project": project.slug,  # Use slug instead of ID
    "status": "planning",
    "progress": 0,
}

print(f"Testing milestone creation with data: {data}")


# Create a mock request with tenant
class MockRequest:
    def __init__(self, user, tenant):
        self.user = user
        self.tenant = tenant


request = MockRequest(user, tenant)

serializer = MilestoneSerializer(data=data, context={"request": request})
if serializer.is_valid():
    milestone = serializer.save()
    print(f"✅ Milestone created successfully: {milestone.name} (slug: {milestone.slug})")
else:
    print(f"❌ Validation errors: {serializer.errors}")
