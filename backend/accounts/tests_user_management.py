"""
Tests for user management functionality including invitations and audit logging.
"""
import json
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import AuditLog, CustomUser, Invitation, Tenant, UserTenant, UserProfile


class InvitationModelTests(TestCase):
    """Test Invitation model functionality"""

    def setUp(self):
        self.tenant = Tenant.objects.create(
            name='Test Tenant',
            domain='test.example.com'
        )
        self.invited_by = CustomUser.objects.create_user(
            email='inviter@example.com',
            password='testpass123',
            first_name='Inviter',
            last_name='User'
        )
        UserTenant.objects.create(
            user=self.invited_by,
            tenant=self.tenant,
            is_owner=True,
            is_approved=True
        )

    def test_invitation_creation(self):
        """Test creating an invitation"""
        invitation = Invitation.objects.create(
            email='invited@example.com',
            tenant=self.tenant,
            invited_by=self.invited_by,
            role='Employee',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7)
        )

        self.assertEqual(invitation.email, 'invited@example.com')
        self.assertEqual(invitation.tenant, self.tenant)
        self.assertEqual(invitation.invited_by, self.invited_by)
        self.assertEqual(invitation.role, 'Employee')
        self.assertFalse(invitation.email_confirmed)
        self.assertFalse(invitation.is_used)

    def test_invitation_expiration(self):
        """Test invitation expiration"""
        expired_invitation = Invitation.objects.create(
            email='expired@example.com',
            tenant=self.tenant,
            invited_by=self.invited_by,
            role='Employee',
            token='expired-token',
            expires_at=timezone.now() - timedelta(days=1)  # Already expired
        )

        # Should not be valid
        self.assertTrue(expired_invitation.is_expired())

        valid_invitation = Invitation.objects.create(
            email='valid@example.com',
            tenant=self.tenant,
            invited_by=self.invited_by,
            role='Employee',
            token='valid-token',
            expires_at=timezone.now() + timedelta(days=1)  # Still valid
        )

        # Should be valid
        self.assertFalse(valid_invitation.is_expired())


