"""
Custom model managers for accounts app following repository pattern.
Provides abstraction layer for database operations and enforces tenant isolation.
"""

import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .models import (
    AuditLog,
    CustomPermission,
    Invitation,
    PermissionGroup,
    Tenant,
    UserTenant,
)


class TenantManager(models.Manager):
    """Custom manager for Tenant model."""

    def get_by_natural_key(self, name: str):
        return self.get(name=name)

    def create_tenant(self, name: str, domain: str, created_by=None, **kwargs) -> Tenant:
        """Create a new tenant with validation."""
        if self.filter(name=name).exists():
            raise ValidationError(f"Tenant with name '{name}' already exists")

        if self.filter(domain=domain).exists():
            raise ValidationError(f"Tenant with domain '{domain}' already exists")

        tenant = self.model(name=name, domain=domain, created_by=created_by, **kwargs)
        tenant.save()
        return tenant

    def get_by_domain(self, domain: str) -> Tenant | None:
        """Get tenant by domain."""
        try:
            return self.get(domain=domain)
        except self.model.DoesNotExist:
            return None

    def get_active_tenants(self) -> models.QuerySet:
        """Get all active tenants (can be extended with is_active field)."""
        return self.all()

    def search_tenants(self, query: str) -> models.QuerySet:
        """Search tenants by name or domain."""
        return self.filter(models.Q(name__icontains=query) | models.Q(domain__icontains=query))


class UserTenantManager(models.Manager):
    """Custom manager for UserTenant model."""

    def get_by_natural_key(self, user_email: str, tenant_name: str):
        return self.get(user__email=user_email, tenant__name=tenant_name)

    def create_membership(
        self,
        user,
        tenant: Tenant,
        is_owner: bool = False,
        is_approved: bool = True,
        role: str = "Employee",
    ) -> UserTenant:
        """Create a new user-tenant membership."""
        if self.filter(user=user, tenant=tenant).exists():
            raise ValidationError(f"User {user.email} is already a member of {tenant.name}")

        membership = self.model(
            user=user, tenant=tenant, is_owner=is_owner, is_approved=is_approved, role=role
        )
        membership.save()
        return membership

    def get_user_memberships(self, user) -> models.QuerySet:
        """Get all tenant memberships for a user."""
        return self.filter(user=user).select_related("tenant")

    def get_tenant_members(self, tenant: Tenant) -> models.QuerySet:
        """Get all users in a tenant."""
        return self.filter(tenant=tenant).select_related("user")

    def get_tenant_owners(self, tenant: Tenant) -> models.QuerySet:
        """Get all owners of a tenant."""
        return self.filter(tenant=tenant, is_owner=True).select_related("user")

    def get_approved_members(self, tenant: Tenant) -> models.QuerySet:
        """Get all approved members of a tenant."""
        return self.filter(tenant=tenant, is_approved=True).select_related("user")

    def get_pending_members(self, tenant: Tenant) -> models.QuerySet:
        """Get all pending members of a tenant."""
        return self.filter(tenant=tenant, is_approved=False).select_related("user")

    def transfer_ownership(
        self, tenant: Tenant, from_user, to_user
    ) -> tuple[UserTenant, UserTenant]:
        """Transfer ownership from one user to another."""
        return self.model.transfer_ownership(tenant, from_user, to_user)

    def ensure_minimum_owners(self, tenant: Tenant) -> UserTenant | None:
        """Ensure tenant has at least one owner."""
        return self.model.ensure_minimum_owners(tenant)

    def remove_member(self, user, tenant: Tenant) -> bool:
        """Remove a member from a tenant safely."""
        try:
            membership = self.get(user=user, tenant=tenant)

            # Prevent removing the last owner
            if membership.is_owner:
                owner_count = self.filter(tenant=tenant, is_owner=True).count()
                if owner_count <= 1:
                    raise ValidationError("Cannot remove the last owner of a tenant")

            membership.delete()
            return True
        except self.model.DoesNotExist:
            return False


