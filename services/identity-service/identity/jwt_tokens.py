"""
Custom JWT Token Configuration for Identity Service

Enhanced JWT tokens to include user roles, tenant info, and permissions.
"""

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings


class CustomRefreshToken(RefreshToken):
    """
    Custom refresh token that includes additional user context.
    """

    @classmethod
    def for_user(cls, user):
        """
        Create a refresh token for a user with extended claims.
        """
        token = super().for_user(user)

        # Add custom claims to the token
        user_tenant = getattr(user, 'usertenant', None)

        # Add user roles and tenant info to token
        if user_tenant:
            token['role'] = user_tenant.role
            token['is_owner'] = user_tenant.is_owner
            token['is_approved'] = user_tenant.is_approved
            token['tenant_id'] = str(user_tenant.tenant.id) if user_tenant.tenant else None
            token['department_id'] = str(user_tenant.department.id) if user_tenant.department else None
        else:
            token['role'] = 'Employee'
            token['is_owner'] = False
            token['is_approved'] = True
            token['tenant_id'] = None
            token['department_id'] = None

        # Add user basic info
        token['user_id'] = str(user.id)
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['full_name'] = f"{user.first_name} {user.last_name}".strip()
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser

        return token
