from django.contrib import admin

from .models import ApprovalLevelConfig, LeaveApprovalStep, LeaveApprovalWorkflow


class ApprovalLevelConfigInline(admin.TabularInline):
    model = ApprovalLevelConfig
    extra = 0
    ordering = ("level",)
    fields = (
        "level",
        "approval_type",
        "specific_user",
        "permission_group",
        "required_role",
    )

    def get_formset(self, request, obj=None, **kwargs):
        """Get formset with tenant-scoped querysets."""
        formset = super().get_formset(request, obj, **kwargs)
        if obj and obj.tenant:
            tenant = obj.tenant
            # Modify the form's base fields to limit querysets
            user_field = formset.form.base_fields.get("specific_user")
            if user_field:
                user_field.queryset = user_field.queryset.filter(
                    usertenant__tenant=tenant, usertenant__is_approved=True
                )
            group_field = formset.form.base_fields.get("permission_group")
            if group_field:
                group_field.queryset = group_field.queryset.filter(tenant=tenant)
        return formset


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
    readonly_fields = fields  # Make steps read-only since they're auto-generated


@admin.register(LeaveApprovalWorkflow)
class LeaveApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tenant",
        "number_of_levels",
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
    fields = (
        "tenant",
        "name",
        "description",
        "is_default",
        "is_active",
        "created_by",
    )
    inlines = [ApprovalLevelConfigInline, LeaveApprovalStepInline]

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
