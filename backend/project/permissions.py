from rest_framework import permissions

from accounts.models import UserTenant
from accounts.rbac import INVITER_ROLES


class HasTenantAccess(permissions.BasePermission):
    """
    Base permission class that ensures tenant isolation.
    All objects must belong to the current tenant.
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


class HasDjangoPermission(permissions.BasePermission):
    """
    Permission class that checks for specific Django permissions.
    Requires permission_map to be defined in subclasses.
    """
    permission_map = {}

    def has_permission(self, request, view) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_permission(request, view):
            return False

        # Get required permission for this action
        action = self._get_action_from_view(view)
        required_perm = self.permission_map.get(action)
        if required_perm:
            # Check both Django permissions and custom permissions
            return self._check_permission(request.user, required_perm, getattr(request, 'tenant', None))
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        # Check tenant access first
        if not HasTenantAccess().has_object_permission(request, view, obj):
            return False

        # For object permissions, typically allow view if user has view permission
        action = self._get_action_from_view(view)
        if action == 'retrieve':
            required_perm = self.permission_map.get('view')
        else:
            required_perm = self.permission_map.get(action)
        if required_perm:
            return self._check_permission(request.user, required_perm, getattr(request, 'tenant', None))
        return False

    def _check_permission(self, user, permission_codename, tenant):
        """Check both Django and custom permissions"""
        if not tenant or not permission_codename:
            return False

        # Check Django permission
        if user.has_perm(permission_codename):
            return True

        # Check custom permissions in user's permission groups
        try:
            from accounts.models import PermissionGroup
            user_groups = user.permission_groups.filter(tenant=tenant)
            for group in user_groups:
                if group.custom_permissions.filter(codename=permission_codename).exists():
                    return True
        except:
            # If custom permissions aren't available yet, just check Django permissions
            pass

        return False

    def _get_action_from_view(self, view):
        """Map DRF view actions to permission actions"""
        action_map = {
            'list': 'view',
            'retrieve': 'view',
            'create': 'add',
            'update': 'change',
            'partial_update': 'change',
            'destroy': 'delete',
        }
        return action_map.get(view.action, 'view')


class IsTenantOwner(permissions.BasePermission):
    """
    Tenant owners have full access to all tenant data.
    """
    def has_permission(self, request, view) -> bool:
        # Allow in dev mode
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        # Must be approved tenant owner
        return bool(UserTenant.objects.filter(
            user=request.user,
            tenant=request.tenant,
            is_owner=True,
            is_approved=True
        ).exists())

    def has_object_permission(self, request, view, obj) -> bool:
        # Allow in dev mode
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        # Object must belong to tenant and user must be owner
        return bool(hasattr(obj, 'tenant') and obj.tenant == request.tenant and
                UserTenant.objects.filter(
                    user=request.user,
                    tenant=request.tenant,
                    is_owner=True,
                    is_approved=True
                ).exists())


class IsTenantCreator(permissions.BasePermission):
    """
    - All tenant owners can view tenant details
    - Only the original creator can update/edit tenant information
    - No one can create or delete tenants (handled separately)
    """

    def has_permission(self, request, view):
        # Allow viewing tenants for all authenticated users in multi-tenant mode
        if view.action in ['list', 'retrieve']:
            return self._user_belongs_to_tenant(request)

        # For create/update/delete, must be tenant creator
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return self._is_tenant_creator(request)

        return False

    def has_object_permission(self, request, view, obj):
        # Allow viewing for all tenant owners
        if view.action in ['retrieve']:
            return self._user_is_tenant_owner(request, obj)

        # For update/delete, must be the creator
        if view.action in ['update', 'partial_update', 'destroy']:
            return obj.created_by == request.user

        return False

    def _user_belongs_to_tenant(self, request):
        """Check if user belongs to any tenant (for viewing)"""
        if hasattr(request, 'tenant') and request.tenant:
            from accounts.models import UserTenant
            return UserTenant.objects.filter(
                user=request.user,
                tenant=request.tenant,
                is_approved=True
            ).exists()
        return True  # Dev mode

    def _user_is_tenant_owner(self, request, tenant):
        """Check if user is an owner of the specific tenant"""
        from accounts.models import UserTenant
        return UserTenant.objects.filter(
            user=request.user,
            tenant=tenant,
            is_owner=True,
            is_approved=True
        ).exists()

    def _is_tenant_creator(self, request):
        """Check if user is the creator of their tenant"""
        if hasattr(request, 'tenant') and request.tenant:
            return request.tenant.created_by == request.user
        return False


class CanManageClients(permissions.BasePermission):
    """
    Permission for client management.
    """
    def has_permission(self, request, view) -> bool:
        # Check tenant access if tenant context exists
        if hasattr(request, 'tenant') and request.tenant is not None:
            from accounts.models import UserTenant
            if not UserTenant.objects.filter(user=request.user, tenant=request.tenant, is_approved=True).exists():
                return False

        # Check Django permission
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_client',
            'add': 'project.add_client',
            'change': 'project.change_client',
            'delete': 'project.delete_client',
        }
        required_perm = perm_map.get(action)
        return bool(required_perm and request.user.has_perm(required_perm))

    def has_object_permission(self, request, view, obj) -> bool:
        # Allow in dev mode
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        # Check tenant
        if hasattr(obj, 'tenant') and obj.tenant != request.tenant:
            return False
        # Check permission
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_client',
            'add': 'project.add_client',
            'change': 'project.change_client',
            'delete': 'project.delete_client',
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


class CanManageProjects(permissions.BasePermission):
    """
    Permission for project management.
    """
    def has_permission(self, request, view) -> bool:
        # Check tenant access if tenant context exists
        if hasattr(request, 'tenant') and request.tenant is not None:
            from accounts.models import UserTenant
            if not UserTenant.objects.filter(user=request.user, tenant=request.tenant, is_approved=True).exists():
                return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_project',
            'add': 'project.add_project',
            'change': 'project.change_project',
            'delete': 'project.delete_project',
        }
        required_perm = perm_map.get(action)
        return bool(required_perm and request.user.has_perm(required_perm))

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        if hasattr(obj, 'tenant') and obj.tenant != request.tenant:
            return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_project',
            'add': 'project.add_project',
            'change': 'project.change_project',
            'delete': 'project.delete_project',
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


class CanManageTasks(permissions.BasePermission):
    """
    Permission for task management.
    """
    def has_permission(self, request, view) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        from accounts.models import UserTenant
        if not UserTenant.objects.filter(user=request.user, tenant=request.tenant, is_approved=True).exists():
            return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_task',
            'add': 'project.add_task',
            'change': 'project.change_task',
            'delete': 'project.delete_task',
        }
        required_perm = perm_map.get(action)
        return bool(required_perm and request.user.has_perm(required_perm))

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        if hasattr(obj, 'tenant') and obj.tenant != request.tenant:
            return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_task',
            'add': 'project.add_task',
            'change': 'project.change_task',
            'delete': 'project.delete_task',
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


class CanManageInvoices(permissions.BasePermission):
    """
    Permission for invoice management.
    """
    def has_permission(self, request, view) -> bool:
        # Check tenant access if tenant context exists
        if hasattr(request, 'tenant') and request.tenant is not None:
            from accounts.models import UserTenant
            if not UserTenant.objects.filter(user=request.user, tenant=request.tenant, is_approved=True).exists():
                return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_invoice',
            'add': 'project.add_invoice',
            'change': 'project.change_invoice',
            'delete': 'project.delete_invoice',
        }
        required_perm = perm_map.get(action)
        return bool(required_perm and request.user.has_perm(required_perm))

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        if hasattr(obj, 'tenant') and obj.tenant != request.tenant:
            return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_invoice',
            'add': 'project.add_invoice',
            'change': 'project.change_invoice',
            'delete': 'project.delete_invoice',
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


class CanManagePayments(permissions.BasePermission):
    """
    Permission for payment management.
    """
    def has_permission(self, request, view) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        from accounts.models import UserTenant
        if not UserTenant.objects.filter(user=request.user, tenant=request.tenant, is_approved=True).exists():
            return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_payment',
            'add': 'project.add_payment',
            'change': 'project.change_payment',
            'delete': 'project.delete_payment',
        }
        required_perm = perm_map.get(action)
        return bool(required_perm and request.user.has_perm(required_perm))

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        if hasattr(obj, 'tenant') and obj.tenant != request.tenant:
            return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_payment',
            'add': 'project.add_payment',
            'change': 'project.change_payment',
            'delete': 'project.delete_payment',
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


class CanManageMilestones(permissions.BasePermission):
    """
    Permission for milestone management.
    """
    def has_permission(self, request, view) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        from accounts.models import UserTenant
        if not UserTenant.objects.filter(user=request.user, tenant=request.tenant, is_approved=True).exists():
            return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_milestone',
            'add': 'project.add_milestone',
            'change': 'project.change_milestone',
            'delete': 'project.delete_milestone',
        }
        required_perm = perm_map.get(action)
        return bool(required_perm and request.user.has_perm(required_perm))

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        if hasattr(obj, 'tenant') and obj.tenant != request.tenant:
            return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_milestone',
            'add': 'project.add_milestone',
            'change': 'project.change_milestone',
            'delete': 'project.delete_milestone',
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


class CanManageSprints(permissions.BasePermission):
    """
    Permission for sprint management.
    """
    def has_permission(self, request, view) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        from accounts.models import UserTenant
        if not UserTenant.objects.filter(user=request.user, tenant=request.tenant, is_approved=True).exists():
            return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_sprint',
            'add': 'project.add_sprint',
            'change': 'project.change_sprint',
            'delete': 'project.delete_sprint',
        }
        required_perm = perm_map.get(action)
        return bool(required_perm and request.user.has_perm(required_perm))

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True
        if hasattr(obj, 'tenant') and obj.tenant != request.tenant:
            return False
        action = self._get_action_from_view(view)
        perm_map = {
            'view': 'project.view_sprint',
            'add': 'project.add_sprint',
            'change': 'project.change_sprint',
            'delete': 'project.delete_sprint',
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


class CanManageInvitations(permissions.BasePermission):
    """
    Permission for the InvitationViewSet.

    Reading invitations: any approved tenant member.
    Creating / editing / deleting invitations: HR Manager role and above,
    or the tenant owner.

    This replaces the erroneous CanManageTasks guard that was previously
    applied to InvitationViewSet.
    """

    def has_permission(self, request, view) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True  # dev-mode bypass

        # Must be an approved member at minimum
        try:
            user_tenant = UserTenant.objects.get(
                user=request.user,
                tenant=request.tenant,
                is_approved=True,
            )
        except UserTenant.DoesNotExist:
            return False

        action = self._get_action_from_view(view)

        # Read-only allowed for all approved members
        if action == 'view':
            return True

        # Mutations require INVITER_ROLES or owner
        return user_tenant.is_owner or user_tenant.role in INVITER_ROLES

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(request, 'tenant') or request.tenant is None:
            return True  # dev-mode bypass
        return bool(hasattr(obj, 'tenant') and obj.tenant == request.tenant)

    def _get_action_from_view(self, view):
        action_map = {
            'list': 'view', 'retrieve': 'view',
            'create': 'add', 'update': 'change',
            'partial_update': 'change', 'destroy': 'delete',
        }
        return action_map.get(getattr(view, 'action', ''), 'view')


# Legacy classes for backward compatibility (deprecated)
class IsClientManager(CanManageClients):
    """Deprecated: Use CanManageClients instead"""
    pass

class IsProjectManager(CanManageProjects):
    """Deprecated: Use CanManageProjects instead"""
    pass

class IsAPIManager(CanManageInvoices):
    """Deprecated: Use CanManageInvoices instead"""
    pass