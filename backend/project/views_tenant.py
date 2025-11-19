"""
Tenant management views for the project app.

This module contains the TenantViewSet for managing tenant organizations
with proper filtering, searching, and ordering capabilities.
"""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from accounts.models import Tenant
from saasCRM.query_optimization import OptimizedViewSetMixin

from .permissions import IsTenantCreator
from .serializers import TenantSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List tenants", description="Retrieve a list of tenant organizations."
    ),
    retrieve=extend_schema(
        summary="Retrieve tenant", description="Retrieve details of a specific tenant."
    ),
    create=extend_schema(summary="Create tenant", description="Create a new tenant organization."),
    update=extend_schema(
        summary="Update tenant", description="Update an existing tenant's information."
    ),
    partial_update=extend_schema(
        summary="Partially update tenant", description="Partially update a tenant's information."
    ),
    destroy=extend_schema(summary="Delete tenant", description="Delete a tenant."),
)
class TenantViewSet(OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing tenant organizations.

    Provides CRUD operations for tenants with filtering, searching, and ordering capabilities.
    """

    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantCreator]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    lookup_field = "slug"

    def perform_create(self, serializer):
        # Determine the tenant
        if hasattr(self.request, "tenant") and self.request.tenant:
            tenant = self.request.tenant
        else:
            # Development/Test mode: try to get tenant from user or create default
            from accounts.models import Tenant, UserTenant

            try:
                user_tenant = UserTenant.objects.filter(
                    user=self.request.user, is_owner=True
                ).first()
                if user_tenant:
                    tenant = user_tenant.tenant
                else:
                    # Create a default tenant for testing
                    tenant, created = Tenant.objects.get_or_create(
                        name="Default Test Tenant", defaults={"domain": "test.com"}
                    )
            except Exception:
                # Fallback for any issues
                tenant, created = Tenant.objects.get_or_create(
                    name="Default Test Tenant", defaults={"domain": "test.com"}
                )
                tenant = tenant

        serializer.save(tenant=tenant)
