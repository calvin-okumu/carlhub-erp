from rest_framework import permissions

from accounts.models import UserTenant


def is_tenant_admin_or_owner(user):
    """Check if user is tenant admin or owner."""
    # Superusers are always admins
    if user.is_superuser:
        return True
    
    # Check tenant admin/owner role
    try:
        user_tenant = user.usertenant
        return user_tenant.is_approved and (user_tenant.is_owner or user_tenant.role in ['admin', 'owner'])
    except:
        return False


class HasTenantAccess(permissions.BasePermission):
    """
    Base permission class that ensures tenant isolation for leave management.
    All leave objects must belong to the current tenant.
    """
    def has_permission(self, request, view) -> bool:
        # Allow in dev mode (no tenant context)
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        # User must be associated with the tenant
        return bool(UserTenant.objects.filter(user=request.user, tenant=request.tenant, is_approved=True).exists())

    def has_object_permission(self, request, view, obj) -> bool:
        # Allow in dev mode
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        # Object must belong to current tenant
        return bool(hasattr(obj, 'tenant') and obj.tenant == request.tenant)


class CanManageLeaveRequests(permissions.BasePermission):
    """
    Permission for leave request management.
    Employees can view/create their own requests.
    Managers can view/approve all requests in their tenant.
    """
    def has_permission(self, request, view) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_permission(request, view):
            return False

        action = self._get_action_from_view(view)

        # Employees can view and create their own requests
        if action in ['view', 'add']:
            return True

        # For approve/change/delete, need specific permissions
        if action in ['change', 'delete']:
            perm_map = {
                'change': 'leave_management.change_leaverequest',
                'delete': 'leave_management.delete_leaverequest',
            }
            required_perm = perm_map.get(action)
            return bool(required_perm and request.user.has_perm(required_perm))

        return False

    def has_object_permission(self, request, view, obj) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_object_permission(request, view, obj):
            return False

        action = self._get_action_from_view(view)

        # Employees can view their own requests
        if action == 'view':
            return obj.employee == request.user or request.user.has_perm('leave_management.view_leaverequest') or is_tenant_admin_or_owner(request.user)

        # Employees can only modify their own pending requests
        if action == 'change':
            if obj.employee == request.user and obj.status == 'pending':
                return True
            # Managers/admins can approve/reject any request
            return request.user.has_perm('leave_management.change_leaverequest') or is_tenant_admin_or_owner(request.user)

        # Only admins can delete requests
        if action == 'delete':
            return request.user.has_perm('leave_management.delete_leaverequest') or is_tenant_admin_or_owner(request.user)

        return False

    def _get_action_from_view(self, view):
        action_map = {
            'list': 'view',
            'retrieve': 'view',
            'create': 'add',
            'update': 'change',
            'partial_update': 'change',
            'destroy': 'delete',
        }
        return action_map.get(view.action, 'view')


class CanApproveLeaves(permissions.BasePermission):
    """
    Permission for leave approval actions.
    Only managers and admins can approve/reject leave requests.
    """
    def has_permission(self, request, view) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_permission(request, view):
            return False

        # Must have permission to change leave requests (approve/reject)
        return request.user.has_perm('leave_management.change_leaverequest') or is_tenant_admin_or_owner(request.user)

    def has_object_permission(self, request, view, obj) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_object_permission(request, view, obj):
            return False

        # Must have permission to change leave requests
        return request.user.has_perm('leave_management.change_leaverequest') or is_tenant_admin_or_owner(request.user)


class CanManageLeaveBalances(permissions.BasePermission):
    """
    Permission for leave balance management.
    Typically restricted to HR admins.
    """
    def has_permission(self, request, view) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_permission(request, view):
            return False

        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'leave_management.view_leavebalance',
            'add': 'leave_management.add_leavebalance',
            'change': 'leave_management.change_leavebalance',
            'delete': 'leave_management.delete_leavebalance',
        }
        required_perm = perm_map.get(action)
        return bool(required_perm and request.user.has_perm(required_perm))

    def has_object_permission(self, request, view, obj) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_object_permission(request, view, obj):
            return False

        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'leave_management.view_leavebalance',
            'change': 'leave_management.change_leavebalance',
            'delete': 'leave_management.delete_leavebalance',
        }
        required_perm = perm_map.get(action)
        return bool(required_perm and request.user.has_perm(required_perm))

    def _get_action_from_view(self, view):
        action_map = {
            'list': 'view',
            'retrieve': 'view',
            'create': 'add',
            'update': 'change',
            'partial_update': 'change',
            'destroy': 'delete',
        }
        return action_map.get(view.action, 'view')


class CanManageLeavePolicies(permissions.BasePermission):
    """
    Permission for leave policy management.
    Restricted to tenant admins/owners.
    """
    def has_permission(self, request, view) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_permission(request, view):
            return False

        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'leave_management.view_leavepolicy',
            'add': 'leave_management.add_leavepolicy',
            'change': 'leave_management.change_leavepolicy',
            'delete': 'leave_management.delete_leavepolicy',
        }
        required_perm = perm_map.get(action)
        return bool(required_perm and request.user.has_perm(required_perm))

    def has_object_permission(self, request, view, obj) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_object_permission(request, view, obj):
            return False

        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'leave_management.view_leavepolicy',
            'change': 'leave_management.change_leavepolicy',
            'delete': 'leave_management.delete_leavepolicy',
        }
        required_perm = perm_map.get(action)
        return bool(required_perm and request.user.has_perm(required_perm))

    def _get_action_from_view(self, view):
        action_map = {
            'list': 'view',
            'retrieve': 'view',
            'create': 'add',
            'update': 'change',
            'partial_update': 'change',
            'destroy': 'delete',
        }
        return action_map.get(view.action, 'view')


class IsLeaveManager(permissions.BasePermission):
    """
    Special permission for leave managers who can approve leaves and manage balances.
    """
    def has_permission(self, request, view) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_permission(request, view):
            return False

        # Must have leave management permissions
        return (request.user.has_perm('leave_management.change_leaverequest') or
                request.user.has_perm('leave_management.change_leavebalance'))

    def has_object_permission(self, request, view, obj) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_object_permission(request, view, obj):
            return False

        # Must have appropriate permissions for the object type
        if hasattr(obj, 'employee'):  # LeaveRequest or LeaveBalance
            return (request.user.has_perm('leave_management.change_leaverequest') or
                    request.user.has_perm('leave_management.change_leavebalance'))
        elif hasattr(obj, 'annual_entitlement'):  # LeavePolicy
            return request.user.has_perm('leave_management.change_leavepolicy')

        return False