import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser, Tenant, UserTenant
from .models import LeaveBalance, LeavePolicy, LeaveRequest


class LeaveManagementModelTests(TestCase):
    """Test cases for leave management models."""

    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name="Test Company",
            domain="testcompany.com"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        UserTenant.objects.create(
            user=self.user,
            tenant=self.tenant,
            is_owner=True,
            is_approved=True
        )

    def test_leave_request_creation(self):
        """Test creating a leave request."""
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=5)

        leave_request = LeaveRequest.objects.create(
            employee=self.user,
            tenant=self.tenant,
            leave_type='annual_leave',
            start_date=start_date,
            end_date=end_date,
            days_requested=Decimal('5.0'),
            reason="Vacation"
        )

        self.assertEqual(leave_request.employee, self.user)
        self.assertEqual(leave_request.tenant, self.tenant)
        self.assertEqual(leave_request.leave_type, 'annual_leave')
        self.assertEqual(leave_request.days_requested, Decimal('5.0'))
        self.assertEqual(leave_request.status, 'pending_department_manager')

    def test_leave_balance_creation(self):
        """Test creating a leave balance."""
        balance = LeaveBalance.objects.create(
            employee=self.user,
            tenant=self.tenant,
            leave_type='annual_leave',
            year=2024,
            total_days=Decimal('25.0'),
            used_days=Decimal('5.0')
        )

        self.assertEqual(balance.employee, self.user)
        self.assertEqual(balance.tenant, self.tenant)
        self.assertEqual(balance.remaining_days, Decimal('20.0'))
        self.assertEqual(balance.utilization_percentage, 20.0)

    def test_leave_policy_creation(self):
        """Test creating a leave policy."""
        policy = LeavePolicy.objects.create(
            tenant=self.tenant,
            leave_type='annual_leave',
            annual_entitlement=Decimal('25.0'),
            max_consecutive_days=30,
            notice_period_days=7
        )

        self.assertEqual(policy.tenant, self.tenant)
        self.assertEqual(policy.leave_type, 'annual_leave')
        self.assertEqual(policy.annual_entitlement, Decimal('25.0'))
        self.assertTrue(policy.is_active)

    def test_business_days_calculation(self):
        """Test business days calculation in leave request."""
        # Monday to Friday (5 business days)
        start_date = datetime.date(2024, 1, 1)  # Monday
        end_date = start_date + datetime.timedelta(days=4)  # Friday

        leave_request = LeaveRequest(
            employee=self.user,
            tenant=self.tenant,
            leave_type='annual_leave',
            start_date=start_date,
            end_date=end_date
        )

        # Trigger clean method
        leave_request.clean()

        self.assertEqual(leave_request.days_requested, Decimal('5.0'))


