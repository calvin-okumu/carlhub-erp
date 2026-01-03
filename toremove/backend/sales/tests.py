"""
Tests for sales app.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.factories import TenantFactory, TenantOwnerFactory, UserFactory
from sales.models import Customer


class SalesAPITestCase(APITestCase):
    """Test cases for sales API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.tenant = TenantFactory()
        self.user = UserFactory()
        TenantOwnerFactory(user=self.user, tenant=self.tenant)
        self.client.force_authenticate(user=self.user)

    def test_customer_crud(self):
        """Test customer CRUD operations."""
        # Create
        customer_data = {
            "name": "Test Customer",
            "email": "test@example.com",
            "company_name": "Test Company",
            "status": "prospect",
            "lead_score": 50,
            "estimated_value": "10000.00",
        }
        response = self.client.post("/api/sales/customers/", customer_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        customer_id = response.data["id"]

        # Read
        response = self.client.get(f"/api/sales/customers/{customer_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Customer")

        # Update
        update_data = {"name": "Updated Customer"}
        response = self.client.patch(
            f"/api/sales/customers/{customer_id}/", update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Customer")

        # Delete
        response = self.client.delete(f"/api/sales/customers/{customer_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_opportunity_crud(self):
        """Test opportunity CRUD operations."""
        # Create customer first
        customer = Customer.objects.create(
            name="Test Customer", email="test@example.com", tenant=self.tenant, created_by=self.user
        )

        # Create
        opportunity_data = {
            "title": "Test Opportunity",
            "customer": str(customer.id),
            "stage": "prospecting",
            "value": "50000.00",
            "probability": 30,
        }
        response = self.client.post("/api/sales/opportunities/", opportunity_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        opportunity_id = response.data["id"]

        # Read
        response = self.client.get(f"/api/sales/opportunities/{opportunity_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Opportunity")

    def test_analytics_endpoint(self):
        """Test analytics endpoint."""
        response = self.client.get("/api/sales/analytics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_customers", response.data)
        self.assertIn("active_opportunities", response.data)