class InvitationManager(models.Manager):
    """Custom manager for Invitation model."""

    def create_invitation(
        self, email: str, tenant: Tenant, invited_by, role: str = "Employee", expires_days: int = 7
    ) -> Invitation:
        """Create a new invitation."""
        if self.filter(email=email, tenant=tenant, is_used=False).exists():
            raise ValidationError(f"Active invitation for {email} already exists")

        # Generate unique token
        token = uuid.uuid4().hex
        while self.filter(token=token).exists():
            token = uuid.uuid4().hex

        invitation = self.model(
            email=email.lower(),
            tenant=tenant,
            token=token,
            role=role,
            invited_by=invited_by,
            expires_at=timezone.now() + timedelta(days=expires_days),
        )
        invitation.save()
        return invitation

    def get_active_invitations(self, tenant: Tenant) -> models.QuerySet:
        """Get all active (unused and not expired) invitations for a tenant."""
        return self.filter(
            tenant=tenant, is_used=False, expires_at__gt=timezone.now()
        ).select_related("invited_by")

    def get_expired_invitations(self, tenant: Tenant) -> models.QuerySet:
        """Get all expired invitations for a tenant."""
        return self.filter(tenant=tenant, is_used=False, expires_at__lte=timezone.now())

    def get_user_invitations(self, email: str) -> models.QuerySet:
        """Get all invitations for an email address."""
        return self.filter(email__iexact=email).select_related("tenant", "invited_by")

    def get_by_token(self, token: str) -> Invitation | None:
        """Get invitation by token."""
        try:
            return self.get(token=token)
        except self.model.DoesNotExist:
            return None

    def mark_as_used(self, invitation: Invitation) -> bool:
        """Mark an invitation as used."""
        try:
            invitation.is_used = True
            invitation.save(update_fields=["is_used"])
            return True
        except Exception:
            return False

    def cancel_invitation(self, invitation: Invitation) -> bool:
        """Cancel an invitation by marking as used."""
        return self.mark_as_used(invitation)

    def cleanup_expired(self, tenant: Tenant = None) -> int:
        """Delete expired invitations. Returns count of deleted invitations."""
        queryset = self.filter(expires_at__lte=timezone.now())
        if tenant:
            queryset = queryset.filter(tenant=tenant)

        count = queryset.count()
        queryset.delete()
        return count


