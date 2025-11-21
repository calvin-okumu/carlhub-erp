from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.models import Invitation, UserTenant

from .models import (
    ApprovalLevelConfig,
    LeaveApproval,
    LeaveApprovalWorkflow,
    LeaveBalance,
    LeavePolicy,
    LeaveRequest,
)
from .services import LeaveApprovalWorkflowService


class LeaveRequestSerializer(serializers.ModelSerializer):
    """Serializer for leave requests with comprehensive validation and display fields."""

    employee_name = serializers.CharField(
        source="employee.get_full_name",
        read_only=True,
        help_text="Full name of the employee",
    )
    tenant_name = serializers.CharField(
        source="tenant.name",
        read_only=True,
        help_text="Name of the tenant organization",
    )
    approved_by_name = serializers.CharField(
        source="approved_by.get_full_name",
        read_only=True,
        help_text="Name of the approver",
    )
    final_approver_name = serializers.CharField(
        source="final_approver.get_full_name",
        read_only=True,
        help_text="Name of the final approver",
    )
    duration_display = serializers.CharField(read_only=True, help_text="Human-readable duration")

    # Workflow fields
    workflow_status = serializers.SerializerMethodField(
        help_text="Current workflow status information"
    )
    approval_history = serializers.SerializerMethodField(help_text="Complete approval history")
    current_approver = serializers.SerializerMethodField(
        help_text="Current approver in the workflow"
    )
    can_approve = serializers.SerializerMethodField(
        help_text="Whether current user can approve this request"
    )
    next_approval_level = serializers.CharField(
        read_only=True, help_text="Next approval level in workflow"
    )

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "slug",
            "employee",
            "employee_name",
            "tenant",
            "tenant_name",
            "leave_type",
            "start_date",
            "end_date",
            "days_requested",
            "reason",
            "status",
            "applied_date",
            "approved_by",
            "approved_by_name",
            "final_approver",
            "final_approver_name",
            "approved_date",
            "approval_notes",
            "duration_display",
            "current_approval_level",
            "next_approval_level",
            "workflow_status",
            "approval_history",
            "current_approver",
            "can_approve",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "employee",
            "employee_name",
            "tenant",
            "tenant_name",
            "days_requested",
            "approved_by_name",
            "final_approver_name",
            "duration_display",
            "current_approval_level",
            "next_approval_level",
            "workflow_status",
            "approval_history",
            "current_approver",
            "can_approve",
            "created_at",
            "updated_at",
        ]
        help_texts = {
            "employee": "Employee requesting leave",
            "tenant": "Company/tenant the request belongs to",
            "leave_type": "Type of leave being requested",
            "start_date": "First day of leave (must be a weekday)",
            "end_date": "Last day of leave (must be after start date)",
            "days_requested": "Total number of leave days (calculated automatically)",
            "reason": "Reason for the leave request",
            "status": "Current status of the leave request",
            "applied_date": "When the leave request was submitted (auto-set)",
            "approved_by": "Manager who approved/rejected the request (legacy field)",
            "final_approver": "Final approver in the workflow chain",
            "approved_date": "When the request was approved/rejected",
            "approval_notes": "Notes from the approver",
            "current_approval_level": "Current approval level in workflow",
        }

    def validate(self, data):
        """Validate leave request data."""
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError("End date must be after start date.")

            # Check for overlapping leave requests
            employee = self.context["request"].user
            tenant = getattr(self.context["request"], "tenant", None)

            if tenant:
                overlapping = LeaveRequest.objects.filter(
                    employee=employee,
                    tenant=tenant,
                    status__in=["pending", "approved"],
                    start_date__lte=end_date,
                    end_date__gte=start_date,
                ).exclude(pk=getattr(self.instance, "pk", None))

                if overlapping.exists():
                    raise serializers.ValidationError(
                        "You have overlapping leave requests for these dates."
                    )

        return data

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_workflow_status(self, obj):
        """Get comprehensive workflow status."""
        return LeaveApprovalWorkflowService.get_workflow_status(obj)

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_approval_history(self, obj):
        """Get approval history with approver details."""
        history = obj.get_approval_history()
        return [
            {
                "id": approval.id,
                "level": approval.approval_level,
                "level_display": approval.get_approval_level_display(),
                "approver": (approval.approver.get_full_name() if approval.approver else None),
                "status": approval.status,
                "approved_date": approval.approved_date,
                "notes": approval.notes,
                "order": approval.order,
            }
            for approval in history
        ]

    @extend_schema_field(OpenApiTypes.STR)
    def get_current_approver(self, obj):
        """Get current approver in workflow."""
        current_approver = obj.get_current_approver()
        return current_approver.get_full_name() if current_approver else None

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_can_approve(self, obj):
        """Check if current user can approve this request."""
        request = self.context.get("request")
        if not request or not request.user:
            return False

        if obj.is_pending:
            can_approve, _ = LeaveApprovalWorkflowService.can_approve_at_level(
                request.user, obj, obj.current_approval_level
            )
            return can_approve
        return False

    def _can_create_for_others(self, user):
        """Check if user can create leave requests for others."""
        # Superusers can create for anyone
        if user.is_superuser:
            return True

        # Check if user has tenant admin/owner role
        try:
            user_tenant = user.usertenant
            return user_tenant.is_approved and (
                user_tenant.is_owner or user_tenant.role in ["Manager", "Tenant Owner"]
            )
        except Exception:
            return False

    def create(self, validated_data):
        """Create leave request with tenant context and user-specific validation."""
        request = self.context["request"]

        # Check if user is trying to create for someone else (from initial data)
        initial_data = self.initial_data if hasattr(self, "initial_data") else {}
        if "employee" in initial_data:
            try:
                target_employee_id = initial_data["employee"]
                if target_employee_id != request.user.id:
                    if not self._can_create_for_others(request.user):
                        raise serializers.ValidationError(
                            "You can only create leave requests for yourself."
                        )
            except (ValueError, TypeError):
                pass  # Invalid employee ID, let field validation handle it

        validated_data["employee"] = request.user

        # Set tenant from request context
        if hasattr(request, "tenant") and request.tenant:
            validated_data["tenant"] = request.tenant
        else:
            # Fallback for dev mode - get tenant from user's approved UserTenant relationship
            try:
                user_tenant = UserTenant.objects.get(user=request.user)
                if user_tenant.is_approved:
                    validated_data["tenant"] = user_tenant.tenant
                else:
                    raise serializers.ValidationError(
                        "Your tenant membership is pending approval. Only approved tenant members can create leave requests."
                    )
            except UserTenant.DoesNotExist:
                # Check if user has pending invitations
                pending_invitations = Invitation.objects.filter(
                    email=request.user.email, is_used=False
                ).select_related("tenant")

                if pending_invitations.exists():
                    invitation_info = []
                    for inv in pending_invitations:
                        status = "expired" if inv.is_expired() else "pending"
                        invitation_info.append(f"{inv.tenant.name} ({status})")

                    raise serializers.ValidationError(
                        f"You have pending invitations but haven't accepted any yet: "
                        f"{', '.join(invitation_info)}. Please accept an invitation to create leave requests."
                    ) from None
                else:
                    raise serializers.ValidationError(
                        "You are not a member of any tenant. Only approved tenant members can create leave requests."
                    ) from None
            except Exception as e:
                raise serializers.ValidationError(
                    f"Unable to determine tenant context: {str(e)}"
                ) from e

        # Create the leave request
        leave_request = super().create(validated_data)

        # Initialize the approval workflow
        LeaveApprovalWorkflowService.initialize_workflow(leave_request)

        return leave_request


