from rest_framework import permissions

from accounts.rbac import MANAGER_ROLES


class IsTenantAdmin(permissions.BasePermission):
    """
    Allows access to tenant administrators.

    A user qualifies as a tenant admin if they are:
    - A Django superuser / staff, OR
    - An approved UserTenant with role Department Manager or above, OR
    - The tenant owner (is_owner=True).
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_staff or request.user.is_superuser:
            return True

        try:
            user_tenant = request.user.usertenant
            return user_tenant.is_approved and (
                user_tenant.is_owner or user_tenant.role in MANAGER_ROLES
            )
        except Exception:
            pass

        return False