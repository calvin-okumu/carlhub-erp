from rest_framework import permissions

from accounts.models import UserTenant
from accounts.rbac import MANAGER_ROLES
# Import the canonical HasTenantAccess — no duplication needed
from project.permissions import HasTenantAccess  # noqa: F401 (re-exported for compat)


def is_tenant_admin_or_owner(user):
    """Return True if the user holds a manager-level role or is the tenant owner.

    Accepts: superusers, approved UserTenants with role in MANAGER_ROLES, or
    any user where is_owner=True.
    """
    if user.is_superuser:
        return True

    try:
        user_tenant = user.usertenant
        return user_tenant.is_approved and (
            user_tenant.is_owner or user_tenant.role in MANAGER_ROLES
        )
    except Exception:
        return False


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
            # Managers and Tenant Owners can approve/reject any request
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
    Only Managers and Tenant Owners can approve/reject leave requests.
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