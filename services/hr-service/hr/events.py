"""
HR Service Event Publishers

This module contains event publishers for HR Service.
Events are published when leave requests are created/updated.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LeaveRequest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.event_bus import event_bus, BaseEvent

logger = logging.getLogger(__name__)


class LeaveRequestedEvent(BaseEvent):
    """Event published when a leave is requested"""
    event_type: str = "leave.requested"
    source_service: str = "hr"


class LeaveApprovedEvent(BaseEvent):
    """Event published when a leave is approved"""
    event_type: str = "leave.approved"
    source_service: str = "hr"


class LeaveRejectedEvent(BaseEvent):
    """Event published when a leave is rejected"""
    event_type: str = "leave.rejected"
    source_service: str = "hr"


class HREventPublisher:
    """Publisher for HR-related events"""

    @staticmethod
    def publish_leave_requested(leave_request):
        """Publish leave requested event"""
        try:
            event = LeaveRequestedEvent(
                data={
                    'leave_request_id': str(leave_request.id),
                    'employee_id': str(leave_request.employee_id) if leave_request.employee_id else None,
                    'start_date': leave_request.start_date.isoformat() if leave_request.start_date else None,
                    'end_date': leave_request.end_date.isoformat() if leave_request.end_date else None,
                    'leave_type': leave_request.leave_type,
                    'status': leave_request.status,
                    'tenant_id': str(leave_request.tenant_id) if leave_request.tenant_id else None,
                    'created_at': leave_request.created_at.isoformat() if leave_request.created_at else None,
                },
                correlation_id=f"leave-{leave_request.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published leave.requested event for request {leave_request.id}")
        except Exception as e:
            logger.error(f"Failed to publish leave.requested event: {e}")

    @staticmethod
    def publish_leave_approved(leave_request):
        """Publish leave approved event"""
        try:
            event = LeaveApprovedEvent(
                data={
                    'leave_request_id': str(leave_request.id),
                    'approved_by': str(leave_request.approved_by) if leave_request.approved_by else None,
                    'approved_at': leave_request.approved_at.isoformat() if leave_request.approved_at else None,
                    'tenant_id': str(leave_request.tenant_id) if leave_request.tenant_id else None,
                },
                correlation_id=f"leave-{leave_request.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published leave.approved event for request {leave_request.id}")
        except Exception as e:
            logger.error(f"Failed to publish leave.approved event: {e}")

    @staticmethod
    def publish_leave_rejected(leave_request):
        """Publish leave rejected event"""
        try:
            event = LeaveRejectedEvent(
                data={
                    'leave_request_id': str(leave_request.id),
                    'rejected_by': str(leave_request.rejected_by) if leave_request.rejected_by else None,
                    'rejected_at': leave_request.rejected_at.isoformat() if leave_request.rejected_at else None,
                    'rejection_reason': leave_request.rejection_reason,
                    'tenant_id': str(leave_request.tenant_id) if leave_request.tenant_id else None,
                },
                correlation_id=f"leave-{leave_request.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published leave.rejected event for request {leave_request.id}")
        except Exception as e:
            logger.error(f"Failed to publish leave.rejected event: {e}")


# Django signal handlers for automatic event publishing

@receiver(post_save, sender=LeaveRequest)
def handle_leave_request_save(sender, instance, created, **kwargs):
    """Handle leave request save events"""
    if created:
        HREventPublisher.publish_leave_requested(instance)

