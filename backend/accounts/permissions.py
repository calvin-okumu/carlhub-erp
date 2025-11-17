from rest_framework import permissions


class IsTenantAdmin(permissions.BasePermission):
    """
    Custom permission to only allow tenant admins to view audit logs.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check if user is admin or has admin role in any tenant
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check tenant admin roles
        try:
            # Since UserTenant is OneToOne, check the single relationship
            user_tenant = request.user.usertenant
            if user_tenant.is_approved and (user_tenant.is_owner or user_tenant.role in ['Manager', 'Tenant Owner']):
                return True
        except:
            pass

        return False