class LeaveManagementAPITests(APITestCase):
    """Test cases for leave management API endpoints."""

    def setUp(self):
        """Set up test data and authentication."""
        self.tenant = Tenant.objects.create(
            name="Test Company",
            domain="testcompany.com"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        UserTenant.objects.create(
            user=self.user,
            tenant=self.tenant,
            is_owner=True,
            is_approved=True
        )

        # Create a leave policy
        LeavePolicy.objects.create(
            tenant=self.tenant,
            leave_type='annual_leave',
            annual_entitlement=Decimal('25.0'),
            max_consecutive_days=30,
            notice_period_days=7
        )

        # Create leave balance
        LeaveBalance.objects.create(
            employee=self.user,
            tenant=self.tenant,
            leave_type='annual_leave',
            year=datetime.date.today().year,
            total_days=Decimal('25.0'),
            used_days=Decimal('0.0')
        )

        # Add permissions for testing
        from django.contrib.auth.models import Permission

        # Add permissions for leave request management
        self.user.user_permissions.add(
            Permission.objects.get(codename='view_leaverequest'),
            Permission.objects.get(codename='add_leaverequest'),
            Permission.objects.get(codename='change_leaverequest'),
        )

        # Add permissions for leave balance management
        self.user.user_permissions.add(
            Permission.objects.get(codename='view_leavebalance'),
        )

        # Add permissions for leave policy management
        self.user.user_permissions.add(
            Permission.objects.get(codename='view_leavepolicy'),
        )

        self.client.force_authenticate(user=self.user)

    def test_create_leave_request(self):
        """Test creating a leave request via API."""
        url = reverse('leaverequest-list')
        data = {
            'leave_type': 'annual_leave',
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
            'reason': 'Vacation time'
        }

        response = self.client.post(url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LeaveRequest.objects.count(), 1)
        self.assertEqual(LeaveRequest.objects.first().status, 'pending_department_manager')

    def test_list_leave_requests(self):
        """Test listing leave requests."""
        # Create a leave request
        LeaveRequest.objects.create(
            employee=self.user,
            tenant=self.tenant,
            leave_type='annual_leave',
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=5),
            days_requested=Decimal('5.0'),
            reason="Test vacation"
        )

        url = reverse('leaverequest-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_approve_leave_request(self):
        """Test approving a leave request."""
        leave_request = LeaveRequest.objects.create(
            employee=self.user,
            tenant=self.tenant,
            leave_type='annual_leave',
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=5),
            days_requested=Decimal('5.0'),
            reason="Test vacation"
        )

        url = reverse('leaverequest-approve', kwargs={'pk': leave_request.pk})
        response = self.client.post(url, {'notes': 'Approved for vacation'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        leave_request.refresh_from_db()
        self.assertEqual(leave_request.status, 'approved')

    def test_get_leave_balance(self):
        """Test retrieving leave balance."""
        url = reverse('leavebalance-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        balance_data = response.data['results'][0]
        self.assertEqual(str(balance_data['remaining_days']), '25.0')

    def test_get_leave_policies(self):
        """Test retrieving leave policies."""
        url = reverse('leavepolicy-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        policy_data = response.data['results'][0]
        self.assertEqual(policy_data['leave_type'], 'annual_leave')
        self.assertEqual(policy_data['annual_entitlement'], '25.0')

    def test_complete_leave_request_workflow(self):
        """Test complete leave request workflow from creation to approval."""
        # Create leave request - use Monday to Friday to ensure exactly 5 business days
        monday = datetime.date.today() + datetime.timedelta(days=(7 - datetime.date.today().weekday()) % 7)
        friday = monday + datetime.timedelta(days=4)  # Monday + 4 days = Friday

        url = reverse('leaverequest-list')
        data = {
            'leave_type': 'annual_leave',
            'start_date': monday.isoformat(),
            'end_date': friday.isoformat(),
            'reason': 'Vacation time'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        leave_request_id = response.data['id']

        # Verify initial balance
        balance_url = reverse('leavebalance-list')
        response = self.client.get(balance_url)
        initial_balance = response.data['results'][0]['remaining_days']
        self.assertEqual(initial_balance, '25.0')

        # Approve the request
        approve_url = reverse('leaverequest-approve', kwargs={'pk': leave_request_id})
        response = self.client.post(approve_url, {'notes': 'Approved for vacation'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify balance was updated
        response = self.client.get(balance_url)
        updated_balance = response.data['results'][0]['remaining_days']
        self.assertEqual(updated_balance, '20.0')  # 25 - 5 days

        # Verify used days were updated
        used_days = response.data['results'][0]['used_days']
        self.assertEqual(used_days, '5.0')

    def test_leave_request_rejection_workflow(self):
        """Test leave request rejection workflow."""
        # Create leave request
        url = reverse('leaverequest-list')
        data = {
            'leave_type': 'annual_leave',
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() + datetime.timedelta(days=3)).isoformat(),
            'reason': 'Sick leave'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        leave_request_id = response.data['id']

        # Verify initial balance unchanged
        balance_url = reverse('leavebalance-list')
        response = self.client.get(balance_url)
        initial_balance = response.data['results'][0]['remaining_days']
        self.assertEqual(initial_balance, '25.0')

        # Reject the request
        reject_url = reverse('leaverequest-reject', kwargs={'pk': leave_request_id})
        response = self.client.post(reject_url, {'notes': 'Insufficient notice period'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify balance remains unchanged
        response = self.client.get(balance_url)
        final_balance = response.data['results'][0]['remaining_days']
        self.assertEqual(final_balance, '25.0')

        # Verify request status
        request_url = reverse('leaverequest-detail', kwargs={'pk': leave_request_id})
        response = self.client.get(request_url)
        self.assertEqual(response.data['status'], 'rejected')

    def test_leave_request_cancellation_workflow(self):
        """Test leave request cancellation workflow."""
        # Create and approve leave request - use Monday to Tuesday for exactly 2 business days
        monday = datetime.date.today() + datetime.timedelta(days=(7 - datetime.date.today().weekday()) % 7)
        tuesday = monday + datetime.timedelta(days=1)  # Monday + 1 day = Tuesday

        url = reverse('leaverequest-list')
        data = {
            'leave_type': 'annual_leave',
            'start_date': monday.isoformat(),
            'end_date': tuesday.isoformat(),
            'reason': 'Personal leave'
        }

        response = self.client.post(url, data, format='json')
        leave_request_id = response.data['id']

        # Approve it
        approve_url = reverse('leaverequest-approve', kwargs={'pk': leave_request_id})
        self.client.post(approve_url, {'notes': 'Approved'})

        # Verify balance was reduced
        balance_url = reverse('leavebalance-list')
        response = self.client.get(balance_url)
        self.assertEqual(response.data['results'][0]['remaining_days'], '23.0')  # 25 - 2

        # Cancel the approved request
        cancel_url = reverse('leaverequest-cancel', kwargs={'pk': leave_request_id})
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify balance was restored
        response = self.client.get(balance_url)
        self.assertEqual(response.data['results'][0]['remaining_days'], '25.0')  # Back to original

        # Verify request status
        request_url = reverse('leaverequest-detail', kwargs={'pk': leave_request_id})
        response = self.client.get(request_url)
        self.assertEqual(response.data['status'], 'cancelled')

    def test_leave_balance_insufficient_days(self):
        """Test that leave requests exceeding available balance are still allowed."""
        # Create a large leave request
        url = reverse('leaverequest-list')
        data = {
            'leave_type': 'annual_leave',
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
            'reason': 'Extended vacation'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Should still be allowed even if it exceeds balance
        # (Business logic allows negative balances or HR can adjust)

    def test_leave_request_validation(self):
        """Test leave request validation rules."""
        url = reverse('leaverequest-list')

        # Test end date before start date
        data = {
            'leave_type': 'annual_leave',
            'start_date': (datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
            'end_date': datetime.date.today().isoformat(),
            'reason': 'Invalid dates'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test that requests with future dates work
        future_date = datetime.date.today() + datetime.timedelta(days=30)
        data = {
            'leave_type': 'annual_leave',
            'start_date': future_date.isoformat(),
            'end_date': (future_date + datetime.timedelta(days=2)).isoformat(),
            'reason': 'Future leave'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
