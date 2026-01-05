"""
Custom JWT Authentication for Microservices
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class SimpleUser:
    """Simple user object from JWT token without database lookup"""

    is_authenticated = True
    is_anonymous = False

    def __init__(self, id, email, first_name='', last_name='', full_name='',
                 is_staff=False, is_superuser=False, tenant_id=None,
                 role='Employee', is_owner=False, is_approved=True,
                 department_id=None):
        self.id = id
        self.pk = id
        self.email = email
        self.username = email
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

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        return self.is_staff or self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_staff or self.is_superuser

    def has_perms(self, perm_list, obj=None):
        return self.is_staff or self.is_superuser


class SimpleJWTAuthentication(JWTAuthentication):
    """JWT authentication without database lookup, supporting UUID user IDs"""

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
                id=user_id, email=email, first_name=first_name,
                last_name=last_name, full_name=full_name, is_staff=is_staff,
                is_superuser=is_superuser, tenant_id=tenant_id, role=role,
                is_owner=is_owner, is_approved=is_approved,
                department_id=department_id
            )
        except Exception as e:
            raise AuthenticationFailed(f'Invalid token payload: {str(e)}')
