from rest_framework import serializers
from .models import AuditLog, UserProfile, EmployeeDocument, CustomUser

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']

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