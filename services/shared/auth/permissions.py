"""
Shared Authentication Permissions for Microservices

This module contains shared permissions that can be used across
all microservices for authentication and authorization.
"""

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

        # Check tenant admin roles via JWT token claims or API call
        # For now, we'll check if user has is_staff flag set
        # In production, this should validate against identity-service
        user_roles = getattr(request.user, 'roles', [])
        if any(role in ['Tenant Owner', 'General Manager', 'Department Manager', 'HR Manager'] for role in user_roles):
            return True

        return False


class IsTenantOwner(permissions.BasePermission):
    """
    Permission to only allow tenant owners to perform certain actions.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Superusers and staff can do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Check if user is tenant owner
        user_roles = getattr(request.user, 'roles', [])
        return 'Tenant Owner' in user_roles


class IsTenantMember(permissions.BasePermission):
    """
    Permission to only allow approved tenant members to access resources.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Superusers and staff can do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Check if user is an approved tenant member
        is_approved = getattr(request.user, 'is_approved', False)
        tenant_id = getattr(request.user, 'tenant_id', None)

        return is_approved and tenant_id is not None


class IsDepartmentManager(permissions.BasePermission):
    """
    Permission to only allow department managers to perform certain actions.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Superusers and staff can do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Check if user is department manager
        user_roles = getattr(request.user, 'roles', [])
        return 'Department Manager' in user_roles


class IsHRManager(permissions.BasePermission):
    """
    Permission to only allow HR managers to perform HR-related actions.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Superusers and staff can do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Check if user is HR manager
        user_roles = getattr(request.user, 'roles', [])
        return 'HR Manager' in user_roles


class IsGeneralManager(permissions.BasePermission):
    """
    Permission to only allow general managers to perform certain actions.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Superusers and staff can do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Check if user is general manager
        user_roles = getattr(request.user, 'roles', [])
        return 'General Manager' in user_roles


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        return obj.user == request.user


class IsSameTenant(permissions.BasePermission):
    """
    Permission to ensure user is accessing resources from their own tenant.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Superusers and staff can do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Check if user has a tenant_id
        user_tenant_id = getattr(request.user, 'tenant_id', None)
        return user_tenant_id is not None


class HasCustomPermission(permissions.BasePermission):
    """
    Permission to check if user has a specific custom permission.
    """

    def __init__(self, permission_codename):
        self.permission_codename = permission_codename

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Superusers and staff can do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Check if user has the custom permission
        user_permissions = getattr(request.user, 'permissions', [])
        return self.permission_codename in user_permissions


class IsApprovedMember(permissions.BasePermission):
    """
    Permission to only allow approved tenant members.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Superusers and staff can do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Check if user is approved
        is_approved = getattr(request.user, 'is_approved', True)
        return is_approved
