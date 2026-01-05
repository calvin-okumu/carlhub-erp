"""
Sales Service Event Publishers

This module contains event publishers for Sales Service.
Events are published when customers, opportunities, or sales activities are created/updated.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Customer, Opportunity, SalesActivity
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.event_bus import event_bus, BaseEvent

logger = logging.getLogger(__name__)


class CustomerCreatedEvent(BaseEvent):
    """Event published when a new customer is created"""
    event_type: str = "customer.created"
    source_service: str = "sales"


class CustomerUpdatedEvent(BaseEvent):
    """Event published when a customer is updated"""
    event_type: str = "customer.updated"
    source_service: str = "sales"


class CustomerDeletedEvent(BaseEvent):
    """Event published when a customer is deleted"""
    event_type: str = "customer.deleted"
    source_service: str = "sales"


class OpportunityCreatedEvent(BaseEvent):
    """Event published when a new opportunity is created"""
    event_type: str = "opportunity.created"
    source_service: str = "sales"


class OpportunityUpdatedEvent(BaseEvent):
    """Event published when an opportunity is updated"""
    event_type: str = "opportunity.updated"
    source_service: str = "sales"


class OpportunityWonEvent(BaseEvent):
    """Event published when an opportunity is won"""
    event_type: str = "opportunity.won"
    source_service: str = "sales"


class OpportunityLostEvent(BaseEvent):
    """Event published when an opportunity is lost"""
    event_type: str = "opportunity.lost"
    source_service: str = "sales"


class SalesActivityCreatedEvent(BaseEvent):
    """Event published when a sales activity is created"""
    event_type: str = "sales_activity.created"
    source_service: str = "sales"


class SalesEventPublisher:
    """Publisher for sales-related events"""

    @staticmethod
    def publish_customer_created(customer):
        """Publish customer created event"""
        try:
            event = CustomerCreatedEvent(
                data={
                    'customer_id': str(customer.id),
                    'name': customer.name,
                    'email': customer.email,
                    'phone': customer.phone,
                    'company': customer.company,
                    'status': customer.status,
                    'tenant_id': str(customer.tenant_id) if customer.tenant_id else None,
                    'created_at': customer.created_at.isoformat() if customer.created_at else None,
                },
                correlation_id=f"customer-{customer.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published customer.created event for {customer.name}")
        except Exception as e:
            logger.error(f"Failed to publish customer.created event: {e}")

    @staticmethod
    def publish_customer_updated(customer, changes=None):
        """Publish customer updated event"""
        try:
            event = CustomerUpdatedEvent(
                data={
                    'customer_id': str(customer.id),
                    'name': customer.name,
                    'status': customer.status,
                    'tenant_id': str(customer.tenant_id) if customer.tenant_id else None,
                    'changes': changes or {},
                    'updated_at': customer.updated_at.isoformat() if customer.updated_at else None,
                },
                correlation_id=f"customer-{customer.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published customer.updated event for {customer.name}")
        except Exception as e:
            logger.error(f"Failed to publish customer.updated event: {e}")

    @staticmethod
    def publish_customer_deleted(customer):
        """Publish customer deleted event"""
        try:
            event = CustomerDeletedEvent(
                data={
                    'customer_id': str(customer.id),
                    'name': customer.name,
                    'tenant_id': str(customer.tenant_id) if customer.tenant_id else None,
                    'deleted_at': customer.deleted_at.isoformat() if customer.deleted_at else None,
                },
                correlation_id=f"customer-{customer.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published customer.deleted event for {customer.name}")
        except Exception as e:
            logger.error(f"Failed to publish customer.deleted event: {e}")

    @staticmethod
    def publish_opportunity_created(opportunity):
        """Publish opportunity created event"""
        try:
            event = OpportunityCreatedEvent(
                data={
                    'opportunity_id': str(opportunity.id),
                    'title': opportunity.title,
                    'value': str(opportunity.value) if opportunity.value else None,
                    'stage': opportunity.stage,
                    'probability': opportunity.probability,
                    'status': opportunity.status,
                    'customer_id': str(opportunity.customer_id) if opportunity.customer_id else None,
                    'tenant_id': str(opportunity.tenant_id) if opportunity.tenant_id else None,
                    'created_at': opportunity.created_at.isoformat() if opportunity.created_at else None,
                },
                correlation_id=f"opportunity-{opportunity.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published opportunity.created event for {opportunity.title}")
        except Exception as e:
            logger.error(f"Failed to publish opportunity.created event: {e}")

    @staticmethod
    def publish_opportunity_updated(opportunity, changes=None):
        """Publish opportunity updated event"""
        try:
            event = OpportunityUpdatedEvent(
                data={
                    'opportunity_id': str(opportunity.id),
                    'title': opportunity.title,
                    'status': opportunity.status,
                    'stage': opportunity.stage,
                    'changes': changes or {},
                    'tenant_id': str(opportunity.tenant_id) if opportunity.tenant_id else None,
                    'updated_at': opportunity.updated_at.isoformat() if opportunity.updated_at else None,
                },
                correlation_id=f"opportunity-{opportunity.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published opportunity.updated event for {opportunity.title}")
        except Exception as e:
            logger.error(f"Failed to publish opportunity.updated event: {e}")

    @staticmethod
    def publish_opportunity_won(opportunity):
        """Publish opportunity won event"""
        try:
            event = OpportunityWonEvent(
                data={
                    'opportunity_id': str(opportunity.id),
                    'title': opportunity.title,
                    'value': str(opportunity.value) if opportunity.value else None,
                    'tenant_id': str(opportunity.tenant_id) if opportunity.tenant_id else None,
                    'won_at': opportunity.won_at.isoformat() if opportunity.won_at else None,
                },
                correlation_id=f"opportunity-{opportunity.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published opportunity.won event for {opportunity.title}")
        except Exception as e:
            logger.error(f"Failed to publish opportunity.won event: {e}")

    @staticmethod
    def publish_opportunity_lost(opportunity):
        """Publish opportunity lost event"""
        try:
            event = OpportunityLostEvent(
                data={
                    'opportunity_id': str(opportunity.id),
                    'title': opportunity.title,
                    'value': str(opportunity.value) if opportunity.value else None,
                    'tenant_id': str(opportunity.tenant_id) if opportunity.tenant_id else None,
                    'lost_at': opportunity.lost_at.isoformat() if opportunity.lost_at else None,
                },
                correlation_id=f"opportunity-{opportunity.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published opportunity.lost event for {opportunity.title}")
        except Exception as e:
            logger.error(f"Failed to publish opportunity.lost event: {e}")

    @staticmethod
    def publish_sales_activity_created(activity):
        """Publish sales activity created event"""
        try:
            event = SalesActivityCreatedEvent(
                data={
                    'activity_id': str(activity.id),
                    'activity_type': activity.activity_type,
                    'title': activity.title,
                    'customer_id': str(activity.customer_id) if activity.customer_id else None,
                    'opportunity_id': str(activity.opportunity_id) if activity.opportunity_id else None,
                    'tenant_id': str(activity.tenant_id) if activity.tenant_id else None,
                    'created_at': activity.created_at.isoformat() if activity.created_at else None,
                },
                correlation_id=f"activity-{activity.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published sales_activity.created event for {activity.title}")
        except Exception as e:
            logger.error(f"Failed to publish sales_activity.created event: {e}")


# Django signal handlers for automatic event publishing

@receiver(post_save, sender=Customer)
def handle_customer_save(sender, instance, created, **kwargs):
    """Handle customer save events"""
    if created:
        SalesEventPublisher.publish_customer_created(instance)
    else:
        SalesEventPublisher.publish_customer_updated(instance)


@receiver(post_delete, sender=Customer)
def handle_customer_delete(sender, instance, **kwargs):
    """Handle customer delete events"""
    SalesEventPublisher.publish_customer_deleted(instance)


@receiver(post_save, sender=Opportunity)
def handle_opportunity_save(sender, instance, created, **kwargs):
    """Handle opportunity save events"""
    if created:
        SalesEventPublisher.publish_opportunity_created(instance)
    else:
        SalesEventPublisher.publish_opportunity_updated(instance)


@receiver(post_save, sender=SalesActivity)
def handle_sales_activity_save(sender, instance, created, **kwargs):
    """Handle sales activity save events"""
    if created:
        SalesEventPublisher.publish_sales_activity_created(instance)
