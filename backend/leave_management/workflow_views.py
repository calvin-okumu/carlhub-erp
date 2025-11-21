from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ApprovalLevelConfig, LeaveApprovalWorkflow
from .permissions import CanManageLeavePolicies
from .serializers import ApprovalLevelConfigSerializer, LeaveApprovalWorkflowSerializer
from .services import (
    LeaveAnalyticsService,
    LeaveApprovalWorkflowService,
    LeaveNotificationService,
)


class LeaveApprovalWorkflowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave approval workflows.

    Allows HR and management to configure approval workflows for leave requests.
    """

    serializer_class = LeaveApprovalWorkflowSerializer
    permission_classes = [CanManageLeavePolicies]  # HR and above can manage workflows
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active", "is_default"]

    def get_queryset(self):
        """Filter workflows by user's tenant."""
        user = self.request.user
        if user.is_superuser:
            return LeaveApprovalWorkflow.objects.all()
        else:
            # Get user's tenant
            user_tenant = user.usertenant_set.filter(is_approved=True).first()
            if user_tenant:
                return LeaveApprovalWorkflow.objects.filter(tenant=user_tenant.tenant)
            return LeaveApprovalWorkflow.objects.none()

    def get_serializer_context(self):
        """Add request context for serializer."""
        context = super().get_serializer_context()
        context["level_configs"] = self.request.data.get("level_configs", [])
        return context

    def perform_create(self, serializer):
        """Set tenant when creating workflow."""
        user = self.request.user
        if not user.is_superuser:
            user_tenant = user.usertenant_set.filter(is_approved=True).first()
            if user_tenant:
                serializer.save(tenant=user_tenant.tenant)
            else:
                from rest_framework import serializers

                raise serializers.ValidationError("User must be approved in a tenant.")
        else:
            # Superuser must specify tenant
            if not self.request.data.get("tenant"):
                from rest_framework import serializers

                raise serializers.ValidationError("Superuser must specify tenant.")
            serializer.save()

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """Set this workflow as the default for the tenant."""
        workflow = self.get_object()

        # Unset other defaults for this tenant
        LeaveApprovalWorkflow.objects.filter(tenant=workflow.tenant, is_default=True).exclude(
            pk=workflow.pk
        ).update(is_default=False)

        # Set this as default
        workflow.is_default = True
        workflow.save()

        serializer = self.get_serializer(workflow)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def level_configs(self, request, pk=None):
        """Get level configurations for this workflow."""
        workflow = self.get_object()
        configs = workflow.level_configs.all()
        serializer = ApprovalLevelConfigSerializer(configs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["put"])
    def update_configs(self, request, pk=None):
        """Update level configurations for this workflow."""
        workflow = self.get_object()
        configs_data = request.data.get("level_configs", [])

        # Validate configs
        for config_data in configs_data:
            config_serializer = ApprovalLevelConfigSerializer(data=config_data)
            if not config_serializer.is_valid():
                return Response(config_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Delete existing configs
        workflow.level_configs.all().delete()

        # Create new configs
        for config_data in configs_data:
            ApprovalLevelConfig.objects.create(workflow=workflow, **config_data)

        # Return updated workflow
        serializer = self.get_serializer(workflow)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get approval analytics for the tenant."""
        user = request.user
        if not hasattr(user, "usertenant_set"):
            return Response({"error": "User tenant not found"}, status=400)

        user_tenant = user.usertenant_set.filter(is_approved=True).first()
        if not user_tenant:
            return Response({"error": "User not approved in any tenant"}, status=400)

        # Parse date parameters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            from datetime import datetime

            start_date = datetime.fromisoformat(start_date).date()
        if end_date:
            from datetime import datetime

            end_date = datetime.fromisoformat(end_date).date()

        analytics = LeaveAnalyticsService.get_approval_metrics(
            user_tenant.tenant, start_date, end_date
        )

        return Response(analytics)

    @action(detail=False, methods=["get"])
    def notifications_summary(self, request):
        """Get pending approvals summary for the current user."""
        summary = LeaveNotificationService.get_pending_approvals_summary(request.user)
        return Response(summary)

    @action(detail=False, methods=["post"])
    def send_reminders(self, request):
        """Send approval reminders for overdue requests."""
        # Check if user has permission (HR/Admin only)
        user = request.user
        if not hasattr(user, "usertenant_set"):
            return Response({"error": "Permission denied"}, status=403)

        user_tenant = user.usertenant_set.filter(is_approved=True).first()
        if not user_tenant or user_tenant.role not in ["HR Manager", "Tenant Owner"]:
            return Response({"error": "Permission denied"}, status=403)

        reminders_sent = LeaveNotificationService.send_pending_approval_reminders()
        return Response(
            {
                "message": f"Sent {reminders_sent} approval reminders",
                "reminders_sent": reminders_sent,
            }
        )

    @action(detail=False, methods=["post"])
    def send_escalations(self, request):
        """Send escalation notifications for critically overdue requests."""
        # Check if user has permission (Admin only)
        user = request.user
        if not hasattr(user, "usertenant_set"):
            return Response({"error": "Permission denied"}, status=403)

        user_tenant = user.usertenant_set.filter(is_approved=True).first()
        if not user_tenant or user_tenant.role not in ["Tenant Owner"]:
            return Response({"error": "Permission denied - Admin only"}, status=403)

        escalations_sent = LeaveNotificationService.send_escalation_notifications()
        return Response(
            {
                "message": f"Sent {escalations_sent} escalation notifications",
                "escalations_sent": escalations_sent,
            }
        )

    @action(detail=True, methods=["post"])
    def quick_approve(self, request, pk=None):
        """Quick approve for mobile - minimal data required."""
        workflow = self.get_object()

        # For quick approval, just mark as approved without detailed notes
        result = LeaveApprovalWorkflowService.process_approval(
            workflow,  # This should be the leave request, not workflow
            request.user,
            "approve",
            "Quick approved via mobile",
            request,
        )

        if result["success"]:
            return Response(
                {"message": "Request approved", "status": result.get("status", "approved")}
            )
        else:
            return Response({"error": result["message"]}, status=400)

    @action(detail=True, methods=["post"])
    def quick_reject(self, request, pk=None):
        """Quick reject for mobile - requires reason."""
        workflow = self.get_object()
        reason = request.data.get("reason", "").strip()

        if not reason:
            return Response({"error": "Rejection reason is required"}, status=400)

        result = LeaveApprovalWorkflowService.process_approval(
            workflow,  # This should be the leave request
            request.user,
            "reject",
            f"Quick rejected: {reason}",
            request,
        )

        if result["success"]:
            return Response(
                {"message": "Request rejected", "status": result.get("status", "rejected")}
            )
        else:
            return Response({"error": result["message"]}, status=400)
