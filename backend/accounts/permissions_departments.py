"""
Permissions for department management.
"""

from rest_framework import permissions


class CanManageDepartments(permissions.BasePermission):
    """
    Permission to manage departments based on user role.

    Tenant Owners/Admins: Full access
    Department Managers: Can manage their department and sub-departments
    HR Managers: Can view all departments, limited management
    General Managers: Can view all departments, limited management
    Others: Read-only access
    """

    def has_permission(self, request, view):
        """Check if user has permission for the view."""
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers have full access
        if request.user.is_superuser:
            return True

        # Safe methods (GET, HEAD, OPTIONS) are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            user_tenant = request.user.usertenant
            if not user_tenant.is_approved:
                return False

            # Tenant owners and admins can manage departments
            if user_tenant.role in ["Tenant Owner", "General Manager", "HR Manager"]:
                return True

            # Department managers can create departments (sub-departments)
            if user_tenant.role == "Department Manager":
                return view.action == "create"

            return False
        except:
            return False

    def has_object_permission(self, request, view, obj):
        """Check if user has permission for specific department."""
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers have full access
        if request.user.is_superuser:
            return True

        # Safe methods are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            user_tenant = request.user.usertenant
            if not user_tenant.is_approved:
                return False

            # Tenant owners and admins can manage any department
            if user_tenant.role in ["Tenant Owner", "General Manager", "HR Manager"]:
                return user_tenant.tenant == obj.tenant

            # Department managers can manage their own department and parent departments
            if user_tenant.role == "Department Manager":
                user_dept = user_tenant.department
                if user_dept:
                    # Can manage own department
                    if user_dept == obj:
                        return True
                    # Can manage parent department
                    if self._is_parent_department(obj, user_dept):
                        return True

            return False
        except:
            return False

    def _is_parent_department(self, potential_parent, child):
        """Check if potential_parent is a parent of child."""
        current = child.parent_department
        while current:
            if current == potential_parent:
                return True
            current = current.parent_department
        return False
