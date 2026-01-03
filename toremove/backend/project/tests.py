from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser, Tenant, UserTenant

from accounting.models import Invoice, Payment
from .models import Client, Milestone, Project, Sprint, Task


class ModelTests(TestCase):
    """Test model creation, relationships, and validation"""

    def setUp(self):
        self.org = Tenant.objects.create(name="Test Organization", address="123 Test St")
        self.client_obj = Client.objects.create(
            name="Test Client",
            email="test@example.com",
            phone="+1234567890",
            status="active",
            tenant=self.org,
        )
        self.project = Project.objects.create(
            name="Test Project",
            tenant=self.org,
            client=self.client_obj,
            status="active",
            priority="high",
            budget=Decimal("50000.00"),
            description="Test project description",
        )
        self.milestone = Milestone.objects.create(
            name="Test Milestone", tenant=self.org, project=self.project, status="active"
        )
        self.sprint = Sprint.objects.create(
            name="Test Sprint", tenant=self.org, milestone=self.milestone, status="active"
        )
        self.task = Task.objects.create(
            title="Test Task",
            tenant=self.org,
            milestone=self.milestone,
            sprint=self.sprint,
            status="in_progress",
        )
        self.invoice = Invoice.objects.create(
            tenant=self.org,
            client=self.client_obj,
            project=self.project,
            amount=Decimal("15000.00"),
        )
        self.payment = Payment.objects.create(
            tenant=self.org, invoice=self.invoice, amount=Decimal("15000.00")
        )

    def test_organization_creation(self):
        """Test organization model creation"""
        self.assertEqual(self.org.name, "Test Organization")
        self.assertEqual(str(self.org), "Test Organization")

    def test_client_creation(self):
        """Test client model creation and relationships"""
        self.assertEqual(self.client_obj.name, "Test Client")
        self.assertEqual(self.client_obj.email, "test@example.com")
        self.assertEqual(self.client_obj.tenant, self.org)
        self.assertEqual(str(self.client_obj), "Test Client")
        self.assertEqual(self.client_obj.status, "active")

    def test_project_creation(self):
        """Test project model creation and relationships"""
        self.assertEqual(self.project.name, "Test Project")
        self.assertEqual(self.project.client, self.client_obj)
        self.assertEqual(self.project.status, "active")
        self.assertEqual(self.project.priority, "high")
        self.assertEqual(self.project.budget, Decimal("50000.00"))
        self.assertEqual(str(self.project), "Test Project")

    def test_milestone_creation(self):
        """Test milestone model creation and validation"""
        self.assertEqual(self.milestone.name, "Test Milestone")
        self.assertEqual(self.milestone.project, self.project)
        self.assertEqual(self.milestone.calculate_progress(), 0)  # No completed sprints
        self.assertEqual(str(self.milestone), "Test Milestone (Test Project)")

        # Test progress validation
        with self.assertRaises(ValidationError):
            invalid_milestone = Milestone(name="Invalid", project=self.project, progress=150)
            invalid_milestone.full_clean()

    def test_sprint_creation(self):
        """Test sprint model creation"""
        self.assertEqual(self.sprint.name, "Test Sprint")
        self.assertEqual(self.sprint.milestone, self.milestone)
        self.assertEqual(str(self.sprint), "Test Sprint (Test Milestone)")

    def test_task_creation(self):
        """Test task model creation"""
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.sprint, self.sprint)
        self.assertEqual(self.task.status, "in_progress")
        self.assertEqual(str(self.task), "Test Task")

    def test_invoice_creation(self):
        """Test invoice model creation"""
        self.assertEqual(self.invoice.client, self.client_obj)
        self.assertEqual(self.invoice.project, self.project)
        self.assertEqual(self.invoice.amount, Decimal("15000.00"))
        self.assertFalse(self.invoice.paid)
        self.assertIn("Invoice", str(self.invoice))

    def test_payment_creation(self):
        """Test payment model creation"""
        self.assertEqual(self.payment.invoice, self.invoice)
        self.assertEqual(self.payment.amount, Decimal("15000.00"))
        self.assertIn("Payment", str(self.payment))

    def test_relationships(self):
        """Test all model relationships"""
        # Tenant -> Client
        self.assertIn(self.client_obj, self.org.clients.all())

        # Client -> Project
        self.assertIn(self.project, self.client_obj.projects.all())

        # Project -> Milestone
        self.assertIn(self.milestone, self.project.milestones.all())

        # Milestone -> Sprint
        self.assertIn(self.sprint, self.milestone.sprints.all())

        # Sprint -> Task
        self.assertIn(self.task, self.sprint.tasks.all())

        # Client/Project -> Invoice
        self.assertIn(self.invoice, self.client_obj.invoices.all())
        self.assertIn(self.invoice, self.project.invoices.all())

        # Invoice -> Payment
        self.assertIn(self.payment, self.invoice.payments.all())

        # Mark first task back
        self.task.status = "in_progress"
        self.task.save()
        self.sprint.refresh_from_db()
        self.assertEqual(self.sprint.status, "active")

    def test_unique_constraints(self):
        """Test unique constraints"""
        # Tenant name unique
        with self.assertRaises(IntegrityError):
            Tenant.objects.create(name="Test Organization")

        # Client email unique
        with self.assertRaises(IntegrityError):
            Client.objects.create(name="Another Client", email="test@example.com", tenant=self.org)


