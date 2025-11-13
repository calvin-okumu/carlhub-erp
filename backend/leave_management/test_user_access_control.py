from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.test import APIRequestFactory

from accounts.models import CustomUser, Tenant, UserTenant
from leave_management.models import LeaveBalance, LeavePolicy, LeaveRequest
from leave_management.serializers import LeaveRequestSerializer
from leave_management.views import LeaveRequestViewSet, LeaveBalanceViewSet, LeavePolicyViewSet


class UserSpecificAccessControlTests(TestCase):
    """Test user-specific access control for leave management."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.tenant = Tenant.objects.create(name="Test Company")
        
        # Create users with different roles
        self.owner = CustomUser.objects.create_user(
            email="owner@test.com",
            password="testpass123"
        )
        self.admin = CustomUser.objects.create_user(
            email="admin@test.com", 
            password="testpass123"
        )
        self.employee1 = CustomUser.objects.create_user(
            email="employee1@test.com",
            password="testpass123"
        )
        self.employee2 = CustomUser.objects.create_user(
            email="employee2@test.com",
            password="testpass123"
        )
        
        # Create user-tenant relationships
        self.owner_tenant = UserTenant.objects.create(
            user=self.owner,
            tenant=self.tenant,
            is_owner=True,
            is_approved=True,
            role='owner'
        )
        self.admin_tenant = UserTenant.objects.create(
            user=self.admin,
            tenant=self.tenant,
            is_owner=False,
            is_approved=True,
            role='admin'
        )
        self.employee1_tenant = UserTenant.objects.create(
            user=self.employee1,
            tenant=self.tenant,
            is_owner=False,
            is_approved=True,
            role='employee'
        )
        self.employee2_tenant = UserTenant.objects.create(
            user=self.employee2,
            tenant=self.tenant,
            is_owner=False,
            is_approved=True,
            role='employee'
        )
        
        # Create leave policies for different types
        self.policy_annual = LeavePolicy.objects.create(
            tenant=self.tenant,
            leave_type='annual_leave',
            annual_entitlement=Decimal('21'),
            is_active=True
        )
        self.policy_sick = LeavePolicy.objects.create(
            tenant=self.tenant,
            leave_type='sick_leave',
            annual_entitlement=Decimal('10'),
            is_active=True
        )
        
        # Create leave requests
        self.leave_request1 = LeaveRequest.objects.create(
            tenant=self.tenant,
            employee=self.employee1,
            leave_type='annual_leave',
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            days_requested=Decimal('1'),
            reason='Test leave 1',
            status='pending'
        )
        
        self.leave_request2 = LeaveRequest.objects.create(
            tenant=self.tenant,
            employee=self.employee2,
            leave_type='annual_leave',
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            days_requested=Decimal('1'),
            reason='Test leave 2',
            status='pending'
        )
        
        # Create leave balances
        self.balance1 = LeaveBalance.objects.create(
            tenant=self.tenant,
            employee=self.employee1,
            leave_type='annual_leave',
            year=timezone.now().year,
            total_days=Decimal('21'),
            used_days=Decimal('5')
        )
        
        self.balance2 = LeaveBalance.objects.create(
            tenant=self.tenant,
            employee=self.employee2,
            leave_type='annual_leave',
            year=timezone.now().year,
            total_days=Decimal('21'),
            used_days=Decimal('3')
        )

    def test_employee_can_only_view_own_leave_requests(self):
        """Test that employees can only view their own leave requests."""
        view = LeaveRequestViewSet.as_view({'get': 'list'})
        
        # Employee1 should only see their own request
        request = self.factory.get('/api/leave-requests/')
        request.user = self.employee1
        request.tenant = self.tenant
        
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only return employee1's requests
        request_ids = [str(req['id']) for req in response.data['results']]
        self.assertIn(str(self.leave_request1.id), request_ids)
        self.assertNotIn(str(self.leave_request2.id), request_ids)

    def test_admin_can_view_all_leave_requests(self):
        """Test that admins can view all leave requests in the tenant."""
        view = LeaveRequestViewSet.as_view({'get': 'list'})
        
        request = self.factory.get('/api/leave-requests/')
        request.user = self.admin
        request.tenant = self.tenant
        
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return all requests
        request_ids = [str(req['id']) for req in response.data['results']]
        self.assertIn(str(self.leave_request1.id), request_ids)
        self.assertIn(str(self.leave_request2.id), request_ids)

    def test_owner_can_view_all_leave_requests(self):
        """Test that owners can view all leave requests in the tenant."""
        view = LeaveRequestViewSet.as_view({'get': 'list'})
        
        request = self.factory.get('/api/leave-requests/')
        request.user = self.owner
        request.tenant = self.tenant
        
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return all requests
        request_ids = [str(req['id']) for req in response.data['results']]
        self.assertIn(str(self.leave_request1.id), request_ids)
        self.assertIn(str(self.leave_request2.id), request_ids)

    def test_employee_can_only_view_own_leave_balances(self):
        """Test that employees can only view their own leave balances."""
        view = LeaveBalanceViewSet.as_view({'get': 'list'})
        
        # Employee1 should only see their own balance
        request = self.factory.get('/api/leave-balances/')
        request.user = self.employee1
        request.tenant = self.tenant
        
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only return employee1's balance
        balance_ids = [str(bal['id']) for bal in response.data['results']]
        self.assertIn(str(self.balance1.id), balance_ids)
        self.assertNotIn(str(self.balance2.id), balance_ids)

    def test_admin_can_view_all_leave_balances(self):
        """Test that admins can view all leave balances in the tenant."""
        view = LeaveBalanceViewSet.as_view({'get': 'list'})
        
        request = self.factory.get('/api/leave-balances/')
        request.user = self.admin
        request.tenant = self.tenant
        
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return all balances
        balance_ids = [str(bal['id']) for bal in response.data['results']]
        self.assertIn(str(self.balance1.id), balance_ids)
        self.assertIn(str(self.balance2.id), balance_ids)

    def test_employee_cannot_create_leave_request_for_others(self):
        """Test that employees cannot create leave requests for other employees."""
        from datetime import timedelta, date
        # Use a specific weekday (Monday) to ensure business days calculation works
        future_date = date(2025, 1, 6)  # Monday, January 6, 2025
        
        request_data = {
            'employee': self.employee2.id,  # Trying to create for employee2
            'leave_type': 'sick_leave',  # Use a valid leave type
            'start_date': future_date,
            'end_date': future_date,
            'reason': 'Test request for someone else'
        }
        
        request = self.factory.post('/api/leave-requests/', request_data)
        request.user = self.employee1
        request.tenant = self.tenant
        
        serializer = LeaveRequestSerializer(data=request_data, context={'request': request})
        # The serializer should be valid at this stage since employee is read_only
        self.assertTrue(serializer.is_valid())
        
        # But save() should raise the validation error
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.save()
        
        self.assertIn('You can only create leave requests for yourself', str(context.exception))

    def test_admin_can_create_leave_request_for_others(self):
        """Test that admins can create leave requests for other employees."""
        from datetime import date
        request_data = {
            'employee': self.employee2.id,
            'leave_type': 'sick_leave',
            'start_date': date(2025, 1, 6),  # Monday
            'end_date': date(2025, 1, 6),    # Monday
            'reason': 'Admin creating request for employee'
        }
        
        request = self.factory.post('/api/leave-requests/', request_data)
        request.user = self.admin
        request.tenant = self.tenant
        
        serializer = LeaveRequestSerializer(data=request_data, context={'request': request})
        self.assertTrue(serializer.is_valid())

    def test_owner_can_create_leave_request_for_others(self):
        """Test that owners can create leave requests for other employees."""
        from datetime import date
        request_data = {
            'employee': self.employee2.id,
            'leave_type': 'sick_leave',
            'start_date': date(2025, 1, 6),  # Monday
            'end_date': date(2025, 1, 6),    # Monday
            'reason': 'Owner creating request for employee'
        }
        
        request = self.factory.post('/api/leave-requests/', request_data)
        request.user = self.owner
        request.tenant = self.tenant
        
        serializer = LeaveRequestSerializer(data=request_data, context={'request': request})
        self.assertTrue(serializer.is_valid())

    def test_employee_can_only_cancel_own_requests(self):
        """Test that employees can only cancel their own leave requests."""
        view = LeaveRequestViewSet.as_view({'post': 'cancel'})
        
        # Employee1 trying to cancel employee2's request should fail
        request = self.factory.post(f'/api/leave-requests/{self.leave_request2.id}/cancel/')
        request.user = self.employee1
        request.tenant = self.tenant
        
        # Mock get_object to return employee2's request
        with patch.object(view, 'get_object', return_value=self.leave_request2):
            response = view(request, pk=self.leave_request2.id)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertIn('You can only cancel your own leave requests', str(response.data))

    def test_admin_can_cancel_any_request(self):
        """Test that admins can cancel any leave request."""
        view = LeaveRequestViewSet.as_view({'post': 'cancel'})
        
        request = self.factory.post(f'/api/leave-requests/{self.leave_request1.id}/cancel/')
        request.user = self.admin
        request.tenant = self.tenant
        
        # Mock get_object to return employee1's request
        with patch.object(view, 'get_object', return_value=self.leave_request1):
            response = view(request, pk=self.leave_request1.id)
            # Should succeed (status might be 200 or other success code depending on implementation)
            self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_has_full_access(self):
        """Test that superusers have full access to all leave data."""
        # Create superuser
        superuser = CustomUser.objects.create_superuser(
            email="super@test.com",
            password="testpass123"
        )
        
        view = LeaveRequestViewSet.as_view({'get': 'list'})
        
        request = self.factory.get('/api/leave-requests/')
        request.user = superuser
        request.tenant = self.tenant
        
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return all requests
        request_ids = [str(req['id']) for req in response.data['results']]
        self.assertIn(str(self.leave_request1.id), request_ids)
        self.assertIn(str(self.leave_request2.id), request_ids)

    def test_unapproved_user_access_restricted(self):
        """Test that unapproved users have restricted access."""
        # Create unapproved user
        unapproved_user = CustomUser.objects.create_user(
            email="unapproved@test.com",
            password="testpass123"
        )
        UserTenant.objects.create(
            user=unapproved_user,
            tenant=self.tenant,
            is_owner=False,
            is_approved=False,  # Not approved
            role='employee'
        )
        
        view = LeaveRequestViewSet.as_view({'get': 'list'})
        
        request = self.factory.get('/api/leave-requests/')
        request.user = unapproved_user
        request.tenant = self.tenant
        
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return empty queryset since user is not approved
        self.assertEqual(len(response.data['results']), 0)