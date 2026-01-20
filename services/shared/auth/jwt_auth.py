"""
Simple JWT Authentication for Microservices

This module provides JWT authentication that doesn't require a local User model.
Services validate tokens using the shared SECRET_KEY and extract user data
from the token payload without database lookup.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class SimpleUser:
    """
    Simple user object that mimics Django User without database.
    Used by SimpleJWTAuthentication for JWT-based authentication in microservices.
    """

    is_authenticated = True
    is_anonymous = False

    def __init__(
        self,
        id,
        email,
        first_name='',
        last_name='',
        full_name='',
        is_staff=False,
        is_superuser=False,
        tenant_id=None,
        role='Employee',
        is_owner=False,
        is_approved=True,
        department_id=None,
        token=None,
    ):
        self.id = id  # This will be a UUID string from token
        self.pk = id
        self.email = email
        self.username = email  # Django auth uses username
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = full_name or f"{first_name} {last_name}".strip()
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.tenant_id = tenant_id
        self.role = role
        self.is_owner = is_owner
        self.is_approved = is_approved
        self.department_id = department_id
        self.token = token

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        """Simple permission check based on is_staff"""
        return self.is_staff or self.is_superuser

    def has_module_perms(self, app_label):
        """Simple module permission check"""
        return self.is_staff or self.is_superuser

    def has_perms(self, perm_list, obj=None):
        """Simple permissions list check"""
        return self.is_staff or self.is_superuser


class SimpleJWTAuthentication(JWTAuthentication):
    """JWT authentication without database lookup, supporting UUID user IDs."""

    def get_user(self, validated_token):
        try:
            user_id = validated_token.get('user_id')
            email = validated_token.get('email')
            first_name = validated_token.get('first_name', '')
            last_name = validated_token.get('last_name', '')
            full_name = validated_token.get('full_name', '')
            is_staff = validated_token.get('is_staff', False)
            is_superuser = validated_token.get('is_superuser', False)
            tenant_id = validated_token.get('tenant_id')
            role = validated_token.get('role', 'Employee')
            is_owner = validated_token.get('is_owner', False)
            is_approved = validated_token.get('is_approved', True)
            department_id = validated_token.get('department_id')

            if not user_id or not email:
                raise AuthenticationFailed('Token contained no recognizable user identification')

            return SimpleUser(
                id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                is_staff=is_staff,
                is_superuser=is_superuser,
                tenant_id=tenant_id,
                role=role,
                is_owner=is_owner,
                is_approved=is_approved,
                department_id=department_id,
                token=validated_token,
            )
        except Exception as exc:
            raise AuthenticationFailed(f'Invalid token payload: {exc}')
