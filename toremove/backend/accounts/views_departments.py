"""
Views for department management.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import Department, UserTenant
from accounts.permissions_departments import CanManageDepartments
from saasCRM.pagination import CustomPageNumberPagination

from .serializers_departments import DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing departments.

    Tenant Owners/Admins can:
    - Create, view, update, delete departments

    Department Managers can:
    - View departments
    - Create sub-departments
    - Update their own department

    Employees can:
    - View departments only
    """

    serializer_class = DepartmentSerializer
    permission_classes = [CanManageDepartments]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tenant", "is_active", "parent_department"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    lookup_field = "slug"

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        queryset = Department.objects.select_related("tenant", "manager", "parent_department")

        # Handle schema generation (no authenticated user)
        if not user or user.is_anonymous:
            return queryset.none()

        # Superusers see all
        if user.is_superuser:
            return queryset

        # Get user's tenant context
        try:
            user_tenant = user.usertenant
            if not user_tenant.is_approved:
                return queryset.none()

            # Filter by tenant
            queryset = queryset.filter(tenant=user_tenant.tenant)

            # Tenant owners and admins see all departments
            if user_tenant.role in ["Tenant Owner", "General Manager", "HR Manager"]:
                return queryset

            # Department managers see their department and sub-departments
            if user_tenant.role == "Department Manager":
                user_dept = user_tenant.department
                if user_dept:
                    # Get department and all its descendants
                    dept_ids = [user_dept.id]
                    self._get_child_departments(user_dept, dept_ids)
                    return queryset.filter(id__in=dept_ids)
                else:
                    return queryset.none()

            # Employees see only active departments
            return queryset.filter(is_active=True)

        except Exception:
            return queryset.none()

    def _get_child_departments(self, department, dept_ids):
        """Recursively get all child department IDs."""
        children = Department.objects.filter(parent_department=department, is_active=True)
        for child in children:
            dept_ids.append(child.id)
            self._get_child_departments(child, dept_ids)

    def perform_create(self, serializer):
        """Set tenant and validate manager assignment."""
        user = self.request.user

        # Get tenant from user context
        try:
            user_tenant = user.usertenant
            if user_tenant.is_approved:
                serializer.save(tenant=user_tenant.tenant)
            else:
                from rest_framework.exceptions import ValidationError

                raise ValidationError("Your tenant membership is not approved.")
        except Exception:
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Unable to determine tenant context.") from None

    @action(detail=True, methods=["get"])
    def employees(self, request, slug=None):
        """Get all employees in this department (including sub-departments)."""
        department = self.get_object()

        # Get all department IDs (this department + children)
        dept_ids = [department.id]
        self._get_child_departments(department, dept_ids)

        # Get all users in these departments
        employees = UserTenant.objects.filter(
            department_id__in=dept_ids, is_approved=True
        ).select_related("user", "department")

        employee_data = []
        for emp in employees:
            employee_data.append(
                {
                    "id": emp.user.id,
                    "full_name": emp.user.get_full_name(),
                    "email": emp.user.email,
                    "role": emp.role,
                    "department": emp.department.name if emp.department else None,
                    "is_active": emp.user.is_active,
                }
            )

        return Response(
            {
                "department": department.name,
                "total_employees": len(employee_data),
                "employees": employee_data,
            }
        )

    @action(detail=True, methods=["post"])
    def assign_manager(self, request, slug=None):
        """Assign a new manager to this department."""
        department = self.get_object()

        # Check permissions
        if not self._can_manage_department(request.user, department):
            return Response(
                {"error": "You do not have permission to manage this department."},
                status=status.HTTP_403_FORBIDDEN,
            )

        new_manager_id = request.data.get("manager_id")
        if not new_manager_id:
            return Response(
                {"error": "manager_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from accounts.models import CustomUser

            new_manager = CustomUser.objects.get(id=new_manager_id)

            # Update department manager
            old_manager = department.manager
            department.manager = new_manager
            department.save()

            # Update user tenant role if needed
            try:
                manager_ut = UserTenant.objects.get(user=new_manager, tenant=department.tenant)
                if manager_ut.role != "Department Manager":
                    manager_ut.role = "Department Manager"
                    manager_ut.department = department
                    manager_ut.save()
            except UserTenant.DoesNotExist:
                pass

            response_data = {
                "message": "Manager updated successfully.",
                "old_manager": old_manager.get_full_name() if old_manager else None,
                "new_manager": new_manager.get_full_name(),
            }

            return Response(response_data)

        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    def _can_manage_department(self, user, department):
        """Check if user can manage the department."""
        if user.is_superuser:
            return True

        try:
            user_tenant = user.usertenant

            # Tenant owners and general managers can manage any department
            if user_tenant.role in ["Tenant Owner", "General Manager", "HR Manager"]:
                return user_tenant.tenant == department.tenant

            # Department managers can manage their own department and parent departments
            if user_tenant.role == "Department Manager":
                user_dept = user_tenant.department
                if user_dept:
                    # Can manage own department
                    if user_dept == department:
                        return True
                    # Can manage parent department
                    if self._is_parent_department(department, user_dept):
                        return True

            return False
        except Exception:
            return False

    def _is_parent_department(self, potential_parent, child):
        """Check if potential_parent is a parent of child."""
        current = child.parent_department
        while current:
            if current == potential_parent:
                return True
            current = current.parent_department
        return False
