"""
Identity Service Serializers

This module contains serializers for Identity Service API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import (
    User, Tenant, UserSession, RefreshToken,
    UserProfile, UserTenant, Department, Invitation,
    EmployeeDocument,
    CustomPermission, PermissionGroup
)


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model"""

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'domain', 'is_active',
            'address', 'phone', 'website', 'industry', 'company_size',
            'default_currency', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""

    class Meta:
        model = UserProfile
        fields = [
            'user', 'job_title', 'phone', 'linkedin_profile',
            'employee_id', 'employee_number', 'tax_number', 'hire_date',
            'street_address', 'city', 'state_province', 'postal_code', 'country',
            'emergency_contact', 'emergency_phone',
            'medical_aid_provider', 'medical_aid_plan', 'medical_aid_number',
            'medical_conditions', 'allergies', 'medications',
            'bank_name', 'account_number', 'branch_code', 'account_type',
            'routing_number', 'swift_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class SimpleUserSerializer(serializers.ModelSerializer):
    """Minimal user serializer to avoid circular references"""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'full_name']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    full_name = serializers.CharField(read_only=True)
    tenant = TenantSerializer(read_only=True)
    profile = UserProfileSerializer(read_only=True)
    user_tenant = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'last_login', 'slug', 'tenant', 'profile', 'user_tenant'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'full_name',
            'tenant', 'profile', 'user_tenant'
        ]

    def get_user_tenant(self, obj):
        try:
            usertenant = obj.usertenant
            if usertenant:
                return UserTenantSerializer(usertenant).data
            return None
        except:
            return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password',
            'password_confirm'
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("User with this email already exists")

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'is_active']


class UserTenantSerializer(serializers.ModelSerializer):
    """Serializer for UserTenant model"""

    user = SimpleUserSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )

    class Meta:
        model = UserTenant
        fields = [
            'id', 'user', 'tenant', 'is_owner', 'is_approved',
            'role', 'department', 'department_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeDocument model"""

    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = EmployeeDocument
        fields = [
            'id', 'user', 'title', 'description', 'document_file',
            'uploaded_at', 'updated_at', 'file_size', 'file_type'
        ]
        read_only_fields = ['id', 'user', 'uploaded_at', 'file_size', 'file_type']


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""

    tenant = TenantSerializer(read_only=True)
    manager = UserSerializer(read_only=True)
    parent_department_name = serializers.CharField(
        source='parent_department.name',
        read_only=True
    )

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'slug', 'tenant', 'manager',
            'description', 'parent_department', 'parent_department_name',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']


class InvitationSerializer(serializers.ModelSerializer):
    """Serializer for Invitation model"""

    invited_by = UserSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = [
            'id', 'email', 'tenant', 'token', 'role',
            'invited_by', 'created_at', 'expires_at',
            'is_used', 'email_confirmed', 'is_expired'
        ]
        read_only_fields = ['id', 'created_at', 'invited_by']


class CustomPermissionSerializer(serializers.ModelSerializer):
    """Serializer for CustomPermission model"""

    created_by = UserSerializer(read_only=True)

    class Meta:
        model = CustomPermission
        fields = [
            'id', 'slug', 'name', 'codename', 'description',
            'category', 'app_label', 'is_active',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class PermissionGroupSerializer(serializers.ModelSerializer):
    """Serializer for PermissionGroup model"""

    tenant = TenantSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    custom_permissions = CustomPermissionSerializer(many=True, read_only=True)

    class Meta:
        model = PermissionGroup
        fields = [
            'id', 'slug', 'name', 'description', 'is_system_group',
            'tenant', 'created_by', 'custom_permissions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError("User account is disabled")
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials")
        else:
            raise serializers.ValidationError("Must include email and password")

        return data


class TokenResponseSerializer(serializers.Serializer):
    """Serializer for token response"""

    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField(default='Bearer')
    expires_in = serializers.IntegerField()
    user = UserSerializer()


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for token refresh"""

    refresh_token = serializers.CharField()

    def validate(self, data):
        token = data.get('refresh_token')

        try:
            refresh_token_obj = RefreshToken.objects.get(
                token=token,
                is_active=True
            )

            if refresh_token_obj.is_expired:
                raise serializers.ValidationError("Refresh token has expired")

            if refresh_token_obj.is_revoked:
                raise serializers.ValidationError("Refresh token has been revoked")

            data['refresh_token_obj'] = refresh_token_obj

        except RefreshToken.DoesNotExist:
            raise serializers.ValidationError("Invalid refresh token")

        return data


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user sessions"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'session_key', 'ip_address', 'user_agent',
            'created_at', 'expires_at', 'is_active'
        ]
        read_only_fields = ['id', 'session_key', 'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""

    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match")

        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("New password must be different from old password")

        return data


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request"""

    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email')

        try:
            user = User.objects.get(email=email, is_active=True)
            data['user'] = user
        except User.DoesNotExist:
            pass

        return data


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""

    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match")

        return data
