"""
Test cases for tenant context resolution in leave management serializers.
"""
import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser, Tenant, UserTenant, Invitation
from .models import LeaveBalance, LeavePolicy, LeaveRequest


class TenantContextResolutionTests(APITestCase):
    """Test tenant context resolution for different user states."""

    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name="Test Company",
            domain="testcompany.com"
        )
        self.owner = CustomUser.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="testpass123"
        )
        UserTenant.objects.create(
            user=self.owner,
            tenant=self.tenant,
            is_owner=True,
            is_approved=True
        )

        # Create a leave policy for testing
        LeavePolicy.objects.create(
            tenant=self.tenant,
            leave_type='annual_leave',
            annual_entitlement=Decimal('25.0'),
            max_consecutive_days=30,
            notice_period_days=7
        )

    def test_approved_user_can_create_leave_request(self):
        """Test that approved users can create leave requests."""
        # Create approved user
        approved_user = CustomUser.objects.create_user(
            username="approved",
            email="approved@example.com",
            password="testpass123"
        )
        UserTenant.objects.create(
            user=approved_user,
            tenant=self.tenant,
            is_approved=True
        )

        self.client.force_authenticate(user=approved_user)
        
        data = {
            'leave_type': 'annual_leave',
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
            'reason': 'Vacation time'
        }

        response = self.client.post('/api/leave/requests/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LeaveRequest.objects.count(), 1)

    def test_unapproved_user_cannot_create_leave_request(self):
        """Test that unapproved users cannot create leave requests."""
        # Create unapproved user
        unapproved_user = CustomUser.objects.create_user(
            username="unapproved",
            email="unapproved@example.com",
            password="testpass123"
        )
        UserTenant.objects.create(
            user=unapproved_user,
            tenant=self.tenant,
            is_approved=False
        )

        self.client.force_authenticate(user=unapproved_user)
        
        data = {
            'leave_type': 'annual_leave',
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
            'reason': 'Vacation time'
        }

        response = self.client.post('/api/leave/requests/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # The error is nested in the response data
        error_detail = response.data[0] if isinstance(response.data, list) else response.data
        if isinstance(error_detail, dict) and 'string' in error_detail:
            error_message = error_detail['string']
        else:
            error_message = str(error_detail)
        self.assertIn('pending approval', error_message)

    def test_user_with_pending_invitation_cannot_create_leave_request(self):
        """Test that users with pending invitations cannot create leave requests."""
        # Create user with invitation but no UserTenant
        invited_user = CustomUser.objects.create_user(
            username="invited",
            email="invited@example.com",
            password="testpass123"
        )
        
        # Create pending invitation
        Invitation.objects.create(
            email='invited@example.com',
            tenant=self.tenant,
            token='test-token-123',
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7)
        )

        self.client.force_authenticate(user=invited_user)
        
        data = {
            'leave_type': 'annual_leave',
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
            'reason': 'Vacation time'
        }

        response = self.client.post('/api/leave/requests/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Extract error message from nested structure
        error_detail = response.data[0] if isinstance(response.data, list) else response.data
        if isinstance(error_detail, dict) and 'string' in error_detail:
            error_message = error_detail['string']
        else:
            error_message = str(error_detail)
        self.assertIn('pending invitations', error_message)

    def test_user_with_expired_invitation_cannot_create_leave_request(self):
        """Test that users with expired invitations cannot create leave requests."""
        # Create user with expired invitation
        expired_user = CustomUser.objects.create_user(
            username="expired",
            email="expired@example.com",
            password="testpass123"
        )
        
        # Create expired invitation
        Invitation.objects.create(
            email='expired@example.com',
            tenant=self.tenant,
            token='test-token-expired',
            invited_by=self.owner,
            expires_at=timezone.now() - timedelta(days=1)  # Expired yesterday
        )

        self.client.force_authenticate(user=expired_user)
        
        data = {
            'leave_type': 'annual_leave',
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
            'reason': 'Vacation time'
        }

        response = self.client.post('/api/leave/requests/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Extract error message from nested structure
        error_detail = response.data[0] if isinstance(response.data, list) else response.data
        if isinstance(error_detail, dict) and 'string' in error_detail:
            error_message = error_detail['string']
        else:
            error_message = str(error_detail)
        self.assertIn('expired', error_message)

    def test_user_with_no_tenant_membership_cannot_create_leave_request(self):
        """Test that users with no tenant membership cannot create leave requests."""
        # Create user with no UserTenant or invitations
        orphan_user = CustomUser.objects.create_user(
            username="orphan",
            email="orphan@example.com",
            password="testpass123"
        )

        self.client.force_authenticate(user=orphan_user)
        
        data = {
            'leave_type': 'annual_leave',
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
            'reason': 'Vacation time'
        }

        response = self.client.post('/api/leave/requests/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Extract error message from nested structure
        error_detail = response.data[0] if isinstance(response.data, list) else response.data
        if isinstance(error_detail, dict) and 'string' in error_detail:
            error_message = error_detail['string']
        else:
            error_message = str(error_detail)
        self.assertIn('not a member of any tenant', error_message)

    def test_leave_policy_creation_tenant_context(self):
        """Test tenant context resolution for leave policy creation."""
        # Test with unapproved user
        unapproved_user = CustomUser.objects.create_user(
            username="unapproved_policy",
            email="unapproved_policy@example.com",
            password="testpass123"
        )
        UserTenant.objects.create(
            user=unapproved_user,
            tenant=self.tenant,
            is_approved=False
        )

        # Add permissions for leave policy management
        from django.contrib.auth.models import Permission
        unapproved_user.user_permissions.add(
            Permission.objects.get(codename='add_leavepolicy'),
        )

        self.client.force_authenticate(user=unapproved_user)
        
        data = {
            'leave_type': 'sick_leave',
            'annual_entitlement': '10.0',
            'max_consecutive_days': 5,
            'notice_period_days': 1
        }

        response = self.client.post('/api/leave/policies/', data, format='json')
        # Should be 400 (tenant context error) not 403 (permission error)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Extract error message from nested structure
        error_detail = response.data[0] if isinstance(response.data, list) else response.data
        if isinstance(error_detail, dict) and 'string' in error_detail:
            error_message = error_detail['string']
        else:
            error_message = str(error_detail)
        self.assertIn('pending approval', error_message)

    def test_multiple_pending_invitations_error_message(self):
        """Test error message when user has multiple pending invitations."""
        # Create second tenant
        tenant2 = Tenant.objects.create(
            name="Second Company",
            domain="secondcompany.com"
        )
        
        # Create user with multiple invitations
        multi_user = CustomUser.objects.create_user(
            username="multi",
            email="multi@example.com",
            password="testpass123"
        )
        
        # Create multiple invitations
        Invitation.objects.create(
            email='multi@example.com',
            tenant=self.tenant,
            token='test-token-1',
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        Invitation.objects.create(
            email='multi@example.com',
            tenant=tenant2,
            token='test-token-2',
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=5)
        )

        self.client.force_authenticate(user=multi_user)
        
        data = {
            'leave_type': 'annual_leave',
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
            'reason': 'Vacation time'
        }

        response = self.client.post('/api/leave/requests/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Extract error message from nested structure
        error_detail = response.data[0] if isinstance(response.data, list) else response.data
        if isinstance(error_detail, dict) and 'string' in error_detail:
            error_message = error_detail['string']
        else:
            error_message = str(error_detail)
        self.assertIn('pending invitations', error_message)
        self.assertIn('Test Company', error_message)
        self.assertIn('Second Company', error_message)