class AuditLogManager(models.Manager):
    """Custom manager for AuditLog model."""

    def log_action(
        self,
        tenant: Tenant = None,
        user=None,
        action: str = "",
        resource_type: str = "",
        resource_id: str = None,
        old_values: dict = None,
        new_values: dict = None,
        ip_address: str = None,
        user_agent: str = None,
        metadata: dict = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        log_entry = self.model(
            tenant=tenant,
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )
        log_entry.save()
        return log_entry

    def get_tenant_logs(self, tenant: Tenant, limit: int = 100) -> models.QuerySet:
        """Get audit logs for a specific tenant."""
        return self.filter(tenant=tenant).select_related("user").order_by("-timestamp")[:limit]

    def get_user_logs(self, user, limit: int = 100) -> models.QuerySet:
        """Get audit logs for a specific user."""
        return self.filter(user=user).select_related("tenant").order_by("-timestamp")[:limit]

    def get_resource_logs(
        self, resource_type: str, resource_id: str, tenant: Tenant = None
    ) -> models.QuerySet:
        """Get audit logs for a specific resource."""
        queryset = self.filter(resource_type=resource_type, resource_id=resource_id)
        if tenant:
            queryset = queryset.filter(tenant=tenant)
        return queryset.select_related("user").order_by("-timestamp")

    def get_security_events(self, tenant: Tenant = None, days: int = 30) -> models.QuerySet:
        """Get security-related audit logs."""
        security_actions = [
            "security_failed_login",
            "security_token_misuse",
            "admin_user_suspended",
            "admin_user_activated",
        ]
        queryset = self.filter(action__in=security_actions)
        if tenant:
            queryset = queryset.filter(tenant=tenant)

        cutoff_date = timezone.now() - timedelta(days=days)
        return queryset.filter(timestamp__gte=cutoff_date).select_related("user", "tenant")

    def search_logs(self, query: str, tenant: Tenant = None) -> models.QuerySet:
        """Search audit logs by various fields."""
        queryset = self.filter(
            models.Q(action__icontains=query)
            | models.Q(resource_type__icontains=query)
            | models.Q(resource_id__icontains=query)
            | models.Q(user__email__icontains=query)
        )
        if tenant:
            queryset = queryset.filter(tenant=tenant)
        return queryset.select_related("user", "tenant").order_by("-timestamp")


class CustomPermissionManager(models.Manager):
    """Custom manager for CustomPermission model."""

    def get_by_natural_key(self, codename: str):
        return self.get(codename=codename)

    def create_permission(
        self,
        name: str,
        codename: str,
        description: str = "",
        category: str = "custom",
        app_label: str = "accounts",
        created_by=None,
    ) -> CustomPermission:
        """Create a new custom permission."""
        if self.filter(codename=codename).exists():
            raise ValidationError(f"Permission with codename '{codename}' already exists")

        if self.filter(name=name).exists():
            raise ValidationError(f"Permission with name '{name}' already exists")

        permission = self.model(
            name=name,
            codename=codename,
            description=description,
            category=category,
            app_label=app_label,
            created_by=created_by,
        )
        permission.save()
        return permission

    def get_by_category(self, category: str) -> models.QuerySet:
        """Get permissions by category."""
        return self.filter(category=category, is_active=True)

    def get_active_permissions(self) -> models.QuerySet:
        """Get all active permissions."""
        return self.filter(is_active=True)

    def search_permissions(self, query: str) -> models.QuerySet:
        """Search permissions by name, codename, or description."""
        return self.filter(
            models.Q(name__icontains=query)
            | models.Q(codename__icontains=query)
            | models.Q(description__icontains=query)
        ).filter(is_active=True)


class PermissionGroupManager(models.Manager):
    """Custom manager for PermissionGroup model."""

    def get_by_natural_key(self, name: str, tenant_name: str):
        return self.get(name=name, tenant__name=tenant_name)

    def create_group(
        self,
        name: str,
        tenant: Tenant,
        description: str = "",
        is_system_group: bool = False,
        created_by=None,
    ) -> PermissionGroup:
        """Create a new permission group."""
        if self.filter(name=name, tenant=tenant).exists():
            raise ValidationError(f"Group '{name}' already exists in tenant '{tenant.name}'")

        group = self.model(
            name=name,
            tenant=tenant,
            description=description,
            is_system_group=is_system_group,
            created_by=created_by,
        )
        group.save()
        return group

    def get_tenant_groups(self, tenant: Tenant) -> models.QuerySet:
        """Get all groups for a tenant."""
        return self.filter(tenant=tenant).prefetch_related("custom_permissions", "users")

    def get_system_groups(self, tenant: Tenant = None) -> models.QuerySet:
        """Get system groups."""
        queryset = self.filter(is_system_group=True)
        if tenant:
            queryset = queryset.filter(tenant=tenant)
        return queryset

    def get_user_groups(self, user, tenant: Tenant = None) -> models.QuerySet:
        """Get groups for a user."""
        queryset = self.filter(users=user)
        if tenant:
            queryset = queryset.filter(tenant=tenant)
        return queryset

    def add_user_to_group(self, user, group: PermissionGroup) -> bool:
        """Add a user to a group."""
        try:
            group.users.add(user)
            return True
        except Exception:
            return False

    def remove_user_from_group(self, user, group: PermissionGroup) -> bool:
        """Remove a user from a group."""
        try:
            group.users.remove(user)
            return True
        except Exception:
            return False

    def search_groups(self, query: str, tenant: Tenant = None) -> models.QuerySet:
        """Search groups by name or description."""
        queryset = self.filter(
            models.Q(name__icontains=query) | models.Q(description__icontains=query)
        )
        if tenant:
            queryset = queryset.filter(tenant=tenant)
        return queryset
