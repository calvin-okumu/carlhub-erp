from django.contrib import admin

from .models import AuditLog, CustomUser, Invitation, Tenant, UserTenant


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "groups")
    search_fields = ("email", "first_name", "last_name")
    filter_horizontal = ("groups", "user_permissions")


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "address", "created_by", "created_at")
    list_filter = ("industry", "company_size", "created_at", "created_by")
    search_fields = ("name", "domain", "created_by__email")
    readonly_fields = ("created_at", "created_by")


@admin.register(UserTenant)
class UserTenantAdmin(admin.ModelAdmin):
    list_display = ("get_user_email", "tenant", "is_owner", "is_approved", "role")
    list_filter = ("is_owner", "is_approved", "role", "tenant")
    search_fields = ("user__email", "tenant__name", "role")
    raw_id_fields = ("user", "tenant")

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = "User Email"
    get_user_email.admin_order_field = "user__email"


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "tenant", "role", "get_invited_by_email", "created_at", "get_expires_at", "is_used")
    list_filter = ("is_used", "role", "tenant", "created_at")
    search_fields = ("email", "tenant__name")
    readonly_fields = ("token", "created_at")

    def get_invited_by_email(self, obj):
        return obj.invited_by.email
    get_invited_by_email.short_description = "Invited By"
    get_invited_by_email.admin_order_field = "invited_by__email"

    def get_expires_at(self, obj):
        return obj.expires_at if obj.expires_at else "Never"
    get_expires_at.short_description = "Expires At"
    get_expires_at.admin_order_field = "expires_at"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'resource_type', 'user', 'tenant', 'ip_address')
    list_filter = ('action', 'resource_type', 'tenant', 'timestamp')
    search_fields = ('user__email', 'resource_id', 'ip_address')
    readonly_fields = ('timestamp', 'old_values', 'new_values', 'metadata')
    ordering = ('-timestamp',)
