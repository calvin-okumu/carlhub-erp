"""
Identity Service Serializers

This module contains serializers for the Identity Service API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, Tenant, UserSession, RefreshToken


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model"""

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'domain', 'is_active',
            'address', 'phone', 'website', 'industry', 'company_size',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    full_name = serializers.CharField(read_only=True)
    tenant = TenantSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'last_login', 'tenant_id', 'tenant'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'full_name', 'tenant']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password', 'password_confirm', 'tenant_id'
        ]

    def validate(self, data):
        """Validate user creation data"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")

        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("User with this email already exists")

        return data

    def create(self, validated_data):
        """Create a new user"""
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
        fields = ['first_name', 'last_name', 'is_active', 'tenant_id']


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """Validate login credentials"""
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
        """Validate refresh token"""
        token = data.get('refresh_token')

        try:
            refresh_token = RefreshToken.objects.get(
                token=token,
                is_active=True
            )

            if refresh_token.is_expired:
                raise serializers.ValidationError("Refresh token has expired")

            if refresh_token.is_revoked:
                raise serializers.ValidationError("Refresh token has been revoked")

            data['refresh_token_obj'] = refresh_token

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
        """Validate password change data"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match")

        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("New password must be different from old password")

        return data


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request"""

    email = serializers.EmailField()

    def validate(self, data):
        """Validate password reset request"""
        email = data.get('email')

        try:
            user = User.objects.get(email=email, is_active=True)
            data['user'] = user
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            pass

        return data


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""

    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()

    def validate(self, data):
        """Validate password reset confirmation"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match")

        # Token validation would be handled in the view
        return data