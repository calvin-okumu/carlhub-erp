"""
Test utilities and base classes for DjangoCRM.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.factories import (
    TenantFactory,
    TenantOwnerFactory,
    UserFactory,
    UserTenantFactory,
)
from project.factories import (
    ClientFactory,
    InvoiceFactory,
    MilestoneFactory,
    PaymentFactory,
    ProjectFactory,
    TaskFactory,
)

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup and helper methods."""

    def setUp(self):
        """Set up common test data."""
        self.tenant = TenantFactory()
        self.user = UserFactory()
        self.user_tenant = TenantOwnerFactory(user=self.user, tenant=self.tenant)

    def create_client(self, **kwargs):
        """Create a client for the test tenant."""
        return ClientFactory(tenant=self.tenant, **kwargs)

    def create_project(self, client=None, **kwargs):
        """Create a project for the test tenant."""
        if client is None:
            client = self.create_client()
        return ProjectFactory(client=client, tenant=self.tenant, **kwargs)

    def create_milestone(self, project=None, **kwargs):
        """Create a milestone for the test tenant."""
        if project is None:
            project = self.create_project()
        return MilestoneFactory(project=project, tenant=self.tenant, **kwargs)

    def create_task(self, milestone=None, **kwargs):
        """Create a task for the test tenant."""
        if milestone is None:
            milestone = self.create_milestone()
        return TaskFactory(milestone=milestone, tenant=self.tenant, **kwargs)

    def create_invoice(self, client=None, project=None, **kwargs):
        """Create an invoice for the test tenant."""
        if client is None:
            client = self.create_client()
        if project is None:
            project = self.create_project(client=client)
        return InvoiceFactory(client=client, project=project, tenant=self.tenant, **kwargs)

    def create_payment(self, invoice=None, **kwargs):
        """Create a payment for the test tenant."""
        if invoice is None:
            invoice = self.create_invoice()
        return PaymentFactory(invoice=invoice, tenant=self.tenant, **kwargs)


class BaseAPITestCase(APITestCase):
    """Base API test case with authentication setup."""

    def setUp(self):
        """Set up authenticated user."""
        self.tenant = TenantFactory()
        self.user = UserFactory()
        self.user_tenant = TenantOwnerFactory(user=self.user, tenant=self.tenant)
        self.client.force_authenticate(user=self.user)

    def assert_response_success(self, response, expected_status=status.HTTP_200_OK):
        """Assert response is successful."""
        self.assertEqual(response.status_code, expected_status)

    def assert_response_created(self, response):
        """Assert response indicates resource creation."""
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def assert_response_no_content(self, response):
        """Assert response has no content."""
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def assert_response_bad_request(self, response):
        """Assert response indicates bad request."""
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def assert_response_unauthorized(self, response):
        """Assert response indicates unauthorized access."""
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def assert_response_forbidden(self, response):
        """Assert response indicates forbidden access."""
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def assert_response_not_found(self, response):
        """Assert response indicates resource not found."""
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestPermissionsMixin:
    """Mixin for testing permissions across different user roles."""

    def get_tenant_owner(self):
        """Get a tenant owner user."""
        user = UserFactory()
        tenant = TenantFactory()
        TenantOwnerFactory(user=user, tenant=tenant)
        return user, tenant

    def get_project_manager(self):
        """Get a project manager user."""
        user = UserFactory()
        tenant = TenantFactory()
        UserTenantFactory(user=user, tenant=tenant, is_owner=False, role="Project Manager")
        return user, tenant

    def get_regular_employee(self):
        """Get a regular employee user."""
        user = UserFactory()
        tenant = TenantFactory()
        UserTenantFactory(user=user, tenant=tenant, is_owner=False, role="Employee")
        return user, tenant

    def test_tenant_owner_access(self, url, method="get", data=None):
        """Test tenant owner can access endpoint."""
        user, tenant = self.get_tenant_owner()
        self.client.force_authenticate(user=user)

        if method.lower() == "get":
            response = self.client.get(url)
        elif method.lower() == "post":
            response = self.client.post(url, data, format="json")
        elif method.lower() == "put":
            response = self.client.put(url, data, format="json")
        elif method.lower() == "delete":
            response = self.client.delete(url)

        self.assert_response_success(response)

    def test_project_manager_access(self, url, method="get", data=None):
        """Test project manager access to endpoint."""
        user, tenant = self.get_project_manager()
        self.client.force_authenticate(user=user)

        if method.lower() == "get":
            response = self.client.get(url)
        elif method.lower() == "post":
            response = self.client.post(url, data, format="json")
        elif method.lower() == "put":
            response = self.client.put(url, data, format="json")
        elif method.lower() == "delete":
            response = self.client.delete(url)

        # Project managers should have limited access
        # This can be overridden in specific test classes
        return response

    def test_regular_employee_access(self, url, method="get", data=None):
        """Test regular employee access to endpoint."""
        user, tenant = self.get_regular_employee()
        self.client.force_authenticate(user=user)

        if method.lower() == "get":
            response = self.client.get(url)
        elif method.lower() == "post":
            response = self.client.post(url, data, format="json")
        elif method.lower() == "put":
            response = self.client.put(url, data, format="json")
        elif method.lower() == "delete":
            response = self.client.delete(url)

        # Regular employees should have very limited access
        # This can be overridden in specific test classes
        return response


class TestDataMixin:
    """Mixin for creating test data efficiently."""

    @staticmethod
    def create_test_tenant(**kwargs):
        """Create a test tenant."""
        return TenantFactory(**kwargs)

    @staticmethod
    def create_test_user(**kwargs):
        """Create a test user."""
        return UserFactory(**kwargs)

    @staticmethod
    def create_test_user_tenant(user=None, tenant=None, **kwargs):
        """Create a test user-tenant relationship."""
        if user is None:
            user = UserFactory()
        if tenant is None:
            tenant = TenantFactory()
        return UserTenantFactory(user=user, tenant=tenant, **kwargs)

    @staticmethod
    def create_test_client(tenant=None, **kwargs):
        """Create a test client."""
        if tenant is None:
            tenant = TenantFactory()
        return ClientFactory(tenant=tenant, **kwargs)

    @staticmethod
    def create_test_project(tenant=None, client=None, **kwargs):
        """Create a test project."""
        if tenant is None:
            tenant = TenantFactory()
        if client is None:
            client = ClientFactory(tenant=tenant)
        return ProjectFactory(tenant=tenant, client=client, **kwargs)

    @staticmethod
    def create_bulk_test_data(count=10, **kwargs):
        """Create bulk test data for performance testing."""
        tenant = TenantFactory()
        clients = ClientFactory.create_batch(count // 2, tenant=tenant)
        projects = []

        for client in clients:
            projects.extend(ProjectFactory.create_batch(2, tenant=tenant, client=client))

        return {"tenant": tenant, "clients": clients, "projects": projects}
