"""
Shared tenant scoping helpers for microservices.
"""

from rest_framework import viewsets
from rest_framework.exceptions import ValidationError


def get_scoped_queryset(request, queryset):
    user = getattr(request, "user", None)
    if user and (getattr(user, "is_superuser", False) or getattr(user, "is_staff", False)):
        return queryset

    tenant_id = getattr(request, "tenant_id", None) or getattr(user, "tenant_id", None)
    if tenant_id:
        return queryset.filter(tenant_id=tenant_id)

    return queryset.none()


def get_tenant_id_for_write(request):
    user = getattr(request, "user", None)
    if user and (getattr(user, "is_superuser", False) or getattr(user, "is_staff", False)):
        return None

    tenant_id = getattr(request, "tenant_id", None) or getattr(user, "tenant_id", None)
    if not tenant_id:
        raise ValidationError({"tenant_id": "Tenant context is required."})
    return tenant_id


class TenantScopedModelViewSet(viewsets.ModelViewSet):
    set_tenant_on_create = True

    def get_queryset(self):
        return get_scoped_queryset(self.request, super().get_queryset())

    def perform_create(self, serializer):
        if not self.set_tenant_on_create:
            serializer.save()
            return

        tenant_id = get_tenant_id_for_write(self.request)
        if tenant_id:
            serializer.save(tenant_id=tenant_id)
            return
        serializer.save()
