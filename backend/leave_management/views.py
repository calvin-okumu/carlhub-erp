from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from accounts.email_service import EmailService
from saasCRM.pagination import CustomPageNumberPagination

from .models import LeaveBalance, LeavePolicy, LeaveRequest
from .permissions import (
    CanApproveLeaves,
    CanManageLeaveBalances,
    CanManageLeavePolicies,
    CanManageLeaveRequests,
)
from .serializers import (
    LeaveApprovalActionSerializer,
    LeaveApprovalSerializer,
    LeaveBalanceSerializer,
    LeavePolicySerializer,
    LeaveRequestSerializer,
)
from .services import LeaveApprovalWorkflowService


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave requests.

    Employees can:
    - View their own leave requests
    - Create new leave requests
    - Update their pending requests

    Managers and Tenant Owners can:
    - View all requests in their tenant
    - Approve/reject requests
    """

    serializer_class = LeaveRequestSerializer
    permission_classes = [CanManageLeaveRequests]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "leave_type", "employee"]
    search_fields = ["reason", "approval_notes"]
    ordering_fields = ["applied_date", "start_date", "end_date", "status"]
    ordering = ["-applied_date"]
    lookup_field = "slug"

    def get_object(self):
        """Override to provide custom error message for not found objects."""
        try:
            return super().get_object()
        except LeaveRequest.DoesNotExist:
            raise NotFound("Leave request not found.") from None

    def get_queryset(self):
        """Filter queryset based on user permissions with enhanced user-specific access."""
        user = self.request.user
        queryset = LeaveRequest.objects.select_related("employee", "tenant")

        # Handle schema generation (no authenticated user)
        if not user or user.is_anonymous:
            return queryset.none()

        # Check if user can view all requests (admin/owner/special permissions)
        if self._can_view_all_requests(user):
            if hasattr(self.request, "tenant") and self.request.tenant:
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
        if user.has_perm("leave_management.view_leaverequest"):
            return True

        # Check tenant admin/owner role
        try:
            user_tenant = user.usertenant
            return user_tenant.is_approved and (
                user_tenant.is_owner or user_tenant.role in ["Manager", "Tenant Owner"]
            )
        except Exception:
            return False

    def perform_create(self, serializer):
        """Set the employee and tenant when creating a request."""
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[CanApproveLeaves])
    def approve(self, request, slug=None):
        """Approve a leave request (legacy endpoint for backward compatibility)."""
        leave_request = self.get_object()

        if not leave_request.is_pending:
            return Response(
                {"error": "Only pending requests can be approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use workflow service for approval
        result = LeaveApprovalWorkflowService.process_approval(
            leave_request, request.user, "approve", request.data.get("notes", "")
        )

        if result["success"]:
            # Update leave balance if fully approved
            if leave_request.is_approved:
                self._update_leave_balance(leave_request)
                EmailService.send_leave_approved_email(leave_request)

            serializer = self.get_serializer(leave_request)
            return Response({"message": result["message"], "data": serializer.data})
        else:
            return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[CanApproveLeaves])
    def reject(self, request, slug=None):
        """Reject a leave request (legacy endpoint for backward compatibility)."""
        leave_request = self.get_object()

        if not leave_request.is_pending:
            return Response(
                {"error": "Only pending requests can be rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use workflow service for rejection
        result = LeaveApprovalWorkflowService.process_approval(
            leave_request, request.user, "reject", request.data.get("notes", "")
        )

        if result["success"]:
            EmailService.send_leave_rejected_email(leave_request)
            serializer = self.get_serializer(leave_request)
            return Response({"message": result["message"], "data": serializer.data})
        else:
            return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def approve_level(self, request, slug=None):
        """Approve a leave request at the current workflow level."""
        try:
            leave_request = self.get_object()

            # Validate action data
            action_serializer = LeaveApprovalActionSerializer(data=request.data)
            if not action_serializer.is_valid():
                return Response(action_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Process approval through workflow
            result = LeaveApprovalWorkflowService.process_approval(
                leave_request,
                request.user,
                "approve",
                action_serializer.validated_data.get("notes", ""),
                request,  # Pass request for audit logging
            )

            if result["success"]:
                # Update leave balance if fully approved
                if leave_request.is_approved:
                    try:
                        self._update_leave_balance(leave_request)
                    except Exception as e:
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.error(f"Leave balance update failed: {e}")

                    try:
                        EmailService.send_leave_approved_email(leave_request)
                    except Exception as e:
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.error(f"Email send failed: {e}")

                serializer = self.get_serializer(leave_request)
                return Response(
                    {
                        "message": result["message"],
                        "data": serializer.data,
                        "next_level": result.get("next_level"),
                    }
                )
            else:
                return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"View error: {e}")
            import traceback

            traceback.print_exc()
            return Response(
                {
                    "error": "An error occurred while processing your request. Please try again or contact support."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], permission_classes=[CanApproveLeaves])
    def reject_level(self, request, slug=None):
        """Reject a leave request at the current workflow level."""
        leave_request = self.get_object()

        # Validate action data
        action_serializer = LeaveApprovalActionSerializer(data=request.data)
        if not action_serializer.is_valid():
            return Response(action_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Process rejection through workflow
        result = LeaveApprovalWorkflowService.process_approval(
            leave_request,
            request.user,
            "reject",
            action_serializer.validated_data.get("notes", ""),
            request,
        )

        if result["success"]:
            EmailService.send_leave_rejected_email(leave_request)
            serializer = self.get_serializer(leave_request)
            return Response({"message": result["message"], "data": serializer.data})
        else:
            return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def workflow_status(self, request, slug=None):
        """Get detailed workflow status for a leave request."""
        leave_request = self.get_object()

        workflow_status = LeaveApprovalWorkflowService.get_workflow_status(leave_request)

        return Response(
            {
                "workflow_status": workflow_status,
                "approval_history": LeaveApprovalSerializer(
                    leave_request.get_approval_history(), many=True
                ).data,
            }
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, slug=None):
        """Cancel a leave request (only by the employee who created it)."""
        leave_request = self.get_object()

        # Only allow cancellation of pending or approved requests
        if leave_request.status not in ["pending", "approved"]:
            return Response(
                {"error": "Cannot cancel requests that are already taken or rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Only the employee can cancel their own request
        if leave_request.employee != request.user:
            return Response(
                {"error": "You can only cancel your own leave requests."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Store original status for balance restoration logic
        original_status = leave_request.status

        leave_request.status = "cancelled"
        leave_request.save()

        # If it was approved, restore the leave balance
        if original_status == "approved":
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
                year=leave_request.start_date.year,
            )
            # Only update if there's sufficient balance
            if (
                balance.used_days + leave_request.days_requested
                <= balance.total_days + balance.carried_over
            ):
                balance.used_days += leave_request.days_requested
                balance.save()
        except LeaveBalance.DoesNotExist:
            # Don't create balance entry if it doesn't exist - HR needs to set it up first
            pass

    def _restore_leave_balance(self, leave_request):
        """Restore leave balance when a request is cancelled."""
        try:
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                tenant=leave_request.tenant,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year,
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
    filterset_fields = ["employee", "leave_type", "year"]
    ordering_fields = ["year", "leave_type", "employee"]
    ordering = ["-year", "leave_type"]
    lookup_field = "slug"

    def get_queryset(self):
        """Filter queryset based on user permissions with enhanced user-specific access."""
        user = self.request.user
        queryset = LeaveBalance.objects.select_related("employee", "tenant")

        # Handle schema generation (no authenticated user)
        if not user or user.is_anonymous:
            return queryset.none()

        # Check if user can view all balances (admin/owner/special permissions)
        if self._can_view_all_balances(user):
            if hasattr(self.request, "tenant") and self.request.tenant:
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
        if user.has_perm("leave_management.view_leavebalance"):
            return True

        # Check tenant admin/owner role
        try:
            user_tenant = user.usertenant
            return user_tenant.is_approved and (
                user_tenant.is_owner or user_tenant.role in ["Manager", "Tenant Owner"]
            )
        except Exception:
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
    filterset_fields = ["leave_type", "is_active"]
    ordering_fields = ["leave_type", "is_active"]
    ordering = ["leave_type"]
    lookup_field = "slug"

    def get_queryset(self):
        """Filter queryset based on user permissions with enhanced user-specific access."""
        user = self.request.user
        queryset = LeavePolicy.objects.select_related("tenant")

        # Handle schema generation (no authenticated user)
        if not user or user.is_anonymous:
            return queryset.none()

        # Check if user can view all policies (admin/owner/special permissions)
        if self._can_view_all_policies(user):
            if hasattr(self.request, "tenant") and self.request.tenant:
                return queryset.filter(tenant=self.request.tenant)
            return queryset

        # Otherwise, only show active policies for their tenant
        if hasattr(self.request, "tenant") and self.request.tenant:
            return queryset.filter(tenant=self.request.tenant, is_active=True)

        return queryset.none()

    def _can_view_all_policies(self, user):
        """Check if user can view all leave policies in the tenant."""
        # Superusers can view all
        if user.is_superuser:
            return True

        # Check for explicit permission
        if user.has_perm("leave_management.view_leavepolicy"):
            return True

        # Check tenant admin/owner role
        try:
            user_tenant = user.usertenant
            return user_tenant.is_approved and (
                user_tenant.is_owner or user_tenant.role in ["Manager", "Tenant Owner"]
            )
        except Exception:
            return False
