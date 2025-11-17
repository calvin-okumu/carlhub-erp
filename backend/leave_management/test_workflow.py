"""
Tests for multi-level leave approval workflow.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser, Department, Tenant, UserTenant
from leave_management.models import (
    LeaveApproval,
    LeaveBalance,
    LeavePolicy,
    LeaveRequest,
)
from leave_management.services import LeaveApprovalWorkflowService


class LeaveApprovalWorkflowTests(TestCase):
    """Test the multi-level leave approval workflow."""

    def setUp(self):
        """Set up test data for workflow testing."""
        self.tenant = Tenant.objects.create(name="Test Company", domain="testcompany.com")

        # Create users for different roles
        self.employee = CustomUser.objects.create_user(
            username="employee", email="employee@test.com", password="testpass123"
        )

        self.department_manager = CustomUser.objects.create_user(
            username="dept_manager", email="manager@test.com", password="testpass123"
        )

        self.hr_manager = CustomUser.objects.create_user(
            username="hr_manager", email="hr@test.com", password="testpass123"
        )

        self.general_manager = CustomUser.objects.create_user(
            username="gen_manager", email="gm@test.com", password="testpass123"
        )

        # Create department
        self.department = Department.objects.create(
            tenant=self.tenant, name="Engineering", manager=self.department_manager
        )

        # Create user-tenant relationships
        UserTenant.objects.create(
            user=self.employee,
            tenant=self.tenant,
            role="Employee",
            department=self.department,
            is_approved=True,
        )

        UserTenant.objects.create(
            user=self.department_manager,
            tenant=self.tenant,
            role="Department Manager",
            department=self.department,
            is_approved=True,
        )

        UserTenant.objects.create(
            user=self.hr_manager, tenant=self.tenant, role="HR Manager", is_approved=True
        )

        UserTenant.objects.create(
            user=self.general_manager, tenant=self.tenant, role="General Manager", is_approved=True
        )

        # Create leave policy and balance
        LeavePolicy.objects.create(
            tenant=self.tenant,
            leave_type="annual_leave",
            annual_entitlement=Decimal("25.0"),
            max_consecutive_days=30,
            notice_period_days=7,
        )

        LeaveBalance.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            year=date.today().year,
            total_days=Decimal("25.0"),
            used_days=Decimal("0.0"),
        )

    def test_approval_chain_generation(self):
        """Test that approval chain is generated correctly."""
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            days_requested=Decimal("5.0"),
            reason="Test vacation",
        )

        approval_chain = LeaveApprovalWorkflowService.get_approval_chain(leave_request)

        # Should have 3 levels: department_manager, hr_manager, general_manager
        self.assertEqual(len(approval_chain), 3)
        self.assertEqual(approval_chain[0][0], "department_manager")
        self.assertEqual(approval_chain[0][1], self.department_manager)
        self.assertEqual(approval_chain[1][0], "hr_manager")
        self.assertEqual(approval_chain[1][1], self.hr_manager)
        self.assertEqual(approval_chain[2][0], "general_manager")
        self.assertEqual(approval_chain[2][1], self.general_manager)

    def test_workflow_initialization(self):
        """Test that workflow is properly initialized for new leave requests."""
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            days_requested=Decimal("5.0"),
            reason="Test vacation",
        )

        # Initialize workflow
        LeaveApprovalWorkflowService.initialize_workflow(leave_request)

        leave_request.refresh_from_db()

        # Should start at department manager level
        self.assertEqual(leave_request.status, "pending_department_manager")
        self.assertEqual(leave_request.current_approval_level, "department_manager")

        # Should have approval records created
        approvals = LeaveApproval.objects.filter(leave_request=leave_request)
        self.assertEqual(approvals.count(), 3)

        # Check that all are pending initially
        for approval in approvals:
            self.assertEqual(approval.status, "pending")

    def test_department_manager_approval(self):
        """Test approval at department manager level."""
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            days_requested=Decimal("5.0"),
            reason="Test vacation",
        )

        LeaveApprovalWorkflowService.initialize_workflow(leave_request)

        # Department manager approves
        result = LeaveApprovalWorkflowService.process_approval(
            leave_request, self.department_manager, "approve", "Approved by dept manager"
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "pending_hr_manager")

        leave_request.refresh_from_db()
        self.assertEqual(leave_request.current_approval_level, "hr_manager")
        self.assertEqual(leave_request.status, "pending_hr_manager")

    def test_hr_manager_approval(self):
        """Test approval at HR manager level."""
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            days_requested=Decimal("5.0"),
            reason="Test vacation",
        )

        LeaveApprovalWorkflowService.initialize_workflow(leave_request)

        # Department manager approves first
        LeaveApprovalWorkflowService.process_approval(
            leave_request, self.department_manager, "approve", "Approved by dept manager"
        )

        # HR manager approves
        result = LeaveApprovalWorkflowService.process_approval(
            leave_request, self.hr_manager, "approve", "Approved by HR"
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "pending_general_manager")

        leave_request.refresh_from_db()
        self.assertEqual(leave_request.current_approval_level, "general_manager")
        self.assertEqual(leave_request.status, "pending_general_manager")

    def test_final_approval(self):
        """Test final approval at general manager level."""
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            days_requested=Decimal("5.0"),
            reason="Test vacation",
        )

        LeaveApprovalWorkflowService.initialize_workflow(leave_request)

        # Department manager approves
        LeaveApprovalWorkflowService.process_approval(
            leave_request, self.department_manager, "approve", "Approved by dept manager"
        )

        # HR manager approves
        LeaveApprovalWorkflowService.process_approval(
            leave_request, self.hr_manager, "approve", "Approved by HR"
        )

        # General manager approves (final approval)
        result = LeaveApprovalWorkflowService.process_approval(
            leave_request, self.general_manager, "approve", "Final approval"
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "approved")

        leave_request.refresh_from_db()
        self.assertEqual(leave_request.status, "approved")
        self.assertEqual(leave_request.final_approver, self.general_manager)

    def test_rejection_at_any_level(self):
        """Test rejection at any approval level."""
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            days_requested=Decimal("5.0"),
            reason="Test vacation",
        )

        LeaveApprovalWorkflowService.initialize_workflow(leave_request)

        # Department manager rejects
        result = LeaveApprovalWorkflowService.process_approval(
            leave_request, self.department_manager, "reject", "Insufficient coverage"
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "rejected")

        leave_request.refresh_from_db()
        self.assertEqual(leave_request.status, "rejected")
        self.assertEqual(leave_request.approval_notes, "Insufficient coverage")

    def test_permission_checking(self):
        """Test that permission checking works correctly."""
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            days_requested=Decimal("5.0"),
            reason="Test vacation",
        )

        LeaveApprovalWorkflowService.initialize_workflow(leave_request)

        # Employee cannot approve
        can_approve, reason = LeaveApprovalWorkflowService.can_approve_at_level(
            self.employee, leave_request, "department_manager"
        )
        self.assertFalse(can_approve)

        # Department manager can approve at department level
        can_approve, reason = LeaveApprovalWorkflowService.can_approve_at_level(
            self.department_manager, leave_request, "department_manager"
        )
        self.assertTrue(can_approve)

        # HR manager can also approve at department level (higher privilege)
        can_approve, reason = LeaveApprovalWorkflowService.can_approve_at_level(
            self.hr_manager, leave_request, "department_manager"
        )
        self.assertTrue(can_approve)

    def test_workflow_status_display(self):
        """Test workflow status display functionality."""
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            days_requested=Decimal("5.0"),
            reason="Test vacation",
        )

        LeaveApprovalWorkflowService.initialize_workflow(leave_request)

        workflow_status = LeaveApprovalWorkflowService.get_workflow_status(leave_request)

        self.assertEqual(workflow_status["current_level"], "department_manager")
        self.assertTrue(workflow_status["is_pending"])
        self.assertFalse(workflow_status["is_approved"])
        self.assertFalse(workflow_status["is_rejected"])
        self.assertEqual(len(workflow_status["steps"]), 3)
        self.assertEqual(workflow_status["next_approver"], self.department_manager.get_full_name())


class LeaveApprovalWorkflowAPITests(APITestCase):
    """Test the API endpoints for workflow approval."""

    def setUp(self):
        """Set up test data for API testing."""
        self.tenant = Tenant.objects.create(name="Test Company", domain="testcompany.com")

        # Create users
        self.employee = CustomUser.objects.create_user(
            username="employee", email="employee@test.com", password="testpass123"
        )

        self.department_manager = CustomUser.objects.create_user(
            username="dept_manager", email="manager@test.com", password="testpass123"
        )

        # Create department
        self.department = Department.objects.create(
            tenant=self.tenant, name="Engineering", manager=self.department_manager
        )

        # Create user-tenant relationships
        UserTenant.objects.create(
            user=self.employee,
            tenant=self.tenant,
            role="Employee",
            department=self.department,
            is_approved=True,
        )

        UserTenant.objects.create(
            user=self.department_manager,
            tenant=self.tenant,
            role="Department Manager",
            department=self.department,
            is_approved=True,
        )

        # Create leave policy and balance
        LeavePolicy.objects.create(
            tenant=self.tenant,
            leave_type="annual_leave",
            annual_entitlement=Decimal("25.0"),
            max_consecutive_days=30,
            notice_period_days=7,
        )

        LeaveBalance.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            year=date.today().year,
            total_days=Decimal("25.0"),
            used_days=Decimal("0.0"),
        )

    def test_workflow_status_endpoint(self):
        """Test the workflow status endpoint."""
        # Create leave request
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            days_requested=Decimal("5.0"),
            reason="Test vacation",
        )

        LeaveApprovalWorkflowService.initialize_workflow(leave_request)

        # Test workflow status endpoint
        self.client.force_authenticate(user=self.department_manager)
        url = reverse("leaverequest-workflow-status", kwargs={"pk": leave_request.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("workflow_status", response.data)
        self.assertIn("approval_history", response.data)

    def test_approve_level_endpoint(self):
        """Test the approve-level endpoint."""
        # Create leave request
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            days_requested=Decimal("5.0"),
            reason="Test vacation",
        )

        LeaveApprovalWorkflowService.initialize_workflow(leave_request)

        # Test approve-level endpoint
        self.client.force_authenticate(user=self.department_manager)
        url = reverse("leaverequest-approve-level", kwargs={"pk": leave_request.pk})
        response = self.client.post(
            url, {"action": "approve", "notes": "Approved by department manager"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)

        leave_request.refresh_from_db()
        self.assertEqual(leave_request.status, "pending_hr_manager")

    def test_reject_level_endpoint(self):
        """Test the reject-level endpoint."""
        # Create leave request
        leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            tenant=self.tenant,
            leave_type="annual_leave",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            days_requested=Decimal("5.0"),
            reason="Test vacation",
        )

        LeaveApprovalWorkflowService.initialize_workflow(leave_request)

        # Test reject-level endpoint
        self.client.force_authenticate(user=self.department_manager)
        url = reverse("leaverequest-reject-level", kwargs={"pk": leave_request.pk})
        response = self.client.post(
            url, {"action": "reject", "notes": "Rejected: insufficient team coverage"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        leave_request.refresh_from_db()
        self.assertEqual(leave_request.status, "rejected")
