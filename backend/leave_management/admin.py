from django.contrib import admin

from .models import LeaveApprovalWorkflow


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