class LeaveBalanceSerializer(serializers.ModelSerializer):
    """Serializer for leave balances with utilization calculations."""

    employee_name = serializers.CharField(
        source="employee.get_full_name",
        read_only=True,
        help_text="Full name of the employee",
    )
    tenant_name = serializers.CharField(
        source="tenant.name",
        read_only=True,
        help_text="Name of the tenant organization",
    )
    remaining_days = serializers.DecimalField(
        max_digits=5,
        decimal_places=1,
        read_only=True,
        help_text="Remaining leave days available",
    )
    utilization_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=1,
        read_only=True,
        help_text="Leave utilization percentage",
    )

    class Meta:
        model = LeaveBalance
        fields = [
            "id",
            "slug",
            "employee",
            "employee_name",
            "tenant",
            "tenant_name",
            "leave_type",
            "year",
            "total_days",
            "used_days",
            "carried_over",
            "remaining_days",
            "utilization_percentage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "employee_name",
            "tenant_name",
            "remaining_days",
            "utilization_percentage",
            "created_at",
            "updated_at",
        ]
        help_texts = {
            "employee": "Employee whose leave balance this represents",
            "tenant": "Company/tenant the balance belongs to",
            "leave_type": "Type of leave this balance applies to",
            "year": "Calendar year for this leave balance",
            "total_days": "Total leave days allocated for this year",
            "used_days": "Days already used this year",
            "carried_over": "Days carried over from previous year",
        }


