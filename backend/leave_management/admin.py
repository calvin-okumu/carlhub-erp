from django.contrib import admin

from .models import LeaveBalance, LeavePolicy, LeaveRequest


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
        "is_active",
    )
    list_filter = ("leave_type", "carry_over_allowed", "is_active", "tenant")
    search_fields = ("tenant__name", "leave_type")
    readonly_fields = ("slug", "created_at", "updated_at")
    raw_id_fields = ("tenant",)
    ordering = ("tenant__name", "leave_type")

    def get_queryset(self, request):
        """Filter queryset based on user's tenant permissions."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter to user's tenants
            user_tenants = request.user.usertenant_set.values_list("tenant", flat=True)
            qs = qs.filter(tenant__in=user_tenants)
        return qs