class InvitationAPITests(APITestCase):
    """Test invitation API endpoints"""

    def setUp(self):
        # Create tenant and owner
        self.tenant = Tenant.objects.create(
            name='Test Tenant',
            domain='test.example.com'
        )
        self.owner = CustomUser.objects.create_user(
            email='owner@example.com',
            password='testpass123',
            first_name='Owner',
            last_name='User'
        )
        UserTenant.objects.create(
            user=self.owner,
            tenant=self.tenant,
            is_owner=True,
            is_approved=True
        )

        # Authenticate as owner
        self.client.force_authenticate(user=self.owner)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_invite_member(self):
        """Test inviting a team member"""
        url = reverse('invite_member')
        data = {
            'email': 'newmember@example.com',
            'role': 'Employee'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

        # Check invitation was created
        invitation = Invitation.objects.get(email='newmember@example.com')
        self.assertEqual(invitation.tenant, self.tenant)
        self.assertEqual(invitation.invited_by, self.owner)
        self.assertEqual(invitation.role, 'Employee')
        self.assertFalse(invitation.email_confirmed)

        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('newmember@example.com', mail.outbox[0].to)
        self.assertIn('Invitation to join', mail.outbox[0].subject)

    def test_invite_existing_user_from_different_tenant_succeeds(self):
        """Test that inviting an existing user from a different tenant succeeds"""
        # Create another user in a different tenant
        other_tenant = Tenant.objects.create(name="Other Tenant", domain="other.com")
        existing_user = CustomUser.objects.create_user(
            email='existing@example.com',
            password='password123',
            first_name='Existing',
            last_name='User'
        )
        UserTenant.objects.create(
            user=existing_user,
            tenant=other_tenant,
            is_owner=True,
            is_approved=True
        )

        url = reverse('invite_member')
        data = {
            'email': 'existing@example.com',  # This user exists in another tenant
            'role': 'Employee'
        }

        response = self.client.post(url, data, format='json')

        # Should succeed with 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

        # Invitation should be created
        invitation = Invitation.objects.get(email='existing@example.com')
        self.assertEqual(invitation.tenant, self.tenant)
        self.assertEqual(invitation.invited_by, self.owner)

        # Email should be sent
        self.assertEqual(len(mail.outbox), 1)

    def test_invite_user_already_in_same_tenant_fails(self):
        """Test that inviting a user already in the same tenant fails"""
        # Create a user already in this tenant
        existing_member = CustomUser.objects.create_user(
            email='member@example.com',
            password='password123',
            first_name='Existing',
            last_name='Member'
        )
        UserTenant.objects.create(
            user=existing_member,
            tenant=self.tenant,
            is_approved=True
        )

        url = reverse('invite_member')
        data = {
            'email': 'member@example.com',  # This user is already in this tenant
            'role': 'Employee'
        }

        response = self.client.post(url, data, format='json')

        # Should fail with 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'User is already a member of this tenant')

        # No invitation should be created
        self.assertFalse(Invitation.objects.filter(email='member@example.com').exists())

        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_invite_user_with_pending_invitation_fails(self):
        """Test that inviting a user with a pending invitation in the same tenant fails"""
        # Create a pending invitation
        Invitation.objects.create(
            email='pending@example.com',
            tenant=self.tenant,
            invited_by=self.owner,
            role='Employee',
            token='pending-token-123',
            expires_at=timezone.now() + timedelta(days=7)
        )

        url = reverse('invite_member')
        data = {
            'email': 'pending@example.com',  # Same email as pending invitation
            'role': 'Employee'
        }

        response = self.client.post(url, data, format='json')

        # Should fail with 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'An invitation is already pending for this email in this tenant')

        # No new invitation should be created
        self.assertEqual(Invitation.objects.filter(email='pending@example.com').count(), 1)

        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_resend_invitation(self):
        """Test resending an invitation"""
        invitation = Invitation.objects.create(
            email='resend@example.com',
            tenant=self.tenant,
            invited_by=self.owner,
            role='Employee',
            token='resend-token-123',
            expires_at=timezone.now() + timedelta(days=7)
        )

        url = reverse('resend_invitation')
        data = {'token': 'resend-token-123'}

        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('resent successfully', response.data['message'])

        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('resend@example.com', mail.outbox[0].to)
        self.assertIn('(Resent)', mail.outbox[0].subject)

    def test_resend_confirmed_invitation_fails(self):
        """Test that resending a confirmed invitation fails"""
        invitation = Invitation.objects.create(
            email='confirmed@example.com',
            tenant=self.tenant,
            invited_by=self.owner,
            role='Employee',
            token='confirmed-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            email_confirmed=True  # Already confirmed
        )

        url = reverse('resend_invitation')
        data = {'token': 'confirmed-token-123'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already confirmed', response.data['error'])

    def test_confirm_invalid_token(self):
        """Test confirming with invalid token"""
        url = reverse('confirm_invitation')
        data = {'token': 'invalid-token'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid or expired', response.data['error'])


class SignupAPITests(APITestCase):
    """Test user signup functionality"""

    def setUp(self):
        self.tenant = Tenant.objects.create(
            name='Test Tenant',
            domain='test.example.com'
        )
        self.invited_by = CustomUser.objects.create_user(
            email='inviter@example.com',
            password='testpass123',
            first_name='Inviter',
            last_name='User'
        )
        UserTenant.objects.create(
            user=self.invited_by,
            tenant=self.tenant,
            is_owner=True,
            is_approved=True
        )

    def test_signup_with_valid_invitation(self):
        """Test signing up with a valid confirmed invitation"""
        invitation = Invitation.objects.create(
            email='signup@example.com',
            tenant=self.tenant,
            invited_by=self.invited_by,
            role='Employee',
            token='signup-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            email_confirmed=True
        )

        url = reverse('signup')
        data = {
            'email': 'signup@example.com',
            'password': 'securepass123',
            'first_name': 'New',
            'last_name': 'User',
            'invitation_token': 'signup-token-123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

        # Check user was created
        user = CustomUser.objects.get(email='signup@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')

        # Check user-tenant relationship
        user_tenant = UserTenant.objects.get(user=user, tenant=self.tenant)
        self.assertTrue(user_tenant.is_approved)
        self.assertEqual(user_tenant.role, 'Employee')

        # Check profile was created
        profile = UserProfile.objects.get(user=user)
        self.assertIsNotNone(profile)

        # Check invitation was marked as used
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_used)

    def test_signup_without_invitation_fails(self):
        """Test that signup without invitation fails"""
        url = reverse('signup')
        data = {
            'email': 'noinvite@example.com',
            'password': 'securepass123',
            'first_name': 'No',
            'last_name': 'Invite'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Company name required', response.data['error'])


class AuditLogTests(TestCase):
    """Test audit logging functionality"""

    def setUp(self):
        self.tenant = Tenant.objects.create(
            name='Test Tenant',
            domain='test.example.com'
        )
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_audit_log_creation(self):
        """Test creating an audit log entry"""
        audit_log = AuditLog.objects.create(
            user=self.user,
            tenant=self.tenant,
            action='user_login',
            resource_type='user',
            resource_id=str(self.user.id),
            ip_address='192.168.1.1',
            user_agent='Test Agent',
            metadata={'test': True}
        )

        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.tenant, self.tenant)
        self.assertEqual(audit_log.action, 'user_login')
        self.assertEqual(audit_log.resource_type, 'user')
        self.assertEqual(audit_log.ip_address, '192.168.1.1')

    def test_audit_log_str_representation(self):
        """Test string representation of audit log"""
        audit_log = AuditLog.objects.create(
            user=self.user,
            tenant=self.tenant,
            action='project_created',
            resource_type='project',
            resource_id='123',
            ip_address='192.168.1.1'
        )

        # Check that the string contains the expected elements
        str_repr = str(audit_log)
        self.assertIn("Project Created", str_repr)
        self.assertIn("Project", str_repr)
        self.assertIn("test@example.com", str_repr)


class ApproveMemberAPITests(APITestCase):
    """Test member approval functionality"""

    def setUp(self):
        # Create tenant and owner
        self.tenant = Tenant.objects.create(
            name='Test Tenant',
            domain='test'
        )
        self.owner = CustomUser.objects.create_user(
            email='owner@example.com',
            password='testpass123',
            first_name='Owner',
            last_name='User'
        )
        UserTenant.objects.create(
            user=self.owner,
            tenant=self.tenant,
            is_owner=True,
            is_approved=True
        )

        # Create unapproved member
        self.member = CustomUser.objects.create_user(
            email='member@example.com',
            password='testpass123',
            first_name='Member',
            last_name='User'
        )
        self.member_tenant = UserTenant.objects.create(
            user=self.member,
            tenant=self.tenant,
            is_owner=False,
            is_approved=False,  # Not approved yet
            role='Employee'
        )

        # Authenticate as owner
        self.client.force_authenticate(user=self.owner)

    @override_settings(MULTI_TENANCY_ENABLED=True, ALLOWED_HOSTS=['test.example.com'])
    def test_approve_member(self):
        """Test approving a team member"""
        url = reverse('approve_member')
        data = {'user_id': self.member.id}

        response = self.client.post(url, data, format='json', HTTP_HOST='test.example.com')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Member approved', response.data['message'])

        # Check member was approved
        self.member_tenant.refresh_from_db()
        self.assertTrue(self.member_tenant.is_approved)

        # Check profile was created
        profile = UserProfile.objects.get(user=self.member)
        self.assertIsNotNone(profile)

    @override_settings(MULTI_TENANCY_ENABLED=True, ALLOWED_HOSTS=['test.example.com'])
    def test_approve_nonexistent_member(self):
        """Test approving a non-existent user"""
        url = reverse('approve_member')
        data = {'user_id': 99999}

        response = self.client.post(url, data, format='json', HTTP_HOST='test.example.com')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('not found', response.data['error'])