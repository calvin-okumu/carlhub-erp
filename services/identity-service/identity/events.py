"""
Identity Service Event Publishers

This module contains event publishers for the Identity Service.
Events are published when users are created, updated, or authenticated.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import user_logged_in, user_logged_out
from .models import User, Tenant
from backend.shared.event_bus import event_bus, BaseEvent

logger = logging.getLogger(__name__)


class UserCreatedEvent(BaseEvent):
    """Event published when a new user is created"""
    event_type: str = "user.created"
    source_service: str = "identity"


class UserUpdatedEvent(BaseEvent):
    """Event published when a user is updated"""
    event_type: str = "user.updated"
    source_service: str = "identity"


class UserDeletedEvent(BaseEvent):
    """Event published when a user is deleted"""
    event_type: str = "user.deleted"
    source_service: str = "identity"


class UserLoggedInEvent(BaseEvent):
    """Event published when a user logs in"""
    event_type: str = "user.logged_in"
    source_service: str = "identity"


class UserLoggedOutEvent(BaseEvent):
    """Event published when a user logs out"""
    event_type: str = "user.logged_out"
    source_service: str = "identity"


class TenantCreatedEvent(BaseEvent):
    """Event published when a new tenant is created"""
    event_type: str = "tenant.created"
    source_service: str = "identity"


class TenantUpdatedEvent(BaseEvent):
    """Event published when a tenant is updated"""
    event_type: str = "tenant.updated"
    source_service: str = "identity"


class IdentityEventPublisher:
    """Publisher for identity-related events"""

    @staticmethod
    def publish_user_created(user: User):
        """Publish user created event"""
        try:
            event = UserCreatedEvent(
                data={
                    'user_id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'tenant_id': str(user.tenant_id) if user.tenant_id else None,
                    'created_at': user.date_joined.isoformat(),
                },
                correlation_id=f"user-{user.id}",
                target_service="audit-service"  # Audit service should log this
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published user.created event for user {user.email}")
        except Exception as e:
            logger.error(f"Failed to publish user.created event: {e}")

    @staticmethod
    def publish_user_updated(user: User, changes: dict = None):
        """Publish user updated event"""
        try:
            event = UserUpdatedEvent(
                data={
                    'user_id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'tenant_id': str(user.tenant_id) if user.tenant_id else None,
                    'changes': changes or {},
                },
                correlation_id=f"user-{user.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published user.updated event for user {user.email}")
        except Exception as e:
            logger.error(f"Failed to publish user.updated event: {e}")

    @staticmethod
    def publish_user_deleted(user: User):
        """Publish user deleted event"""
        try:
            event = UserDeletedEvent(
                data={
                    'user_id': str(user.id),
                    'email': user.email,
                    'tenant_id': str(user.tenant_id) if user.tenant_id else None,
                },
                correlation_id=f"user-{user.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published user.deleted event for user {user.email}")
        except Exception as e:
            logger.error(f"Failed to publish user.deleted event: {e}")

    @staticmethod
    def publish_user_logged_in(user: User, ip_address: str = None, user_agent: str = None):
        """Publish user logged in event"""
        try:
            event = UserLoggedInEvent(
                data={
                    'user_id': str(user.id),
                    'email': user.email,
                    'tenant_id': str(user.tenant_id) if user.tenant_id else None,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'login_time': user.last_login.isoformat() if user.last_login else None,
                },
                correlation_id=f"login-{user.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published user.logged_in event for user {user.email}")
        except Exception as e:
            logger.error(f"Failed to publish user.logged_in event: {e}")

    @staticmethod
    def publish_user_logged_out(user: User):
        """Publish user logged out event"""
        try:
            event = UserLoggedOutEvent(
                data={
                    'user_id': str(user.id),
                    'email': user.email,
                    'tenant_id': str(user.tenant_id) if user.tenant_id else None,
                    'logout_time': user.last_login.isoformat() if user.last_login else None,
                },
                correlation_id=f"logout-{user.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published user.logged_out event for user {user.email}")
        except Exception as e:
            logger.error(f"Failed to publish user.logged_out event: {e}")

    @staticmethod
    def publish_tenant_created(tenant: Tenant):
        """Publish tenant created event"""
        try:
            event = TenantCreatedEvent(
                data={
                    'tenant_id': str(tenant.id),
                    'name': tenant.name,
                    'slug': tenant.slug,
                    'domain': tenant.domain,
                    'industry': tenant.industry,
                    'company_size': tenant.company_size,
                    'created_at': tenant.created_at.isoformat(),
                },
                correlation_id=f"tenant-{tenant.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published tenant.created event for tenant {tenant.name}")
        except Exception as e:
            logger.error(f"Failed to publish tenant.created event: {e}")

    @staticmethod
    def publish_tenant_updated(tenant: Tenant, changes: dict = None):
        """Publish tenant updated event"""
        try:
            event = TenantUpdatedEvent(
                data={
                    'tenant_id': str(tenant.id),
                    'name': tenant.name,
                    'slug': tenant.slug,
                    'domain': tenant.domain,
                    'industry': tenant.industry,
                    'company_size': tenant.company_size,
                    'changes': changes or {},
                },
                correlation_id=f"tenant-{tenant.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published tenant.updated event for tenant {tenant.name}")
        except Exception as e:
            logger.error(f"Failed to publish tenant.updated event: {e}")


# Django signal handlers for automatic event publishing

@receiver(post_save, sender=User)
def handle_user_save(sender, instance, created, **kwargs):
    """Handle user save events"""
    if created:
        IdentityEventPublisher.publish_user_created(instance)
    else:
        # For updates, we could track changes here
        IdentityEventPublisher.publish_user_updated(instance)


@receiver(post_delete, sender=User)
def handle_user_delete(sender, instance, **kwargs):
    """Handle user delete events"""
    IdentityEventPublisher.publish_user_deleted(instance)


@receiver(post_save, sender=Tenant)
def handle_tenant_save(sender, instance, created, **kwargs):
    """Handle tenant save events"""
    if created:
        IdentityEventPublisher.publish_tenant_created(instance)
    else:
        IdentityEventPublisher.publish_tenant_updated(instance)


@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    """Handle user login events"""
    ip_address = getattr(request, 'META', {}).get('REMOTE_ADDR')
    user_agent = getattr(request, 'META', {}).get('HTTP_USER_AGENT')
    IdentityEventPublisher.publish_user_logged_in(user, ip_address, user_agent)


@receiver(user_logged_out)
def handle_user_logout(sender, request, user, **kwargs):
    """Handle user logout events"""
    IdentityEventPublisher.publish_user_logged_out(user)