"""
Permission classes for project service.
"""
from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.IsAuthenticated):
    pass


class TenantBasedPermission(permissions.BasePermission):
    """
    Base permission class that ensures tenant isolation.
    All objects must belong to current tenant.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "tenant_id"):
            tenant_id = getattr(request, "tenant_id", None)
            if tenant_id:
                return obj.tenant_id == tenant_id
        return True


class CanManageClients(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "tenant_id"):
            tenant_id = getattr(request, "tenant_id", None)
            if tenant_id:
                return obj.tenant_id == tenant_id
        return True


class CanManageProjects(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "tenant_id"):
            tenant_id = getattr(request, "tenant_id", None)
            if tenant_id:
                return obj.tenant_id == tenant_id
        return True


class CanManageMilestones(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "tenant_id"):
            tenant_id = getattr(request, "tenant_id", None)
            if tenant_id:
                return obj.tenant_id == tenant_id
        return True


class CanManageSprints(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "tenant_id"):
            tenant_id = getattr(request, "tenant_id", None)
            if tenant_id:
                return obj.tenant_id == tenant_id
        return True


class CanManageTasks(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "tenant_id"):
            tenant_id = getattr(request, "tenant_id", None)
            if tenant_id:
                return obj.tenant_id == tenant_id
        return True


class CanManageContracts(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "tenant_id"):
            tenant_id = getattr(request, "tenant_id", None)
            if tenant_id:
                return obj.tenant_id == tenant_id
        return True


class IsTenantOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "tenant_id"):
            tenant_id = getattr(request, "tenant_id", None)
            if tenant_id:
                return obj.tenant_id == tenant_id
        return True


class IsTenantCreator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "tenant_id"):
            tenant_id = getattr(request, "tenant_id", None)
            if tenant_id:
                return obj.tenant_id == tenant_id
        return True
