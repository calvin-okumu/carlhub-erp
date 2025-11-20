from django.contrib import admin

from .models import (
    LeaveApprovalStep,
    LeaveApprovalWorkflow,
    LeaveBalance,
    LeavePolicy,
    LeaveRequest,
)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "tenant",
        "leave_type",
        "start_date",
        "end_date",
        "days_requested",
        "status",
        "applied_date",
        "approved_by",
    )
    list_filter = ("status", "leave_type", "tenant", "applied_date", "approved_date")
    search_fields = (
        "employee__email",
        "employee__first_name",
        "employee__last_name",
        "tenant__name",
    )
    readonly_fields = (
        "slug",
        "days_requested",
        "applied_date",
        "approved_date",
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("employee", "tenant", "approved_by")
    ordering = ("-applied_date",)

    def get_queryset(self, request):
        """Filter queryset based on user's tenant permissions."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter to user's tenants
            user_tenants = request.user.usertenant_set.values_list("tenant", flat=True)
            qs = qs.filter(tenant__in=user_tenants)
        return qs


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "tenant",
        "leave_type",
        "year",
        "total_days",
        "used_days",
        "remaining_days",
        "utilization_percentage",
    )
    list_filter = ("leave_type", "year", "tenant")
    search_fields = (
        "employee__email",
        "employee__first_name",
        "employee__last_name",
        "tenant__name",
    )
    readonly_fields = (
        "slug",
        "remaining_days",
        "utilization_percentage",
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("employee", "tenant")
    ordering = ("-year", "employee__email")

    def get_queryset(self, request):
        """Filter queryset based on user's tenant permissions."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter to user's tenants
            user_tenants = request.user.usertenant_set.values_list("tenant", flat=True)
            qs = qs.filter(tenant__in=user_tenants)
        return qs


@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "leave_type",
        "annual_entitlement",
        "max_consecutive_days",
        "notice_period_days",
        "carry_over_allowed",
        "approval_workflow",
        "is_active",
    )
    list_filter = ("leave_type", "carry_over_allowed", "is_active", "tenant")
    search_fields = ("tenant__name", "leave_type")
    readonly_fields = ("slug", "created_at", "updated_at")
    raw_id_fields = ("tenant", "approval_workflow")
    ordering = ("tenant__name", "leave_type")

    def get_queryset(self, request):
        """Filter queryset based on user's tenant permissions."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter to user's tenants
            user_tenants = request.user.usertenant_set.values_list("tenant", flat=True)
            qs = qs.filter(tenant__in=user_tenants)
        return qs


class LeaveApprovalStepInline(admin.TabularInline):
    model = LeaveApprovalStep
    extra = 0
    ordering = ("order",)
    fields = (
        "order",
        "name",
        "approval_type",
        "specific_user",
        "permission_group",
        "required_role",
        "max_approvers",
        "selection_criteria",
        "requires_notes",
    )


@admin.register(LeaveApprovalWorkflow)
class LeaveApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tenant",
        "is_default",
        "is_active",
        "created_by",
        "created_at",
    )
    list_filter = ("is_default", "is_active", "tenant", "created_at")
    search_fields = ("name", "description", "tenant__name")
    readonly_fields = ("slug", "created_at", "updated_at")
    raw_id_fields = ("tenant", "created_by")
    ordering = ("tenant__name", "name")
    inlines = [LeaveApprovalStepInline]

    def get_queryset(self, request):
        """Filter queryset based on user's tenant permissions."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter to user's tenants
            user_tenants = request.user.usertenant_set.values_list("tenant", flat=True)
            qs = qs.filter(tenant__in=user_tenants)
        return qs

    def save_model(self, request, obj, form, change):
        """Set created_by on creation."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(LeaveApprovalStep)
class LeaveApprovalStepAdmin(admin.ModelAdmin):
    list_display = (
        "workflow",
        "order",
        "name",
        "approval_type",
        "max_approvers",
        "requires_notes",
    )
    list_filter = ("approval_type", "requires_notes", "workflow__tenant")
    search_fields = ("name", "description", "workflow__name")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("workflow", "specific_user", "permission_group")
    ordering = ("workflow", "order")

    def get_queryset(self, request):
        """Filter queryset based on user's tenant permissions."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter to user's tenants
            user_tenants = request.user.usertenant_set.values_list("tenant", flat=True)
            qs = qs.filter(workflow__tenant__in=user_tenants)
        return qs
