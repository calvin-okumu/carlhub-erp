from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser, EmployeeDocument, Tenant, UserProfile, UserTenant


class UserProfileModelTests(TestCase):
    """Test UserProfile model"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com", password="testpass123", first_name="Test", last_name="User"
        )
        self.tenant = Tenant.objects.create(name="Test Tenant", domain="test.example.com")
        self.user_tenant = UserTenant.objects.create(
            user=self.user, tenant=self.tenant, is_owner=True, is_approved=True
        )

    def test_profile_creation_for_owner(self):
        """Test that profile is created for tenant owner"""
        # Profile should be created automatically via signal
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(str(profile), f"{self.user.email} - Profile")

    def test_profile_creation_for_approved_member(self):
        """Test that profile is created when member is approved"""
        # Create another user
        user2 = CustomUser.objects.create_user(
            email="member@example.com",
            password="testpass123",
            first_name="Member",
            last_name="User",
        )
        # Create UserTenant as non-owner, not approved
        user_tenant2 = UserTenant.objects.create(
            user=user2, tenant=self.tenant, is_owner=False, is_approved=False
        )

        # Initially no profile should exist
        self.assertFalse(UserProfile.objects.filter(user=user2).exists())

        # Approve the member
        user_tenant2.is_approved = True
        user_tenant2.save()

        # Profile should now exist
        profile = UserProfile.objects.get(user=user2)
        self.assertEqual(profile.user, user2)


class EmployeeDocumentModelTests(TestCase):
    """Test EmployeeDocument model"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(email="test@example.com", password="testpass123")

    def test_document_creation(self):
        """Test document model creation"""
        from django.core.files.base import ContentFile

        document = EmployeeDocument.objects.create(
            user=self.user,
            title="Test Document",
            description="Test description",
            document_file=ContentFile(b"test content", name="test.pdf"),
        )

        self.assertEqual(document.user, self.user)
        self.assertEqual(document.title, "Test Document")
        self.assertEqual(str(document), f"{self.user.email} - Test Document")

    def test_document_file_save(self):
        """Test file metadata is set on save"""
        from django.core.files.base import ContentFile

        document = EmployeeDocument(
            user=self.user,
            title="Test Document",
            document_file=ContentFile(b"test content", name="test.pdf"),
        )
        document.save()

        # File metadata should be set
        self.assertEqual(document.file_type, "pdf")
        self.assertEqual(document.file_size, 12)  # 'test content' is 12 bytes


class UserProfileAPITests(APITestCase):
    """Test UserProfile API endpoints"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=self.user)

        # Create tenant and user-tenant relationship
        self.tenant = Tenant.objects.create(name="Test Tenant", domain="test.example.com")
        UserTenant.objects.create(
            user=self.user, tenant=self.tenant, is_owner=True, is_approved=True
        )

    def test_get_profile(self):
        """Test retrieving user profile"""
        response = self.client.get("/api/accounts/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user.id)

    def test_update_profile(self):
        """Test updating user profile"""
        data = {
            "job_title": "Software Engineer",
            "phone": "+1234567890",
            "street_address": "123 Test St",
            "city": "Test City",
        }
        response = self.client.put("/api/accounts/profile/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["job_title"], "Software Engineer")

    def test_profile_not_found_for_unapproved_user(self):
        """Test that unapproved users don't get profiles"""
        # Create unapproved user
        unapproved_user = CustomUser.objects.create_user(
            email="unapproved@example.com", password="testpass123"
        )
        UserTenant.objects.create(
            user=unapproved_user, tenant=self.tenant, is_owner=False, is_approved=False
        )

        # Try to access profile as unapproved user
        self.client.force_authenticate(user=unapproved_user)
        # This should raise an exception since no profile exists
        with self.assertRaises(Exception):
            self.client.get("/api/accounts/profile/")


class EmployeeDocumentAPITests(APITestCase):
    """Test EmployeeDocument API endpoints"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=self.user)

        # Create tenant and user-tenant relationship
        self.tenant = Tenant.objects.create(name="Test Tenant", domain="test.example.com")
        UserTenant.objects.create(
            user=self.user, tenant=self.tenant, is_owner=True, is_approved=True
        )

    def test_list_documents(self):
        """Test listing user documents"""
        response = self.client.get("/api/accounts/documents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check paginated response format
        self.assertIsInstance(response.data, dict)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIsInstance(response.data["results"], list)

    def test_create_document(self):
        """Test creating a document"""
        from io import BytesIO


        # Create a simple PDF-like file for testing
        file_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        file = BytesIO(file_content)
        file.name = "test.pdf"

        data = {"title": "Test Document", "description": "Test description", "document_file": file}
        response = self.client.post("/api/accounts/documents/", data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Test Document")
        self.assertEqual(response.data["user"], self.user.id)

    def test_document_permissions(self):
        """Test that users can only access their own documents"""
        from django.core.files.base import ContentFile

        # Create another user
        other_user = CustomUser.objects.create_user(
            email="other@example.com", password="testpass123"
        )
        UserTenant.objects.create(
            user=other_user, tenant=self.tenant, is_owner=True, is_approved=True
        )

        # Create document for other user
        doc = EmployeeDocument.objects.create(
            user=other_user,
            title="Other User Document",
            document_file=ContentFile(b"test", name="other.pdf"),
        )

        # Try to access as first user
        response = self.client.get(f"/api/accounts/documents/{doc.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
