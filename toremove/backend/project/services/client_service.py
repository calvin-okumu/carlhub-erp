from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.models import UserTenant

from ..models import Client


class ClientService:
    """Service layer for Client business logic"""

    @staticmethod
    def get_clients_for_user(
        user_tenant: UserTenant,
        search: str | None = None,
        ordering: str | None = None,
        status: str | None = None,
    ) -> list[Client]:
        """
        Get clients for a specific user tenant with optional filtering
        """
        queryset = Client.objects.filter(tenant=user_tenant.tenant)

        if search:
            queryset = queryset.filter(name__icontains=search)

        if status:
            queryset = queryset.filter(status=status)

        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    @staticmethod
    def get_client_by_slug(user_tenant: UserTenant, slug: str) -> Client | None:
        """
        Get a specific client by slug for the user's tenant
        """
        try:
            return Client.objects.get(tenant=user_tenant.tenant, slug=slug)
        except Client.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_client(user_tenant: UserTenant, client_data: dict[str, Any]) -> Client:
        """
        Create a new client for the tenant
        """
        # Add tenant to client data
        client_data["tenant"] = user_tenant.tenant

        # Validate unique client name per tenant
        if Client.objects.filter(tenant=user_tenant.tenant, name=client_data["name"]).exists():
            raise ValidationError("A client with this name already exists for your organization.")

        client = Client.objects.create(**client_data)
        return client

    @staticmethod
    @transaction.atomic
    def update_client(
        user_tenant: UserTenant, slug: str, update_data: dict[str, Any]
    ) -> Client | None:
        """
        Update an existing client
        """
        client = ClientService.get_client_by_slug(user_tenant, slug)
        if not client:
            return None

        # Check if name is being changed and validate uniqueness
        if "name" in update_data and update_data["name"] != client.name:
            if Client.objects.filter(tenant=user_tenant.tenant, name=update_data["name"]).exists():
                raise ValidationError(
                    "A client with this name already exists for your organization."
                )

        # Update client fields
        for field, value in update_data.items():
            if hasattr(client, field):
                setattr(client, field, value)

        client.updated_at = timezone.now()
        client.save()
        return client

    @staticmethod
    @transaction.atomic
    def delete_client(user_tenant: UserTenant, slug: str) -> bool:
        """
        Soft delete a client
        """
        client = ClientService.get_client_by_slug(user_tenant, slug)
        if not client:
            return False

        # Check if client has associated projects
        if client.projects.exists():
            raise ValidationError(
                "Cannot delete client with associated projects. Please delete the projects first."
            )

        client.delete()
        return True

    @staticmethod
    def get_client_stats(user_tenant: UserTenant) -> dict[str, Any]:
        """
        Get statistics about clients for the tenant
        """
        queryset = Client.objects.filter(tenant=user_tenant.tenant)

        return {
            "total_clients": queryset.count(),
            "active_clients": queryset.filter(status="active").count(),
            "inactive_clients": queryset.filter(status="inactive").count(),
            "recent_clients": queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count(),
        }

    @staticmethod
    def bulk_update_status(user_tenant: UserTenant, client_slugs: list[str], status: str) -> int:
        """
        Bulk update client status
        """
        updated_count = Client.objects.filter(
            tenant=user_tenant.tenant, slug__in=client_slugs
        ).update(status=status, updated_at=timezone.now())

        return updated_count
