from rest_framework import serializers

from .models import Department, UserTenant


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model with slug support"""

    manager_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "manager",
            "manager_name",
            "employee_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "created_at",
            "updated_at",
            "employee_count",
            "manager_name",
        ]

    def get_manager_name(self, obj):
        """Get manager's full name"""
        if obj.manager:
            return obj.manager.get_full_name() or obj.manager.email
        return None

    def get_employee_count(self, obj):
        """Get number of employees in this department"""
        return UserTenant.objects.filter(department=obj, is_approved=True).count()

    def validate_manager(self, value):
        """Validate that manager is an active user"""
        if value and not value.is_active:
            raise serializers.ValidationError("Manager must be an active user")
        return value


class DepartmentDetailSerializer(DepartmentSerializer):
    """Detailed serializer for Department with additional information"""

    employees = serializers.SerializerMethodField()

    class Meta(DepartmentSerializer.Meta):
        fields = DepartmentSerializer.Meta.fields + ["employees"]

    def get_employees(self, obj):
        """Get list of employees in this department"""
        user_tenants = UserTenant.objects.filter(department=obj, is_approved=True).select_related(
            "user"
        )
        return [
            {
                "id": ut.user.id,
                "email": ut.user.email,
                "full_name": ut.user.get_full_name(),
                "role": ut.role,
                "is_active": ut.user.is_active,
                "is_approved": ut.is_approved,
            }
            for ut in user_tenants
        ]


class DepartmentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating departments"""

    class Meta:
        model = Department
        fields = ["name", "description", "manager"]

    def validate_name(self, value):
        """Validate department name uniqueness within tenant"""
        tenant = self.context["request"].tenant
        queryset = Department.objects.filter(name=value, tenant=tenant)

        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        if queryset.exists():
            raise serializers.ValidationError(
                "Department with this name already exists in this tenant"
            )

        return value
