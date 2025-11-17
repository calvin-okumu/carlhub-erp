from rest_framework import serializers
from .models import AuditLog, UserProfile, EmployeeDocument, CustomUser, CustomPermission, PermissionGroup

class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'first_name', 'last_name', 'job_title', 'phone', 'linkedin_profile',
            'employee_id', 'employee_number', 'tax_number', 'hire_date',
            'street_address', 'city', 'state_province', 'postal_code', 'country',
            'emergency_contact', 'emergency_phone', 'medical_aid_provider',
            'medical_aid_plan', 'medical_aid_number', 'medical_conditions',
            'allergies', 'medications', 'bank_name', 'account_number',
            'branch_code', 'account_type', 'routing_number', 'swift_code',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = '__all__'
        read_only_fields = ['user', 'uploaded_at', 'file_size', 'file_type']

# Update existing User serializer to include profile
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active',
                 'date_joined', 'profile']


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'action', 'resource_type', 'resource_id',
            'old_values', 'new_values', 'ip_address', 'user_agent',
            'timestamp', 'metadata', 'user_email', 'tenant_name'
        ]
        read_only_fields = ['id', 'timestamp']


class CustomPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = [
            'id', 'slug', 'name', 'codename', 'description',
            'category', 'app_label', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class PermissionGroupSerializer(serializers.ModelSerializer):
    custom_permissions = CustomPermissionSerializer(many=True, read_only=True)

    class Meta:
        model = PermissionGroup
        fields = [
            'id', 'slug', 'name', 'description', 'is_system_group',
            'custom_permissions'
        ]
        read_only_fields = ['id', 'slug']