class AuthenticationTests(APITestCase):
    """Test authentication endpoints"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(email="test@example.com", password="testpass123")

    def test_login_success(self):
        """Test successful login"""
        data = {"email": "test@example.com", "password": "testpass123"}
        response = self.client.post("/api/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user_id", response.data)
        self.assertIn("role", response.data)
        self.assertEqual(response.data["email"], "test@example.com")

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {"email": "test@example.com", "password": "wrongpassword"}
        response = self.client.post("/api/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        # Missing password
        data = {"email": "test@example.com"}
        response = self.client.post("/api/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing email
        data = {"password": "testpass123"}
        response = self.client.post("/api/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TenantAPITests(APITestCase):
    """Test Tenant API endpoints"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="testpass"
        )
        self.client.force_authenticate(user=self.user)

        self.org1 = Tenant.objects.create(
            name="Org 1", address="Address 1", domain="org1.example.com"
        )
        # Note: UserTenant has OneToOneField, so user can only belong to one tenant
        # For testing multiple tenants, we'd need separate users or modify the model
        from accounts.models import UserTenant

        UserTenant.objects.create(user=self.user, tenant=self.org1, is_owner=True, is_approved=True)

    def test_list_tenants(self):
        """Test listing tenants"""
        response = self.client.get("/api/tenants/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_tenant(self):
        """Test creating tenant"""
        data = {"name": "New Tenant", "address": "New Address"}
        response = self.client.post("/api/tenants/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Tenant")

    def test_retrieve_tenant(self):
        """Test retrieving single tenant"""
        response = self.client.get(f"/api/tenants/{self.org1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Org 1")

    def test_update_tenant(self):
        """Test updating tenant"""
        data = {"name": "Updated Tenant", "address": "Updated Address"}
        response = self.client.put(f"/api/tenants/{self.org1.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Tenant")

    def test_delete_tenant(self):
        """Test deleting tenant"""
        response = self.client.delete(f"/api/tenants/{self.org1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify deletion
        response = self.client.get(f"/api/tenants/{self.org1.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tenant_filtering(self):
        """Test tenant filtering and searching"""
        # Search by name
        response = self.client.get("/api/tenants/?search=Org 1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Ordering
        response = self.client.get("/api/tenants/?ordering=name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ClientAPITests(APITestCase):
    """Test Client API endpoints"""

    def setUp(self):
        # Create user with proper permissions
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="testpass"
        )
        # Assign Tenant Owners group which has all permissions
        self.group, created = Group.objects.get_or_create(name="Tenant Owners")
        self.user.groups.add(self.group)
        # Also assign permissions directly for test
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        client_content_type = ContentType.objects.get_for_model(Client)
        permissions = Permission.objects.filter(
            content_type=client_content_type,
            codename__in=["add_client", "change_client", "delete_client", "view_client"],
        )
        self.user.user_permissions.add(*permissions)
        self.client.force_authenticate(user=self.user)

        self.org = Tenant.objects.create(name="Test Org")
        # Create UserTenant association
        from accounts.models import UserTenant

        UserTenant.objects.create(user=self.user, tenant=self.org, is_owner=True, is_approved=True)
        self.client_obj = Client.objects.create(
            name="Test Client", email="test@example.com", tenant=self.org, status="active"
        )

    def test_list_clients(self):
        """Test listing clients"""
        response = self.client.get("/api/clients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("tenant_name", response.data["results"][0])
        self.assertIn("projects_count", response.data["results"][0])

    def test_create_client(self):
        """Test creating client"""
        data = {"name": "New Client", "email": "new@example.com", "status": "prospect"}
        response = self.client.post("/api/clients/", data, format="json")
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Client")
        # Verify tenant was auto-assigned
        self.assertEqual(response.data["tenant"], self.org.id)

    def test_client_validation(self):
        """Test client validation"""
        # Duplicate email
        data = {
            "name": "Another Client",
            "email": "test@example.com",  # Duplicate
        }
        response = self.client.post("/api/clients/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_filtering(self):
        """Test client filtering"""
        # Filter by status
        response = self.client.get("/api/clients/?status=active")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        # Search by name
        response = self.client.get("/api/clients/?search=Test Client")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


class ProjectAPITests(APITestCase):
    """Test Project API endpoints"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="testpass"
        )
        # Assign Tenant Owners group which has all permissions
        self.group, created = Group.objects.get_or_create(name="Tenant Owners")
        self.user.groups.add(self.group)
        # Also assign permissions directly for test
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        project_content_type = ContentType.objects.get_for_model(Project)
        permissions = Permission.objects.filter(
            content_type=project_content_type,
            codename__in=["add_project", "change_project", "delete_project", "view_project"],
        )
        self.user.user_permissions.add(*permissions)
        self.client.force_authenticate(user=self.user)

        self.org = Tenant.objects.create(name="Test Org")
        # Create UserTenant association
        from accounts.models import UserTenant

        UserTenant.objects.create(user=self.user, tenant=self.org, is_owner=True, is_approved=True)
        self.client_obj = Client.objects.create(
            name="Test Client", email="test@example.com", tenant=self.org
        )
        self.project = Project.objects.create(
            name="Test Project",
            client=self.client_obj,
            tenant=self.org,
            status="active",
            priority="high",
            budget=Decimal("50000.00"),
        )

    def test_list_projects(self):
        """Test listing projects"""
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("client_name", response.data["results"][0])
        self.assertIn("milestones_count", response.data["results"][0])

    def test_create_project(self):
        """Test creating project"""
        data = {
            "name": "New Project",
            "client": self.client_obj.id,
            "tenant": self.org.id,
            "status": "planning",
            "priority": "medium",
            "budget": "25000.00",
            "description": "New project description",
        }
        response = self.client.post("/api/projects/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Project")

    def test_project_filtering(self):
        """Test project filtering"""
        # Filter by status
        response = self.client.get("/api/projects/?status=active")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        # Filter by priority
        response = self.client.get("/api/projects/?priority=high")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


class MilestoneAPITests(APITestCase):
    """Test Milestone API endpoints"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="testpass"
        )
        self.client.force_authenticate(user=self.user)

        self.org = Tenant.objects.create(name="Test Org")
        # Create UserTenant association
        from accounts.models import UserTenant

        UserTenant.objects.create(user=self.user, tenant=self.org, is_owner=True, is_approved=True)
        self.client_obj = Client.objects.create(
            name="Test Client", email="test@example.com", tenant=self.org
        )
        self.project = Project.objects.create(
            name="Test Project", client=self.client_obj, tenant=self.org
        )
        self.milestone = Milestone.objects.create(
            name="Test Milestone",
            tenant=self.org,
            project=self.project,
            status="active",
            progress=50,
        )

    def test_list_milestones(self):
        """Test listing milestones"""
        response = self.client.get("/api/milestones/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("project_name", response.data["results"][0])
        self.assertIn("sprints_count", response.data["results"][0])

    def test_create_milestone(self):
        """Test creating milestone"""
        data = {
            "name": "New Milestone",
            "project": self.project.slug,
            "status": "planning",
            "progress": 0,
        }
        response = self.client.post("/api/milestones/", data, format="json")
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_milestone_validation(self):
        """Test milestone progress validation"""
        data = {
            "name": "Invalid Milestone",
            "project": self.project.slug,
            "progress": 150,  # Invalid: > 100
        }
        response = self.client.post("/api/milestones/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SprintAPITests(APITestCase):
    """Test Sprint API endpoints"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="testpass"
        )
        self.group = Group.objects.create(name="API Control Administrators")
        self.user.groups.add(self.group)
        self.client.force_authenticate(user=self.user)

        self.org = Tenant.objects.create(name="Test Org")
        # Create UserTenant association
        from accounts.models import UserTenant

        UserTenant.objects.create(user=self.user, tenant=self.org, is_owner=True, is_approved=True)
        self.client_obj = Client.objects.create(
            name="Test Client", email="test@example.com", tenant=self.org
        )
        self.project = Project.objects.create(
            name="Test Project", client=self.client_obj, tenant=self.org
        )
        self.invoice = Invoice.objects.create(
            client=self.client_obj, project=self.project, amount=Decimal("15000.00")
        )

    def test_list_invoices(self):
        """Test listing invoices"""
        response = self.client.get("/api/invoices/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("client_name", response.data[0])

    def test_create_invoice(self):
        """Test creating invoice"""
        data = {"client": self.client_obj.id, "project": self.project.id, "amount": "25000.00"}
        response = self.client.post("/api/invoices/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invoice_filtering(self):
        """Test invoice filtering"""
        # Filter by paid status
        response = self.client.get("/api/invoices/?paid=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class PaymentAPITests(APITestCase):
    """Test Payment API endpoints"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="testpass"
        )
        self.group = Group.objects.create(name="API Control Administrators")
        self.user.groups.add(self.group)
        self.client.force_authenticate(user=self.user)

        self.org = Tenant.objects.create(name="Test Org")
        # Create UserTenant association
        from accounts.models import UserTenant

        UserTenant.objects.create(user=self.user, tenant=self.org, is_owner=True, is_approved=True)
        self.client_obj = Client.objects.create(
            name="Test Client", email="test@example.com", tenant=self.org
        )
        self.project = Project.objects.create(
            name="Test Project", client=self.client_obj, tenant=self.org
        )
        self.invoice = Invoice.objects.create(
            tenant=self.org,
            client=self.client_obj,
            project=self.project,
            amount=Decimal("15000.00"),
        )
        self.payment = Payment.objects.create(
            tenant=self.org, invoice=self.invoice, amount=Decimal("15000.00")
        )

    def test_list_payments(self):
        """Test listing payments"""
        response = self.client.get("/api/payments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("invoice_id", response.data["results"][0])

    def test_create_payment(self):
        """Test creating payment"""
        data = {"invoice": self.invoice.id, "amount": "7500.00"}
        response = self.client.post("/api/payments/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PermissionTests(APITestCase):
    """Test permission controls"""

    def setUp(self):
        # Create users with different permissions
        self.regular_user = CustomUser.objects.create_user(
            email="regular@example.com", password="pass"
        )
        self.client_manager = CustomUser.objects.create_user(
            email="client_mgr@example.com", password="pass"
        )
        self.project_manager = CustomUser.objects.create_user(
            email="project_mgr@example.com", password="pass"
        )
        self.api_manager = CustomUser.objects.create_user(
            email="api_mgr@example.com", password="pass"
        )

        # Use the default groups created by migration
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        from project.models import Client, Invoice, Project

        tenant_owners_group, _ = Group.objects.get_or_create(name="Tenant Owners")
        project_managers_group, _ = Group.objects.get_or_create(name="Project Managers")

        # Manually assign permissions to groups for testing
        # Client permissions
        client_content_type = ContentType.objects.get_for_model(Client)
        for perm_codename in ["add_client", "change_client", "delete_client", "view_client"]:
            try:
                perm = Permission.objects.get(
                    content_type=client_content_type, codename=perm_codename
                )
                tenant_owners_group.permissions.add(perm)
                if perm_codename in [
                    "add_client",
                    "change_client",
                    "view_client",
                ]:  # Project managers can view/add/change clients
                    project_managers_group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass

        # Project permissions
        project_content_type = ContentType.objects.get_for_model(Project)
        for perm_codename in ["add_project", "change_project", "delete_project", "view_project"]:
            try:
                perm = Permission.objects.get(
                    content_type=project_content_type, codename=perm_codename
                )
                tenant_owners_group.permissions.add(perm)
                project_managers_group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass

        # Invoice permissions
        invoice_content_type = ContentType.objects.get_for_model(Invoice)
        for perm_codename in ["add_invoice", "change_invoice", "delete_invoice", "view_invoice"]:
            try:
                perm = Permission.objects.get(
                    content_type=invoice_content_type, codename=perm_codename
                )
                tenant_owners_group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass

        # Assign users to appropriate groups
        self.client_manager.groups.add(tenant_owners_group)
        self.project_manager.groups.add(project_managers_group)
        self.api_manager.groups.add(tenant_owners_group)
        # regular_user gets no special groups - should have limited access

        # Create test data
        self.org = Tenant.objects.create(name="Test Org")
        self.client_obj = Client.objects.create(
            name="Test Client", email="test@example.com", tenant=self.org
        )
        self.project = Project.objects.create(
            name="Test Project", client=self.client_obj, tenant=self.org
        )
        self.invoice = Invoice.objects.create(
            client=self.client_obj, project=self.project, tenant=self.org, amount=Decimal("1000.00")
        )

        # Create UserTenant relationships for the test users
        from accounts.models import UserTenant

        UserTenant.objects.create(
            user=self.client_manager,
            tenant=self.org,
            is_owner=True,
            is_approved=True,
            role="Tenant Owner",
        )
        UserTenant.objects.create(
            user=self.project_manager,
            tenant=self.org,
            is_owner=False,
            is_approved=True,
            role="Manager",
        )
        UserTenant.objects.create(
            user=self.api_manager,
            tenant=self.org,
            is_owner=True,
            is_approved=True,
            role="Tenant Owner",
        )
        # regular_user has no UserTenant relationship - should have no access

    def test_client_permissions(self):
        """Test client management permissions"""
        # Regular user should not access clients
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/clients/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Client manager should access clients
        self.client.force_authenticate(user=self.client_manager)
        response = self.client.get("/api/clients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_permissions(self):
        """Test project management permissions"""
        # Regular user should not access projects
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Project manager should access projects
        self.client.force_authenticate(user=self.project_manager)
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoice_permissions(self):
        """Test invoice permissions"""
        # Regular user should not access invoices
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/invoices/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # API manager should access invoices
        self.client.force_authenticate(user=self.api_manager)
        response = self.client.get("/api/invoices/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_endpoints(self):
        """Test endpoints that don't require special permissions"""
        self.client.force_authenticate(user=self.regular_user)

        # Tenants should be accessible
        response = self.client.get("/api/tenants/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Milestones should be accessible
        response = self.client.get("/api/milestones/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GroupTests(TestCase):
    """Test default groups and group assignment"""

    def setUp(self):
        from django.core.management import call_command

        call_command("setup_groups")

    def test_default_groups_created(self):
        """Test that default groups are created"""
        from django.contrib.auth.models import Group

        default_groups = [
            "Tenant Owners",
            "Project Managers",
            "Employees",
            "Clients",
            "Administrators",
        ]

        for group_name in default_groups:
            self.assertTrue(Group.objects.filter(name=group_name).exists())

    def test_user_group_assignment_on_signup(self):
        """Test that users are assigned to appropriate groups during signup"""
        # This would require testing the signup API
        # For now, just check that groups exist
        from django.contrib.auth.models import Group

        self.assertTrue(Group.objects.filter(name="Tenant Owners").exists())


class ErrorHandlingTests(APITestCase):
    """Test error handling and edge cases"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="testpass"
        )
        self.client.force_authenticate(user=self.user)

    def test_not_found(self):
        """Test 404 responses"""
        response = self.client.get("/api/organizations/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        """Test unauthenticated access"""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/tenants/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BulkOperationsAPITests(APITestCase):
    """Test bulk operations endpoints"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="testpass"
        )
        # Assign Tenant Owners group which has all permissions
        self.group, created = Group.objects.get_or_create(name="Tenant Owners")
        self.user.groups.add(self.group)
        # Also assign permissions directly for test
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        client_content_type = ContentType.objects.get_for_model(Client)
        project_content_type = ContentType.objects.get_for_model(Project)
        task_content_type = ContentType.objects.get_for_model(Task)
        permissions = Permission.objects.filter(
            content_type__in=[client_content_type, project_content_type, task_content_type],
            codename__in=[
                "add_client",
                "change_client",
                "delete_client",
                "view_client",
                "add_project",
                "change_project",
                "delete_project",
                "view_project",
                "add_task",
                "change_task",
                "delete_task",
                "view_task",
            ],
        )
        self.user.user_permissions.add(*permissions)
        self.client.force_authenticate(user=self.user)

        self.org = Tenant.objects.create(name="Test Org")
        # Create UserTenant association
        from accounts.models import UserTenant

        UserTenant.objects.create(user=self.user, tenant=self.org, is_owner=True, is_approved=True)

        # Create test data
        self.client_obj1 = Client.objects.create(
            name="Test Client 1", email="client1@example.com", tenant=self.org
        )
        self.client_obj2 = Client.objects.create(
            name="Test Client 2", email="client2@example.com", tenant=self.org
        )
        # Clients without projects for bulk delete test
        self.client_obj3 = Client.objects.create(
            name="Test Client 3", email="client3@example.com", tenant=self.org
        )
        self.client_obj4 = Client.objects.create(
            name="Test Client 4", email="client4@example.com", tenant=self.org
        )
        self.project1 = Project.objects.create(
            name="Test Project 1", client=self.client_obj1, tenant=self.org
        )
        self.project2 = Project.objects.create(
            name="Test Project 2", client=self.client_obj2, tenant=self.org
        )
        self.milestone = Milestone.objects.create(
            name="Test Milestone", project=self.project1, tenant=self.org
        )
        self.task1 = Task.objects.create(
            title="Test Task 1", milestone=self.milestone, tenant=self.org
        )
        self.task2 = Task.objects.create(
            title="Test Task 2", milestone=self.milestone, tenant=self.org
        )

    def test_bulk_delete_clients_success(self):
        """Test successful bulk delete of clients"""
        data = {"client_ids": [self.client_obj3.id, self.client_obj4.id]}
        response = self.client.post("/api/clients/bulk_delete_clients/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["deleted_count"], 2)
        self.assertIn("Successfully deleted 2 clients", response.data["message"])

        # Verify clients were hard deleted
        self.assertFalse(Client.objects.filter(id=self.client_obj3.id).exists())
        self.assertFalse(Client.objects.filter(id=self.client_obj4.id).exists())

    def test_bulk_delete_clients_with_projects(self):
        """Test bulk delete clients fails when they have associated projects"""
        data = {"client_ids": [self.client_obj1.id]}  # client_obj1 has project1
        response = self.client.post("/api/clients/bulk_delete_clients/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot delete clients with associated projects", response.data["error"])
        self.assertIn("has associated projects", str(response.data["details"]))

        # Verify client was not deleted (hard delete, so still exists)
        client1 = Client.objects.get(id=self.client_obj1.id)
        self.assertTrue(client1.id == self.client_obj1.id)

    def test_bulk_delete_clients_empty_list(self):
        """Test bulk delete clients with empty list"""
        data = {"client_ids": []}
        response = self.client.post("/api/clients/bulk_delete_clients/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("client_ids are required", response.data["error"])

    def test_bulk_delete_clients_invalid_ids(self):
        """Test bulk delete clients with invalid IDs"""
        data = {"client_ids": [999, 998]}  # Non-existent IDs
        response = self.client.post("/api/clients/bulk_delete_clients/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("No valid clients found", response.data["error"])

    def test_bulk_delete_projects_success(self):
        """Test successful bulk delete of projects"""
        data = {"project_ids": [self.project1.id, self.project2.id]}
        response = self.client.post("/api/projects/bulk_delete_projects/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["deleted_count"], 2)
        self.assertIn("Successfully deleted 2 projects", response.data["message"])

        # Verify projects were soft deleted (not in default queryset)
        self.assertFalse(Project.objects.filter(id=self.project1.id).exists())
        self.assertFalse(Project.objects.filter(id=self.project2.id).exists())
        # But they exist in all objects with is_deleted=True
        project1 = Project.all_objects.get(id=self.project1.id)
        project2 = Project.all_objects.get(id=self.project2.id)
        self.assertTrue(project1.is_deleted)
        self.assertTrue(project2.is_deleted)

    def test_bulk_delete_projects_with_invoices(self):
        """Test bulk delete projects fails when they have associated invoices"""
        # Create invoice for project1
        Invoice.objects.create(
            client=self.client_obj1,
            project=self.project1,
            tenant=self.org,
            amount=Decimal("1000.00"),
        )

        data = {"project_ids": [self.project1.id]}
        response = self.client.post("/api/projects/bulk_delete_projects/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot delete projects with associated invoices", response.data["error"])
        self.assertIn("has associated invoices", str(response.data["details"]))

        # Verify project was not soft deleted
        project1 = Project.objects.get(id=self.project1.id)
        self.assertFalse(project1.is_deleted)

    def test_bulk_delete_projects_empty_list(self):
        """Test bulk delete projects with empty list"""
        data = {"project_ids": []}
        response = self.client.post("/api/projects/bulk_delete_projects/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("project_ids are required", response.data["error"])

    def test_bulk_delete_tasks_success(self):
        """Test successful bulk delete of tasks"""
        data = {"task_ids": [self.task1.id, self.task2.id]}
        response = self.client.post("/api/tasks/bulk_delete_tasks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["deleted_count"], 2)
        self.assertIn("Successfully deleted 2 tasks", response.data["message"])

        # Verify tasks were soft deleted (not in default queryset)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())
        self.assertFalse(Task.objects.filter(id=self.task2.id).exists())
        # But they exist in all objects with is_deleted=True
        task1 = Task.all_objects.get(id=self.task1.id)
        task2 = Task.all_objects.get(id=self.task2.id)
        self.assertTrue(task1.is_deleted)
        self.assertTrue(task2.is_deleted)


class ExcelExportImportTests(APITestCase):
    """Test Excel export and import functionality"""

    def setUp(self):
        # Create user with proper permissions
        self.user = CustomUser.objects.create_user(
            email="exceltest@example.com", password="testpass"
        )
        # Assign necessary permissions
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        content_types = ContentType.objects.filter(app_label="project")
        permissions = Permission.objects.filter(
            content_type__in=content_types,
            codename__in=["view_client", "view_project", "view_task"],
        )
        self.user.user_permissions.add(*permissions)
        self.client.force_authenticate(user=self.user)

        # Create tenant and association
        self.org = Tenant.objects.create(name="Excel Test Org")
        UserTenant.objects.create(user=self.user, tenant=self.org, is_owner=True, is_approved=True)

        # Create test data
        self.client_obj = Client.objects.create(
            name="Test Client", email="test@example.com", tenant=self.org, status="active"
        )
        self.project = Project.objects.create(
            name="Test Project",
            client=self.client_obj,
            tenant=self.org,
            status="active",
            priority="high",
            budget=Decimal("10000.00"),
        )
        self.milestone = Milestone.objects.create(
            name="Test Milestone", project=self.project, tenant=self.org, status="active"
        )
        self.task = Task.objects.create(
            title="Test Task", milestone=self.milestone, tenant=self.org, status="to_do"
        )

    def test_client_export(self):
        """Test client Excel export"""
        response = self.client.get("/api/excel-export/?model=clients")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn('attachment; filename="clients_export.xlsx"', response["Content-Disposition"])
        # Check that response has content
        self.assertGreater(len(response.content), 0)

    def test_project_export(self):
        """Test project Excel export"""
        response = self.client.get("/api/excel-export/?model=projects")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn(
            'attachment; filename="projects_export.xlsx"', response["Content-Disposition"]
        )
        # Check that response has content
        self.assertGreater(len(response.content), 0)

    def test_task_export(self):
        """Test task Excel export"""
        response = self.client.get("/api/excel-export/?model=tasks")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn('attachment; filename="tasks_export.xlsx"', response["Content-Disposition"])
        # Check that response has content
        self.assertGreater(len(response.content), 0)

    def test_export_invalid_type(self):
        """Test export with invalid type"""
        response = self.client.get("/api/excel-export/?model=invalid")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_export_missing_type(self):
        """Test export without type parameter"""
        response = self.client.get("/api/excel-export/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_bulk_delete_tasks_empty_list(self):
        """Test bulk delete tasks with empty list"""
        data = {"task_ids": []}
        response = self.client.post("/api/tasks/bulk_delete_tasks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("task_ids are required", response.data["error"])
