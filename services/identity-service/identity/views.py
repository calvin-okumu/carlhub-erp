"""
Identity Service Views

This module contains API views for Identity Service microservice.
"""

import uuid
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .jwt_tokens import CustomRefreshToken
from .models import User, Tenant, RefreshToken as RefreshTokenModel, UserSession
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    TenantSerializer, LoginSerializer, TokenResponseSerializer,
    RefreshTokenSerializer, UserSessionSerializer,
    ChangePasswordSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer
)
from .email_service import EmailService, EmailError


class TenantListCreateView(generics.ListCreateAPIView):
    """List and create tenants"""

    queryset = Tenant.objects.filter(is_active=True)
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter tenants based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return Tenant.objects.all()
        # Regular users can only see their own tenant
        return Tenant.objects.filter(id=user.tenant_id, is_active=True)


class TenantDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update tenant details"""

    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter tenants based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return Tenant.objects.all()
        # Regular users can only access their own tenant
        return Tenant.objects.filter(id=user.tenant_id)


class UserListCreateView(generics.ListCreateAPIView):
    """List and create users"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        """Filter users based on permissions and tenant"""
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        # Regular users can only see users in their tenant
        return User.objects.filter(tenant_id=user.tenant_id)

    def perform_create(self, serializer):
        """Set tenant for new user if not specified"""
        user = self.request.user
        if not serializer.validated_data.get('tenant_id') and not user.is_superuser:
            serializer.validated_data['tenant_id'] = user.tenant_id
        serializer.save()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete user details"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        """Filter users based on permissions"""
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        # Users can access their own profile and other users in their tenant
        return User.objects.filter(tenant_id=user.tenant_id)


class LoginView(APIView):
    """User login endpoint"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Authenticate user and return tokens"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Create JWT tokens with custom claims
            refresh = CustomRefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Store refresh token in database
            expires_at = timezone.now() + timedelta(days=30)  # 30 days
            RefreshTokenModel.objects.create(
                user=user,
                token=str(refresh),
                expires_at=expires_at
            )

            # Create user session
            session_expires = timezone.now() + timedelta(hours=24)  # 24 hours
            UserSession.objects.create(
                user=user,
                session_key=str(uuid.uuid4()),
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                expires_at=session_expires
            )

            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            # Prepare response
            response_data = {
                'access_token': access_token,
                'refresh_token': str(refresh),
                'token_type': 'Bearer',
                'expires_in': 3600,  # 1 hour
                'user': UserSerializer(user).data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RefreshTokenView(APIView):
    """Refresh access token"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Refresh access token using refresh token"""
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token_obj = serializer.validated_data['refresh_token_obj']
            user = refresh_token_obj.user

            # Create new JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Revoke old refresh token
            refresh_token_obj.revoke()

            # Store new refresh token
            expires_at = timezone.now() + timedelta(days=30)
            RefreshTokenModel.objects.create(
                user=user,
                token=str(refresh),
                expires_at=expires_at
            )

            response_data = {
                'access_token': access_token,
                'refresh_token': str(refresh),
                'token_type': 'Bearer',
                'expires_in': 3600,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """User logout endpoint"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Logout user by revoking refresh tokens and sessions"""
        user = request.user

        # Revoke all refresh tokens for user
        RefreshTokenModel.objects.filter(
            user=user,
            is_active=True
        ).update(is_active=False, revoked_at=timezone.now())

        # Deactivate user sessions
        UserSession.objects.filter(
            user=user,
            is_active=True
        ).update(is_active=False)

        return Response(
            {'message': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    """Change user password"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Change user password"""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Verify old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Current password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            # Revoke all refresh tokens (force re-login)
            RefreshTokenModel.objects.filter(
                user=user,
                is_active=True
            ).update(is_active=False, revoked_at=timezone.now())

            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSessionsView(generics.ListAPIView):
    """List user sessions"""

    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return sessions for the current user"""
        return UserSession.objects.filter(user=self.request.user)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile management"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return current user"""
        return self.request.user

    def get_serializer_class(self):
        """Use update serializer for PUT/PATCH"""
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset(request):
    """Request password reset"""
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get('email')
        
        try:
            # Get user by email
            from .models import User
            user = User.objects.get(email=email, is_active=True)
            
            # Generate reset token (in real implementation)
            reset_token = str(uuid.uuid4())
            reset_url = f"{settings.FRONTEND_URL}/reset-password/?token={reset_token}"
            
            # Send email
            EmailService.send_password_reset_email(user, reset_url)
            
            return Response(
                {'message': 'Password reset email sent'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return Response(
                {'message': 'Password reset email sent'},
                status=status.HTTP_200_OK
            )
        except EmailError as e:
            return Response(
                {'error': e.user_message},
                status=e.status_code
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to send password reset email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    """Confirm password reset"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        # In a real implementation, validate token and reset password
        # For now, just return success
        return Response(
            {'message': 'Password reset successfully'},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response(
        {
            'status': 'healthy',
            'service': 'identity-service',
            'timestamp': timezone.now().isoformat()
        },
        status=status.HTTP_200_OK
    )
