from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import CustomPermission, PermissionGroup, UserTenant
from .permissions import IsTenantAdmin
from .serializers import CustomPermissionSerializer, PermissionGroupSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="UUID of the permission",
        )
    ]
)
class CustomPermissionViewSet(ModelViewSet):
    """
    CRUD operations for custom permissions
    """

    serializer_class = CustomPermissionSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    lookup_field = "id"

    def get_queryset(self):
        # Only show permissions for current tenant's admin
        user_tenant = get_object_or_404(UserTenant, user=self.request.user, is_approved=True)
        return CustomPermission.objects.filter(
            created_by__usertenant__tenant=user_tenant.tenant
        ).distinct()

    def perform_create(self, serializer):
        user_tenant = get_object_or_404(UserTenant, user=self.request.user, is_approved=True)
        serializer.save(created_by=self.request.user, app_label=f"tenant_{user_tenant.tenant.id}")


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="UUID of permission group",
        )
    ]
)
class PermissionGroupViewSet(ModelViewSet):
    """
    CRUD operations for permission groups
    """

    serializer_class = PermissionGroupSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    lookup_field = "id"

    def get_queryset(self):
        user_tenant = get_object_or_404(UserTenant, user=self.request.user, is_approved=True)
        return PermissionGroup.objects.filter(tenant=user_tenant.tenant)

    def perform_create(self, serializer):
        user_tenant = get_object_or_404(UserTenant, user=self.request.user, is_approved=True)
        serializer.save(tenant=user_tenant.tenant, created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def assign_users(self, request, pk=None):
        """Assign users to this permission group"""
        group = self.get_object()
        user_ids = request.data.get("user_ids", [])

        # Validate users belong to same tenant
        user_tenant = get_object_or_404(UserTenant, user=request.user, is_approved=True)
        valid_users = UserTenant.objects.filter(
            tenant=user_tenant.tenant, user__id__in=user_ids, is_approved=True
        ).values_list("user", flat=True)

        group.users.set(valid_users)
        return Response({"message": f"Assigned {len(valid_users)} users to group"})

    @action(detail=True, methods=["post"])
    def assign_permissions(self, request, pk=None):
        """Assign custom permissions to this group"""
        group = self.get_object()
        permission_ids = request.data.get("permission_ids", [])
        if isinstance(permission_ids, str):
            permission_ids = [permission_ids]
        elif not isinstance(permission_ids, list):
            permission_ids = []

        permissions = CustomPermission.objects.filter(id__in=permission_ids)
        group.custom_permissions.set(permissions)
        return Response({"message": f"Assigned {len(permissions)} permissions to group"})


class UserPermissionViewSet(generics.GenericAPIView):
    """
    View and manage user permissions
    """

    permission_classes = [IsAuthenticated, IsTenantAdmin]
    # Use a simple serializer to satisfy DRF requirements
    serializer_class = CustomPermissionSerializer

    def get(self, request, user_id):
        """Get user's current permissions"""
        user_tenant = get_object_or_404(UserTenant, user=request.user, is_approved=True)
        target_user_tenant = get_object_or_404(
            UserTenant, user__id=user_id, tenant=user_tenant.tenant, is_approved=True
        )

        # Get Django permissions from groups
        django_permissions = set()
        for group in target_user_tenant.user.groups.all():
            django_permissions.update(group.permissions.values_list("codename", flat=True))

        # Get custom permissions from permission groups
        custom_permissions = set()
        for perm_group in target_user_tenant.user.permission_groups.filter(
            tenant=user_tenant.tenant
        ):
            custom_permissions.update(
                perm_group.custom_permissions.values_list("codename", flat=True)
            )

        return Response(
            {
                "user_id": user_id,
                "django_permissions": list(django_permissions),
                "custom_permissions": list(custom_permissions),
                "groups": list(target_user_tenant.user.groups.values("id", "name")),
                "permission_groups": list(
                    target_user_tenant.user.permission_groups.filter(
                        tenant=user_tenant.tenant
                    ).values("id", "name")
                ),
            }
        )

    def post(self, request, user_id):
        """Assign permissions directly to user"""
        user_tenant = get_object_or_404(UserTenant, user=request.user, is_approved=True)
        target_user_tenant = get_object_or_404(
            UserTenant, user__id=user_id, tenant=user_tenant.tenant, is_approved=True
        )

        permission_ids = request.data.get("permission_ids", [])
        permissions = CustomPermission.objects.filter(id__in=permission_ids)

        # Create a personal permission group for this user
        personal_group, created = PermissionGroup.objects.get_or_create(
            name=f"Personal - {target_user_tenant.user.email}",
            tenant=user_tenant.tenant,
            defaults={"created_by": request.user, "is_system_group": True},
        )

        personal_group.custom_permissions.set(permissions)
        personal_group.users.add(target_user_tenant.user)

        return Response({"message": f"Assigned {len(permissions)} permissions to user"})
