"""
Admin configuration for audit app.
"""
from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'resource_type', 'resource_id', 'user_id', 'tenant_id', 'timestamp']
    list_filter = ['action', 'resource_type', 'timestamp']
    search_fields = ['resource_id', 'user_id', 'tenant_id']
    readonly_fields = ['id', 'tenant_id', 'user_id', 'action', 'resource_type', 'resource_id', 'old_values', 'new_values', 'ip_address', 'user_agent', 'timestamp', 'metadata']
    ordering = ['-timestamp']
