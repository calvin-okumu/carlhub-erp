"""
Notification Service Event Publishers

This module contains event publishers for Notification Service.
Events are published when notifications are created/sent.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.event_bus import event_bus, BaseEvent

logger = logging.getLogger(__name__)


class NotificationCreatedEvent(BaseEvent):
    """Event published when a new notification is created"""
    event_type: str = "notification.created"
    source_service: str = "notification"


class NotificationSentEvent(BaseEvent):
    """Event published when a notification is sent"""
    event_type: str = "notification.sent"
    source_service: str = "notification"


class NotificationReadEvent(BaseEvent):
    """Event published when a notification is read"""
    event_type: str = "notification.read"
    source_service: str = "notification"


class NotificationEventPublisher:
    """Publisher for notification-related events"""

    @staticmethod
    def publish_notification_created(notification):
        """Publish notification created event"""
        try:
            event = NotificationCreatedEvent(
                data={
                    'notification_id': str(notification.id),
                    'title': notification.title,
                    'content': notification.content,
                    'notification_type': notification.notification_type,
                    'recipient_id': str(notification.recipient_id) if notification.recipient_id else None,
                    'tenant_id': str(notification.tenant_id) if notification.tenant_id else None,
                    'status': notification.status,
                    'created_at': notification.created_at.isoformat() if notification.created_at else None,
                },
                correlation_id=f"notification-{notification.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published notification.created event for {notification.title}")
        except Exception as e:
            logger.error(f"Failed to publish notification.created event: {e}")

    @staticmethod
    def publish_notification_sent(notification):
        """Publish notification sent event"""
        try:
            event = NotificationSentEvent(
                data={
                    'notification_id': str(notification.id),
                    'title': notification.title,
                    'sent_at': notification.sent_at.isoformat() if notification.sent_at else None,
                    'tenant_id': str(notification.tenant_id) if notification.tenant_id else None,
                },
                correlation_id=f"notification-{notification.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published notification.sent event for {notification.title}")
        except Exception as e:
            logger.error(f"Failed to publish notification.sent event: {e}")

    @staticmethod
    def publish_notification_read(notification):
        """Publish notification read event"""
        try:
            event = NotificationReadEvent(
                data={
                    'notification_id': str(notification.id),
                    'read_at': notification.read_at.isoformat() if notification.read_at else None,
                    'tenant_id': str(notification.tenant_id) if notification.tenant_id else None,
                },
                correlation_id=f"notification-{notification.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published notification.read event for {notification.title}")
        except Exception as e:
            logger.error(f"Failed to publish notification.read event: {e}")


# Django signal handlers for automatic event publishing

@receiver(post_save, sender=Notification)
def handle_notification_save(sender, instance, created, **kwargs):
    """Handle notification save events"""
    if created:
        NotificationEventPublisher.publish_notification_created(instance)


# Note: You might want to add handlers for other notification state changes
# like when notifications are sent or read
