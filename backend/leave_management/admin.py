from django.contrib import admin

from .models import (
    LeaveApproval,
    LeaveApprovalWorkflow,
    LeaveBalance,
    LeavePolicy,
    LeaveRequest,
)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "days_requested",
        "status",
        "current_approval_level",
        "tenant",
        "applied_date",
    )
    list_filter = (
        "status",
        "leave_type",
        "tenant",
        "start_date",
        "end_date",
        "current_approval_level",
    )
    search_fields = ("employee__email", "employee__first_name", "employee__last_name", "reason")
    readonly_fields = ("slug", "created_at", "updated_at")
    raw_id_fields = ("employee", "tenant")
    ordering = ("-applied_date",)
    date_hierarchy = "applied_date"

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
        "leave_type",
        "year",
        "total_days",
        "used_days",
        "remaining_days",
        "utilization_percentage",
        "tenant",
    )
    list_filter = ("leave_type", "year", "tenant")
    search_fields = ("employee__email", "employee__first_name", "employee__last_name")
    readonly_fields = (
        "slug",
        "created_at",
        "updated_at",
        "remaining_days",
        "utilization_percentage",
    )
    raw_id_fields = ("employee", "tenant")
    ordering = ("-year", "leave_type")

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
        "is_active",
        "approval_levels_display",
    )
    list_filter = ("leave_type", "is_active", "tenant")
    search_fields = ("tenant__name",)
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

    def approval_levels_display(self, obj):
        """Display approval levels in a readable format."""
        if obj.approval_levels:
            level_names = {
                "department_manager": "Dept Mgr",
                "hr_manager": "HR Mgr",
                "general_manager": "Gen Mgr",
                "tenant_owner": "Owner",
            }
            levels = [level_names.get(level, str(level)) for level in obj.approval_levels if level]
            return " → ".join(levels) if levels else "None"
        return "Default"

    approval_levels_display.short_description = "Approval Levels"


@admin.register(LeaveApproval)
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = (
        "leave_request",
        "approver",
        "approval_level",
        "status",
        "approved_date",
        "order",
    )
    list_filter = ("status", "approval_level", "approved_date")
    search_fields = ("leave_request__employee__email", "approver__email", "notes")
    readonly_fields = ("slug", "created_at", "updated_at")
    raw_id_fields = ("leave_request", "approver")
    ordering = ("leave_request", "order")

    def get_queryset(self, request):
        """Filter queryset based on user's tenant permissions."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter to user's tenants
            user_tenants = request.user.usertenant_set.values_list("tenant", flat=True)
            qs = qs.filter(leave_request__tenant__in=user_tenants)
        return qs


@admin.register(LeaveApprovalWorkflow)
class LeaveApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tenant",
        "approval_levels",
        "number_of_levels",
        "is_default",
        "is_active",
        "created_by",
        "created_at",
    )
    list_filter = ("is_default", "is_active", "tenant", "approval_levels", "created_at")
    search_fields = ("name", "description", "tenant__name")
    readonly_fields = ("slug", "created_at", "updated_at")
    raw_id_fields = ("tenant", "created_by")
    ordering = ("tenant__name", "name")
    fields = (
        "tenant",
        "name",
        "description",
        "approval_levels",
        "is_default",
        "is_active",
        "created_by",
    )

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
