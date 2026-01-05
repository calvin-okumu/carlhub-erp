"""
Accounting Service Event Publishers

This module contains event publishers for Accounting Service.
Events are published when invoices, payments, or accounts are created/updated.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Invoice, Payment, Account
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.event_bus import event_bus, BaseEvent

logger = logging.getLogger(__name__)


class InvoiceCreatedEvent(BaseEvent):
    """Event published when a new invoice is created"""
    event_type: str = "invoice.created"
    source_service: str = "accounting"


class InvoicePaidEvent(BaseEvent):
    """Event published when an invoice is paid"""
    event_type: str = "invoice.paid"
    source_service: str = "accounting"


class InvoiceCancelledEvent(BaseEvent):
    """Event published when an invoice is cancelled"""
    event_type: str = "invoice.cancelled"
    source_service: str = "accounting"


class PaymentReceivedEvent(BaseEvent):
    """Event published when a payment is received"""
    event_type: str = "payment.received"
    source_service: str = "accounting"


class PaymentProcessedEvent(BaseEvent):
    """Event published when a payment is processed"""
    event_type: str = "payment.processed"
    source_service: str = "accounting"


class AccountCreatedEvent(BaseEvent):
    """Event published when a new account is created"""
    event_type: str = "account.created"
    source_service: str = "accounting"


class AccountingEventPublisher:
    """Publisher for accounting-related events"""

    @staticmethod
    def publish_invoice_created(invoice):
        """Publish invoice created event"""
        try:
            event = InvoiceCreatedEvent(
                data={
                    'invoice_id': str(invoice.id),
                    'invoice_number': invoice.invoice_number,
                    'customer_id': str(invoice.customer_id) if invoice.customer_id else None,
                    'tenant_id': str(invoice.tenant_id) if invoice.tenant_id else None,
                    'amount': str(invoice.amount) if invoice.amount else None,
                    'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
                    'status': invoice.status,
                    'created_at': invoice.created_at.isoformat() if invoice.created_at else None,
                },
                correlation_id=f"invoice-{invoice.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published invoice.created event for {invoice.invoice_number}")
        except Exception as e:
            logger.error(f"Failed to publish invoice.created event: {e}")

    @staticmethod
    def publish_invoice_paid(invoice):
        """Publish invoice paid event"""
        try:
            event = InvoicePaidEvent(
                data={
                    'invoice_id': str(invoice.id),
                    'invoice_number': invoice.invoice_number,
                    'amount': str(invoice.amount) if invoice.amount else None,
                    'paid_date': invoice.paid_at.isoformat() if invoice.paid_at else None,
                    'tenant_id': str(invoice.tenant_id) if invoice.tenant_id else None,
                    'created_at': invoice.paid_at.isoformat() if invoice.paid_at else None,
                },
                correlation_id=f"invoice-{invoice.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published invoice.paid event for {invoice.invoice_number}")
        except Exception as e:
            logger.error(f"Failed to publish invoice.paid event: {e}")

    @staticmethod
    def publish_invoice_cancelled(invoice):
        """Publish invoice cancelled event"""
        try:
            event = InvoiceCancelledEvent(
                data={
                    'invoice_id': str(invoice.id),
                    'invoice_number': invoice.invoice_number,
                    'tenant_id': str(invoice.tenant_id) if invoice.tenant_id else None,
                    'cancelled_at': invoice.cancelled_at.isoformat() if invoice.cancelled_at else None,
                    'reason': invoice.cancelled_reason,
                },
                correlation_id=f"invoice-{invoice.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published invoice.cancelled event for {invoice.invoice_number}")
        except Exception as e:
            logger.error(f"Failed to publish invoice.cancelled event: {e}")

    @staticmethod
    def publish_payment_received(payment):
        """Publish payment received event"""
        try:
            event = PaymentReceivedEvent(
                data={
                    'payment_id': str(payment.id),
                    'amount': str(payment.amount) if payment.amount else None,
                    'payment_method': payment.payment_method,
                    'invoice_id': str(payment.invoice_id) if payment.invoice_id else None,
                    'customer_id': str(payment.customer_id) if payment.customer_id else None,
                    'tenant_id': str(payment.tenant_id) if payment.tenant_id else None,
                    'created_at': payment.created_at.isoformat() if payment.created_at else None,
                },
                correlation_id=f"payment-{payment.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published payment.received event for {payment.id}")
        except Exception as e:
            logger.error(f"Failed to publish payment.received event: {e}")

    @staticmethod
    def publish_payment_processed(payment):
        """Publish payment processed event"""
        try:
            event = PaymentProcessedEvent(
                data={
                    'payment_id': str(payment.id),
                    'amount': str(payment.amount) if payment.amount else None,
                    'processed_at': payment.processed_at.isoformat() if payment.processed_at else None,
                    'tenant_id': str(payment.tenant_id) if payment.tenant_id else None,
                },
                correlation_id=f"payment-{payment.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published payment.processed event for {payment.id}")
        except Exception as e:
            logger.error(f"Failed to publish payment.processed event: {e}")

    @staticmethod
    def publish_account_created(account):
        """Publish account created event"""
        try:
            event = AccountCreatedEvent(
                data={
                    'account_id': str(account.id),
                    'account_number': account.account_number,
                    'account_name': account.account_name,
                    'account_type': account.account_type,
                    'tenant_id': str(account.tenant_id) if account.tenant_id else None,
                    'created_at': account.created_at.isoformat() if account.created_at else None,
                },
                correlation_id=f"account-{account.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published account.created event for {account.account_number}")
        except Exception as e:
            logger.error(f"Failed to publish account.created event: {e}")


# Django signal handlers for automatic event publishing

@receiver(post_save, sender=Invoice)
def handle_invoice_save(sender, instance, created, **kwargs):
    """Handle invoice save events"""
    if created:
        AccountingEventPublisher.publish_invoice_created(instance)

@receiver(post_save, sender=Payment)
def handle_payment_save(sender, instance, created, **kwargs):
    """Handle payment save events"""
    if created:
        AccountingEventPublisher.publish_payment_received(instance)
    else:
        AccountingEventPublisher.publish_payment_processed(instance)

@receiver(post_save, sender=Account)
def handle_account_save(sender, instance, created, **kwargs):
    """Handle account save events"""
    if created:
        AccountingEventPublisher.publish_account_created(instance)
