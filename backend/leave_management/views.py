from decimal import Decimal

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.email_service import EmailService
from accounts.models import CustomUser
from saasCRM.pagination import CustomPageNumberPagination

from .models import LeaveBalance, LeavePolicy, LeaveRequest
from .permissions import (
    CanApproveLeaves,
    CanManageLeaveBalances,
    CanManageLeavePolicies,
    CanManageLeaveRequests,
)
from .serializers import (
    LeaveBalanceSerializer,
    LeavePolicySerializer,
    LeaveRequestSerializer,
)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave requests.

    Employees can:
    - View their own leave requests
    - Create new leave requests
    - Update their pending requests

    Managers can:
    - View all requests in their tenant
    - Approve/reject requests
    """
    serializer_class = LeaveRequestSerializer
    permission_classes = [CanManageLeaveRequests]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'leave_type', 'employee', 'approved_by']
    search_fields = ['reason', 'approval_notes']
    ordering_fields = ['applied_date', 'start_date', 'end_date', 'status']
    ordering = ['-applied_date']

    def get_queryset(self):
        """Filter queryset based on user permissions with enhanced user-specific access."""
        user = self.request.user
        queryset = LeaveRequest.objects.select_related('employee', 'tenant', 'approved_by')

        # Handle schema generation (no authenticated user)
        if not user or user.is_anonymous:
            return queryset.none()

        # Check if user can view all requests (admin/owner/special permissions)
        if self._can_view_all_requests(user):
            if hasattr(self.request, 'tenant') and self.request.tenant:
                return queryset.filter(tenant=self.request.tenant)
            return queryset

        # Otherwise, only show user's own requests
        return queryset.filter(employee=user)

    def _can_view_all_requests(self, user):
        """Check if user can view all leave requests in the tenant."""
        # Superusers can view all
        if user.is_superuser:
            return True
        
        # Check for explicit permission
        if user.has_perm('leave_management.view_leaverequest'):
            return True
        
        # Check tenant admin/owner role
        try:
            user_tenant = user.usertenant
            return user_tenant.is_approved and (user_tenant.is_owner or user_tenant.role in ['admin', 'owner'])
        except:
            return False

    def perform_create(self, serializer):
        """Set the employee and tenant when creating a request."""
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[CanApproveLeaves])
    def approve(self, request, pk=None):
        """Approve a leave request."""
        leave_request = self.get_object()

        if leave_request.status != 'pending':
            return Response(
                {'error': 'Only pending requests can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        leave_request.status = 'approved'
        leave_request.approved_by = request.user
        leave_request.approved_date = timezone.now()
        leave_request.approval_notes = request.data.get('notes', '')
        leave_request.save()

        # Update leave balance if approved
        self._update_leave_balance(leave_request)

        # Send approval email notification
        EmailService.send_leave_approved_email(leave_request)

        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[CanApproveLeaves])
    def reject(self, request, pk=None):
        """Reject a leave request."""
        leave_request = self.get_object()

        if leave_request.status != 'pending':
            return Response(
                {'error': 'Only pending requests can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        leave_request.status = 'rejected'
        leave_request.approved_by = request.user
        leave_request.approved_date = timezone.now()
        leave_request.approval_notes = request.data.get('notes', '')
        leave_request.save()

        # Send rejection email notification
        EmailService.send_leave_rejected_email(leave_request)

        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a leave request (only by the employee who created it)."""
        leave_request = self.get_object()

        # Only allow cancellation of pending or approved requests
        if leave_request.status not in ['pending', 'approved']:
            return Response(
                {'error': 'Cannot cancel requests that are already taken or rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Only the employee can cancel their own request
        if leave_request.employee != request.user:
            return Response(
                {'error': 'You can only cancel your own leave requests.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Store original status for balance restoration logic
        original_status = leave_request.status

        leave_request.status = 'cancelled'
        leave_request.save()

        # If it was approved, restore the leave balance
        if original_status == 'approved':
            self._restore_leave_balance(leave_request)

        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)

    def _update_leave_balance(self, leave_request):
        """Update leave balance when a request is approved."""
        try:
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                tenant=leave_request.tenant,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year
            )
            balance.used_days += leave_request.days_requested
            balance.save()
        except LeaveBalance.DoesNotExist:
            # Create balance entry if it doesn't exist
            LeaveBalance.objects.create(
                employee=leave_request.employee,
                tenant=leave_request.tenant,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year,
                total_days=Decimal('0'),  # Will need to be set by HR
                used_days=leave_request.days_requested
            )

    def _restore_leave_balance(self, leave_request):
        """Restore leave balance when a request is cancelled."""
        try:
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                tenant=leave_request.tenant,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year
            )
            balance.used_days -= leave_request.days_requested
            balance.save()
        except LeaveBalance.DoesNotExist:
            pass  # Balance doesn't exist, nothing to restore


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave balances.

    HR/Admin users can manage leave balances for employees.
    Employees can view their own balances.
    """
    serializer_class = LeaveBalanceSerializer
    permission_classes = [CanManageLeaveBalances]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'leave_type', 'year']
    ordering_fields = ['year', 'leave_type', 'employee']
    ordering = ['-year', 'leave_type']

    def get_queryset(self):
        """Filter queryset based on user permissions with enhanced user-specific access."""
        user = self.request.user
        queryset = LeaveBalance.objects.select_related('employee', 'tenant')

        # Handle schema generation (no authenticated user)
        if not user or user.is_anonymous:
            return queryset.none()

        # Check if user can view all balances (admin/owner/special permissions)
        if self._can_view_all_balances(user):
            if hasattr(self.request, 'tenant') and self.request.tenant:
                return queryset.filter(tenant=self.request.tenant)
            return queryset

        # Otherwise, only show user's own balances
        return queryset.filter(employee=user)

    def _can_view_all_balances(self, user):
        """Check if user can view all leave balances in the tenant."""
        # Superusers can view all
        if user.is_superuser:
            return True
        
        # Check for explicit permission
        if user.has_perm('leave_management.view_leavebalance'):
            return True
        
        # Check tenant admin/owner role
        try:
            user_tenant = user.usertenant
            return user_tenant.is_approved and (user_tenant.is_owner or user_tenant.role in ['admin', 'owner'])
        except:
            return False


class LeavePolicyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave policies.

    Only tenant admins can manage leave policies.
    All tenant users can view active policies.
    """
    serializer_class = LeavePolicySerializer
    permission_classes = [CanManageLeavePolicies]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['leave_type', 'is_active']
    ordering_fields = ['leave_type', 'is_active']
    ordering = ['leave_type']

    def get_queryset(self):
        """Filter queryset based on user permissions with enhanced user-specific access."""
        user = self.request.user
        queryset = LeavePolicy.objects.select_related('tenant')

        # Handle schema generation (no authenticated user)
        if not user or user.is_anonymous:
            return queryset.none()

        # Check if user can view all policies (admin/owner/special permissions)
        if self._can_view_all_policies(user):
            if hasattr(self.request, 'tenant') and self.request.tenant:
                return queryset.filter(tenant=self.request.tenant)
            return queryset

        # Otherwise, only show active policies for their tenant
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return queryset.filter(tenant=self.request.tenant, is_active=True)

        return queryset.none()

    def _can_view_all_policies(self, user):
        """Check if user can view all leave policies in the tenant."""
        # Superusers can view all
        if user.is_superuser:
            return True
        
        # Check for explicit permission
        if user.has_perm('leave_management.view_leavepolicy'):
            return True
        
        # Check tenant admin/owner role
        try:
            user_tenant = user.usertenant
            return user_tenant.is_approved and (user_tenant.is_owner or user_tenant.role in ['admin', 'owner'])
        except:
            return False
