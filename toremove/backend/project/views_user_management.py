"""
User Management Views for DjangoCRM

This module contains ViewSets for user management entities:
- UserTenant Management
- Invitation Management
- User Management

These ViewSets handle user onboarding, tenant membership,
and user administration with proper security controls.
"""

import logging

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from accounts.audit import AuditLogger
from accounts.email_service import EmailError, EmailService
from accounts.models import CustomUser, Invitation, UserTenant
from saasCRM.query_optimization import OptimizedTenantScopedMixin, OptimizedViewSetMixin

from .permissions import IsTenantOwner
from .serializers import (
    CustomUserSerializer,
    InvitationSerializer,
    UserTenantSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        summary="List user-tenant relationships",
        description="Retrieve a list of user-tenant relationships for current tenant.",
    ),
    retrieve=extend_schema(
        summary="Retrieve user-tenant relationship",
        description="Retrieve details of a specific user-tenant relationship.",
    ),
    create=extend_schema(
        summary="Create user-tenant relationship", description="Add a user to a tenant."
    ),
    update=extend_schema(
        summary="Update user-tenant relationship",
        description="Update user's role and permissions in tenant.",
    ),
    partial_update=extend_schema(
        summary="Partially update user-tenant relationship",
        description="Partially update user's role and permissions.",
    ),
    destroy=extend_schema(
        summary="Remove user from tenant", description="Remove a user from a tenant."
    ),
)
class UserTenantViewSet(OptimizedTenantScopedMixin, OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing user-tenant relationships.

    Provides CRUD operations for managing which users belong to which tenants,
    their roles, and permissions within each tenant.
    """

    queryset = UserTenant.objects.all()
    serializer_class = UserTenantSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_owner", "is_approved", "role"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    ordering_fields = ["created_at", "user__email", "role"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("user", "tenant")
        return queryset

    def perform_create(self, serializer):
        # Determine the tenant
        if hasattr(self.request, "tenant") and self.request.tenant:
            tenant = self.request.tenant
        else:
            # Development/Test mode: try to get tenant from user or create default
            try:
                user_tenant = UserTenant.objects.filter(
                    user=self.request.user, is_owner=True
                ).first()
                if user_tenant:
                    tenant = user_tenant.tenant
                else:
                    # Create a default tenant for testing
                    from accounts.models import Tenant

                    tenant, created = Tenant.objects.get_or_create(
                        name="Default Test Tenant", defaults={"domain": "test.com"}
                    )
            except Exception:
                # Fallback for any issues
                from accounts.models import Tenant

                tenant, created = Tenant.objects.get_or_create(
                    name="Default Test Tenant", defaults={"domain": "test.com"}
                )
                tenant = tenant

        serializer.save(tenant=tenant)

    @action(detail=True, methods=["post"])
    def approve_member(self, request, slug=None):
        """
        Approve a pending tenant member.
        Only tenant owners can approve members.
        """
        user_tenant = self.get_object()

        if user_tenant.is_approved:
            return Response(
                {"error": "Member is already approved"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_tenant.is_approved = True
        user_tenant.save(update_fields=["is_approved"])

        # Send approval email
        try:
            EmailService.send_member_approval_email(
                user_tenant.user.email, user_tenant.tenant.name, user_tenant.role
            )
        except EmailError as e:
            logger.error(f"Failed to send approval email: {e}")

        # Log the action
        AuditLogger.log(
            user=request.user,
            action="approve_member",
            resource_type="user_tenant",
            resource_id=str(user_tenant.id),
            details=f"Approved {user_tenant.user.email} as {user_tenant.role}",
        )

        return Response(
            {
                "message": "Member approved successfully",
                "user_tenant": self.get_serializer(user_tenant).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def remove_member(self, request, slug=None):
        """
        Remove a member from the tenant.
        Only tenant owners can remove members.
        """
        user_tenant = self.get_object()

        # Prevent removing the last owner
        if user_tenant.is_owner:
            owner_count = UserTenant.objects.filter(
                tenant=user_tenant.tenant, is_owner=True
            ).count()

            if owner_count <= 1:
                return Response(
                    {"error": "Cannot remove the last owner from the tenant"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        user_email = user_tenant.user.email
        tenant_name = user_tenant.tenant.name

        # Delete the user-tenant relationship
        user_tenant.delete()

        # Send removal email
        try:
            EmailService.send_member_removal_email(user_email, tenant_name)
        except EmailError as e:
            logger.error(f"Failed to send removal email: {e}")

        # Log the action
        AuditLogger.log(
            user=request.user,
            action="remove_member",
            resource_type="user_tenant",
            resource_id=str(user_tenant.id),
            details=f"Removed {user_email} from {tenant_name}",
        )

        return Response(
            {"message": f"Member {user_email} removed successfully"}, status=status.HTTP_200_OK
        )


@extend_schema_view(
    list=extend_schema(
        summary="List invitations", description="Retrieve a list of invitations for current tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve invitation", description="Retrieve details of a specific invitation."
    ),
    create=extend_schema(
        summary="Create invitation", description="Create a new invitation to join the tenant."
    ),
    update=extend_schema(summary="Update invitation", description="Update an existing invitation."),
    partial_update=extend_schema(
        summary="Partially update invitation", description="Partially update an invitation."
    ),
    destroy=extend_schema(summary="Delete invitation", description="Delete an invitation."),
)
class InvitationViewSet(OptimizedTenantScopedMixin, OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing tenant invitations.

    Provides CRUD operations for inviting users to join tenants.
    Includes invitation status tracking and email delivery.
    """

    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["role"]
    search_fields = ["email", "invited_by__email"]
    ordering_fields = ["created_at", "email"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("invited_by", "tenant")
        return queryset

    def perform_create(self, serializer):
        # Determine the tenant
        if hasattr(self.request, "tenant") and self.request.tenant:
            tenant = self.request.tenant
        else:
            # Development/Test mode: try to get tenant from user or create default
            try:
                user_tenant = UserTenant.objects.filter(
                    user=self.request.user, is_owner=True
                ).first()
                if user_tenant:
                    tenant = user_tenant.tenant
                else:
                    # Create a default tenant for testing
                    from accounts.models import Tenant

                    tenant, created = Tenant.objects.get_or_create(
                        name="Default Test Tenant", defaults={"domain": "test.com"}
                    )
            except Exception:
                # Fallback for any issues
                from accounts.models import Tenant

                tenant, created = Tenant.objects.get_or_create(
                    name="Default Test Tenant", defaults={"domain": "test.com"}
                )
                tenant = tenant

        invitation = serializer.save(tenant=tenant, invited_by=self.request.user)

        # Send invitation email
        try:
            EmailService.send_invitation_email(
                invitation.email,
                invitation.tenant.name,
                invitation.role,
                invitation.invitation_token,
            )
        except EmailError as e:
            logger.error(f"Failed to send invitation email: {e}")
            invitation.status = "failed"
            invitation.save(update_fields=["status"])

    @action(detail=True, methods=["post"])
    def resend_invitation(self, request, slug=None):
        """
        Resend an invitation email.
        """
        invitation = self.get_object()

        if invitation.status != "pending":
            return Response(
                {"error": "Only pending invitations can be resent"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate new token
        invitation.invitation_token = invitation.generate_invitation_token()
        invitation.save(update_fields=["invitation_token"])

        # Resend email
        try:
            EmailService.send_invitation_email(
                invitation.email,
                invitation.tenant.name,
                invitation.role,
                invitation.invitation_token,
            )

            return Response(
                {"message": "Invitation resent successfully"}, status=status.HTTP_200_OK
            )

        except EmailError as e:
            logger.error(f"Failed to resend invitation email: {e}")
            return Response(
                {"error": "Failed to resend invitation email"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def cancel_invitation(self, request, slug=None):
        """
        Cancel a pending invitation.
        """
        invitation = self.get_object()

        if invitation.status != "pending":
            return Response(
                {"error": "Only pending invitations can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = "cancelled"
        invitation.save(update_fields=["status"])

        # Log the action
        AuditLogger.log(
            user=request.user,
            action="cancel_invitation",
            resource_type="invitation",
            resource_id=str(invitation.id),
            details=f"Cancelled invitation for {invitation.email}",
        )

        return Response({"message": "Invitation cancelled successfully"}, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(summary="List users", description="Retrieve a list of users in the system."),
    retrieve=extend_schema(
        summary="Retrieve user", description="Retrieve details of a specific user."
    ),
    create=extend_schema(summary="Create user", description="Create a new user account."),
    update=extend_schema(
        summary="Update user", description="Update an existing user's information."
    ),
    partial_update=extend_schema(
        summary="Partially update user", description="Partially update a user's information."
    ),
    destroy=extend_schema(summary="Delete user", description="Delete a user account."),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts.

    Provides CRUD operations for user management.
    Includes user search and filtering capabilities.
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["email", "created_at", "last_login"]
    ordering = ["email"]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Non-superusers can only see users from their tenants
        if not self.request.user.is_superuser:
            user_tenants = UserTenant.objects.filter(user=self.request.user).values_list(
                "tenant", flat=True
            )

            # Get users from the same tenants
            queryset = queryset.filter(usertenant__tenant__in=user_tenants).distinct()

        return queryset

    @action(detail=True, methods=["post"])
    def assign_admin(self, request, slug=None):
        """
        Assign admin privileges to a user.
        Only superusers can assign admin privileges.
        """
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superusers can assign admin privileges"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = self.get_object()

        if user.is_staff:
            return Response(
                {"error": "User is already an admin"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.is_staff = True
        user.save(update_fields=["is_staff"])

        # Log the action
        AuditLogger.log(
            user=request.user,
            action="assign_admin",
            resource_type="user",
            resource_id=str(user.id),
            details=f"Assigned admin privileges to {user.email}",
        )

        return Response(
            {"message": f"Admin privileges assigned to {user.email} successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def remove_admin(self, request, slug=None):
        """
        Remove admin privileges from a user.
        Only superusers can remove admin privileges.
        """
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superusers can remove admin privileges"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = self.get_object()

        if not user.is_staff:
            return Response({"error": "User is not an admin"}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent removing superuser status from the last superuser
        if user.is_superuser:
            superuser_count = CustomUser.objects.filter(is_superuser=True).count()
            if superuser_count <= 1:
                return Response(
                    {"error": "Cannot remove superuser privileges from the last superuser"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        user.is_staff = False
        user.save(update_fields=["is_staff"])

        # Log the action
        AuditLogger.log(
            user=request.user,
            action="remove_admin",
            resource_type="user",
            resource_id=str(user.id),
            details=f"Removed admin privileges from {user.email}",
        )

        return Response(
            {"message": f"Admin privileges removed from {user.email} successfully"},
            status=status.HTTP_200_OK,
        )