class LeavePolicySerializer(serializers.ModelSerializer):
    """Serializer for leave policies with validation."""

    tenant_name = serializers.CharField(
        source="tenant.name",
        read_only=True,
        help_text="Name of the tenant organization",
    )

    class Meta:
        model = LeavePolicy
        fields = [
            "id",
            "slug",
            "tenant",
            "tenant_name",
            "leave_type",
            "annual_entitlement",
            "max_consecutive_days",
            "notice_period_days",
            "carry_over_allowed",
            "max_carry_over",
            "auto_approve_max_days",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "tenant",
            "tenant_name",
            "created_at",
            "updated_at",
        ]
        help_texts = {
            "tenant": "Company/tenant this policy applies to",
            "leave_type": "Type of leave this policy applies to",
            "annual_entitlement": "Default annual leave entitlement in days",
            "max_consecutive_days": "Maximum consecutive days allowed for this leave type",
            "notice_period_days": "Minimum notice period required in working days",
            "carry_over_allowed": "Whether unused leave can be carried over to next year",
            "max_carry_over": "Maximum days that can be carried over (null = unlimited)",
            "auto_approve_max_days": "Maximum days that can be auto-approved (null = no auto-approval)",
            "is_active": "Whether this policy is currently active",
        }

    def validate(self, data):
        """Validate leave policy data."""
        carry_over_allowed = data.get("carry_over_allowed", True)
        max_carry_over = data.get("max_carry_over")

        if not carry_over_allowed and max_carry_over is not None:
            raise serializers.ValidationError(
                "Cannot set max_carry_over when carry_over_allowed is False."
            )

        return data

    def create(self, validated_data):
        """Create leave policy with tenant context."""
        request = self.context["request"]

        # Set tenant from request context
        if hasattr(request, "tenant") and request.tenant:
            validated_data["tenant"] = request.tenant
        else:
            # Fallback for dev mode - get tenant from user's ownership
            try:
                user_tenant = UserTenant.objects.get(user=request.user)
                if user_tenant.is_approved:
                    validated_data["tenant"] = user_tenant.tenant
                else:
                    raise serializers.ValidationError(
                        "Your tenant membership is pending approval. Only approved tenant members can create leave policies."
                    )
            except UserTenant.DoesNotExist:
                raise serializers.ValidationError(
                    "You are not a member of any tenant. Only approved tenant members can create leave policies."
                ) from None
            except Exception as e:
                raise serializers.ValidationError(
                    f"Unable to determine tenant context: {str(e)}"
                ) from e

        return super().create(validated_data)


