"""
Audit log service for handling audit operations.
"""

from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Q

from ..models import AuditLog
from ..permissions import IsTenantAdmin

User = get_user_model()


class AuditLogService:
    """Service for managing audit logs."""

    @staticmethod
    def get_audit_logs(user: User, filters: dict[str, Any] | None = None) -> list[AuditLog]:
        """Get audit logs based on user permissions and filters."""
        # Superusers can see all logs
        if user.is_superuser:
            queryset = AuditLog.objects.all()
        else:
            # Regular users can only see logs from their tenant
            try:
                user_tenant = user.usertenant
                if user_tenant.is_approved:
                    queryset = AuditLog.objects.filter(tenant=user_tenant.tenant)
                else:
                    return []
            except Exception:
                return []

        # Apply filters
        if filters:
            if "action" in filters:
                queryset = queryset.filter(action=filters["action"])
            if "resource_type" in filters:
                queryset = queryset.filter(resource_type=filters["resource_type"])
            if "tenant" in filters:
                queryset = queryset.filter(tenant=filters["tenant"])
            if "user" in filters:
                queryset = queryset.filter(user=filters["user"])
            if "date_from" in filters:
                queryset = queryset.filter(timestamp__gte=filters["date_from"])
            if "date_to" in filters:
                queryset = queryset.filter(timestamp__lte=filters["date_to"])

        return queryset.order_by("-timestamp")

    @staticmethod
    def get_user_audit_logs(user: User, target_user: User) -> list[AuditLog]:
        """Get audit logs for a specific user."""
        # Check if user has permission to view target user's logs
        if not AuditLogService.can_view_user_logs(user, target_user):
            return []

        return AuditLog.objects.filter(user=target_user).order_by("-timestamp")

    @staticmethod
    def get_tenant_audit_logs(user: User) -> list[AuditLog]:
        """Get audit logs for user's tenant."""
        try:
            user_tenant = user.usertenant
            if user_tenant.is_approved:
                return AuditLog.objects.filter(tenant=user_tenant.tenant).order_by("-timestamp")
        except Exception:
            pass

        return []

    @staticmethod
    def search_audit_logs(user: User, query: str) -> list[AuditLog]:
        """Search audit logs by query string."""
        base_queryset = AuditLogService._get_base_queryset(user)

        if not base_queryset.exists():
            return []

        # Search in multiple fields
        search_filters = (
            Q(action__icontains=query)
            | Q(resource_type__icontains=query)
            | Q(resource_id__icontains=query)
            | Q(user__email__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(ip_address__icontains=query)
        )

        return base_queryset.filter(search_filters).order_by("-timestamp")

    @staticmethod
    def get_audit_log_statistics(user: User, days: int = 30) -> dict[str, Any]:
        """Get audit log statistics for the last N days."""
        from datetime import timedelta

        from django.utils import timezone

        date_threshold = timezone.now() - timedelta(days=days)
        base_queryset = AuditLogService._get_base_queryset(user)
        queryset = base_queryset.filter(timestamp__gte=date_threshold)

        # Action statistics
        action_stats = {}
        for log in queryset:
            action = log.get_action_display()
            action_stats[action] = action_stats.get(action, 0) + 1

        # Resource type statistics
        resource_stats = {}
        for log in queryset:
            resource_type = log.get_resource_type_display()
            resource_stats[resource_type] = resource_stats.get(resource_type, 0) + 1

        # User activity statistics
        user_stats = {}
        for log in queryset:
            user_email = log.user.email if log.user else "Unknown"
            user_stats[user_email] = user_stats.get(user_email, 0) + 1

        return {
            "total_logs": queryset.count(),
            "action_distribution": action_stats,
            "resource_distribution": resource_stats,
            "user_activity": user_stats,
            "date_range": {"from": date_threshold, "to": timezone.now()},
        }

    @staticmethod
    def can_view_user_logs(user: User, target_user: User) -> bool:
        """Check if user can view target user's audit logs."""
        # Users can always view their own logs
        if user == target_user:
            return True

        # Superusers can view any logs
        if user.is_superuser:
            return True

        # Check if users are in the same tenant and user has admin permissions
        try:
            user_tenant = user.usertenant
            target_tenant = target_user.usertenant

            if (
                user_tenant.is_approved
                and target_tenant.is_approved
                and user_tenant.tenant == target_tenant.tenant
            ):
                # Check if user has tenant admin permissions
                return IsTenantAdmin().has_object_permission(user, user_tenant.tenant)
        except Exception:
            pass

        return False

    @staticmethod
    def _get_base_queryset(user: User):
        """Get base queryset based on user permissions."""
        # Superusers can see all logs
        if user.is_superuser:
            return AuditLog.objects.all()

        # Regular users can only see logs from their tenant
        try:
            user_tenant = user.usertenant
            if user_tenant.is_approved:
                return AuditLog.objects.filter(tenant=user_tenant.tenant)
        except Exception:
            pass

        return AuditLog.objects.none()

    @staticmethod
    def export_audit_logs(
        user: User, format_type: str = "csv", filters: dict[str, Any] | None = None
    ) -> str:
        """Export audit logs in specified format."""
        import csv
        from io import StringIO

        logs = AuditLogService.get_audit_logs(user, filters)

        if format_type.lower() == "csv":
            output = StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(
                [
                    "Timestamp",
                    "User",
                    "Action",
                    "Resource Type",
                    "Resource ID",
                    "IP Address",
                    "Details",
                ]
            )

            # Write data
            for log in logs:
                writer.writerow(
                    [
                        log.timestamp,
                        log.user.email if log.user else "",
                        log.get_action_display(),
                        log.get_resource_type_display(),
                        log.resource_id,
                        log.ip_address,
                        log.details or "",
                    ]
                )

            return output.getvalue()

        # Add other export formats as needed
        return ""

    @staticmethod
    def cleanup_old_logs(days: int = 365) -> int:
        """Clean up audit logs older than specified days."""
        from datetime import timedelta

        from django.utils import timezone

        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = AuditLog.objects.filter(timestamp__lt=cutoff_date).delete()

        return deleted_count
