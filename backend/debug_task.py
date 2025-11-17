#!/usr/bin/env python
"""
Debug task creation
"""
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saasCRM.settings")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from accounts.models import CustomUser, Tenant, UserTenant
from project.models import Client, Milestone, Project, Sprint
from project.serializers import TaskSerializer

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

milestone = Milestone.objects.filter(name="Test Milestone", project=project).first()
if not milestone:
    milestone = Milestone.objects.create(
        name="Test Milestone", project=project, tenant=tenant, status="active"
    )

sprint = Sprint.objects.filter(name="Test Sprint", milestone=milestone).first()
if not sprint:
    sprint = Sprint.objects.create(
        name="Test Sprint", milestone=milestone, tenant=tenant, status="active"
    )

print(f"Created sprint with slug: {sprint.slug}")

# Test task creation
data = {
    "title": "New Task",
    "milestone": milestone.slug,  # Use slug instead of ID
    "sprint": sprint.slug,  # Use slug instead of ID
    "status": "to_do",
}

print(f"Testing task creation with data: {data}")


# Create a mock request with tenant
class MockRequest:
    def __init__(self, user, tenant):
        self.user = user
        self.tenant = tenant


request = MockRequest(user, tenant)

serializer = TaskSerializer(data=data, context={"request": request})
if serializer.is_valid():
    task = serializer.save()
    print(f"✅ Task created successfully: {task.title} (slug: {task.slug})")
else:
    print(f"❌ Validation errors: {serializer.errors}")