class LeaveApprovalSerializer(serializers.ModelSerializer):
    """Serializer for leave approval records with workflow information."""

    approver_name = serializers.CharField(
        source="approver.get_full_name",
        read_only=True,
        help_text="Name of the approver",
    )
    level_display = serializers.CharField(
        source="get_approval_level_display",
        read_only=True,
        help_text="Display name of approval level",
    )

    class Meta:
        model = LeaveApproval
        fields = [
            "id",
            "slug",
            "leave_request",
            "approval_level",
            "level_display",
            "approver",
            "approver_name",
            "status",
            "approved_date",
            "notes",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "approver_name",
            "level_display",
            "approved_date",
            "created_at",
            "updated_at",
        ]
        help_texts = {
            "leave_request": "Leave request being approved",
            "approval_level": "Level in the approval chain",
            "approver": "User who performed the approval",
            "status": "Approval status (pending/approved/rejected)",
            "notes": "Notes from the approver",
            "order": "Order in the approval sequence",
        }


class LeaveApprovalActionSerializer(serializers.Serializer):
    """Serializer for leave approval actions."""

    action = serializers.ChoiceField(
        choices=["approve", "reject"],
        help_text="Action to perform on the leave request",
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Optional notes explaining the decision",
    )

    def validate(self, data):
        """Validate approval action data."""
        action = data.get("action")
        notes = data.get("notes", "")

        if action == "reject" and not notes.strip():
            raise serializers.ValidationError("Notes are required when rejecting a leave request.")

        return data


class ApprovalLevelConfigSerializer(serializers.ModelSerializer):
    """Serializer for approval level configurations."""

    approval_type_display = serializers.CharField(
        source="get_approval_type_display",
        read_only=True,
        help_text="Human-readable approval type",
    )

    specific_user_name = serializers.CharField(
        source="specific_user.get_full_name",
        read_only=True,
        help_text="Full name of the specific user",
    )

    permission_group_name = serializers.CharField(
        source="permission_group.name",
        read_only=True,
        help_text="Name of the permission group",
    )

    required_role_display = serializers.CharField(
        source="get_required_role_display",
        read_only=True,
        help_text="Human-readable required role",
    )

    class Meta:
        model = ApprovalLevelConfig
        fields = [
            "id",
            "level",
            "approval_type",
            "approval_type_display",
            "specific_user",
            "specific_user_name",
            "permission_group",
            "permission_group_name",
            "required_role",
            "required_role_display",
        ]
        read_only_fields = ["id"]


class LeaveApprovalWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for leave approval workflows."""

    level_configs = ApprovalLevelConfigSerializer(many=True, read_only=True)
    number_of_levels = serializers.SerializerMethodField(
        help_text="Number of approval levels in this workflow (maximum 5)",
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
        help_text="Name of the user who created this workflow",
    )

    class Meta:
        model = LeaveApprovalWorkflow
        fields = [
            "id",
            "name",
            "description",
            "is_default",
            "is_active",
            "level_configs",
            "number_of_levels",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by_name"]

    def get_number_of_levels(self, obj):
        """Get the number of approval levels."""
        return obj.level_configs.count()

    def create(self, validated_data):
        """Create workflow with level configs."""
        level_configs_data = self.context.get("level_configs", [])
        validated_data["created_by"] = self.context["request"].user

        workflow = super().create(validated_data)

        # Create level configs
        for config_data in level_configs_data:
            ApprovalLevelConfig.objects.create(workflow=workflow, **config_data)

        return workflow

    def update(self, instance, validated_data):
        """Update workflow and level configs."""
        level_configs_data = self.context.get("level_configs", [])

        # Update workflow
        instance = super().update(instance, validated_data)

        # Delete existing configs and create new ones
        instance.level_configs.all().delete()
        for config_data in level_configs_data:
            ApprovalLevelConfig.objects.create(workflow=instance, **config_data)

        return instance
