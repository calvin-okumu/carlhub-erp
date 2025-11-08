#!/usr/bin/env python
"""
Debug sprint creation
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saasCRM.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from project.models import Project, Milestone, Sprint, Client
from accounts.models import Tenant, CustomUser, UserTenant
from project.serializers import SprintSerializer

# Get or create test data
tenant = Tenant.objects.filter(name="Test Tenant").first()
if not tenant:
    tenant = Tenant.objects.create(name="Test Tenant", domain='test.com')

user = CustomUser.objects.filter(email="test@example.com").first()
if not user:
    user = CustomUser.objects.create(email="test@example.com", first_name='Test', last_name='User')

UserTenant.objects.get_or_create(
    user=user,
    tenant=tenant,
    defaults={'is_owner': True, 'is_approved': True}
)

client = Client.objects.filter(name="Test Client", tenant=tenant).first()
if not client:
    client = Client.objects.create(name="Test Client", email="client@test.com", tenant=tenant)

project = Project.objects.filter(name="Test Project", tenant=tenant).first()
if not project:
    project = Project.objects.create(name="Test Project", client=client, tenant=tenant, status='active')

milestone = Milestone.objects.filter(name="Test Milestone", project=project).first()
if not milestone:
    milestone = Milestone.objects.create(name="Test Milestone", project=project, tenant=tenant, status='active')

print(f"Created milestone with slug: {milestone.slug}")

# Test sprint creation
data = {
    'name': 'New Sprint',
    'milestone': milestone.slug,  # Use slug instead of ID
    'status': 'planned',
}

print(f"Testing sprint creation with data: {data}")

# Create a mock request with tenant
class MockRequest:
    def __init__(self, user, tenant):
        self.user = user
        self.tenant = tenant

request = MockRequest(user, tenant)

serializer = SprintSerializer(data=data, context={'request': request})
if serializer.is_valid():
    sprint = serializer.save()
    print(f"✅ Sprint created successfully: {sprint.name} (slug: {sprint.slug})")
else:
    print(f"❌ Validation errors: {serializer.errors}")