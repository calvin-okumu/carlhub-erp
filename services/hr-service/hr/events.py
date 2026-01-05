"""
HR Service Event Publishers

This module contains event publishers for HR Service.
Events are published when employees, leave requests, or payroll is created/updated.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Employee, LeaveRequest, Payroll
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.event_bus import event_bus, BaseEvent

logger = logging.getLogger(__name__)


class EmployeeCreatedEvent(BaseEvent):
    """Event published when a new employee is created"""
    event_type: str = "employee.created"
    source_service: str = "hr"


class EmployeeUpdatedEvent(BaseEvent):
    """Event published when an employee is updated"""
    event_type: str = "employee.updated"
    source_service: str = "hr"


class EmployeeTerminatedEvent(BaseEvent):
    """Event published when an employee is terminated"""
    event_type: str = "employee.terminated"
    source_service: str = "hr"


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


class PayrollCreatedEvent(BaseEvent):
    """Event published when payroll is created"""
    event_type: str = "payroll.created"
    source_service: str = "hr"


class PayrollUpdatedEvent(BaseEvent):
    """Event published when payroll is updated"""
    event_type: str = "payroll.updated"
    source_service: str = "hr"


class HREventPublisher:
    """Publisher for HR-related events"""

    @staticmethod
    def publish_employee_created(employee):
        """Publish employee created event"""
        try:
            event = EmployeeCreatedEvent(
                data={
                    'employee_id': str(employee.id),
                    'first_name': employee.first_name,
                    'last_name': employee.last_name,
                    'email': employee.email,
                    'employee_id_field': employee.employee_id,
                    'hire_date': employee.hire_date.isoformat() if employee.hire_date else None,
                    'tenant_id': str(employee.tenant_id) if employee.tenant_id else None,
                    'department_id': str(employee.department_id) if employee.department_id else None,
                    'created_at': employee.created_at.isoformat() if employee.created_at else None,
                },
                correlation_id=f"employee-{employee.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published employee.created event for {employee.email}")
        except Exception as e:
            logger.error(f"Failed to publish employee.created event: {e}")

    @staticmethod
    def publish_employee_updated(employee, changes=None):
        """Publish employee updated event"""
        try:
            event = EmployeeUpdatedEvent(
                data={
                    'employee_id': str(employee.id),
                    'first_name': employee.first_name,
                    'last_name': employee.last_name,
                    'email': employee.email,
                    'changes': changes or {},
                    'updated_at': employee.updated_at.isoformat() if employee.updated_at else None,
                },
                correlation_id=f"employee-{employee.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published employee.updated event for {employee.email}")
        except Exception as e:
            logger.error(f"Failed to publish employee.updated event: {e}")

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

    @staticmethod
    def publish_payroll_created(payroll):
        """Publish payroll created event"""
        try:
            event = PayrollCreatedEvent(
                data={
                    'payroll_id': str(payroll.id),
                    'employee_id': str(payroll.employee_id) if payroll.employee_id else None,
                    'pay_period': payroll.pay_period,
                    'gross_pay': str(payroll.gross_pay) if payroll.gross_pay else None,
                    'net_pay': str(payroll.net_pay) if payroll.net_pay else None,
                    'tenant_id': str(payroll.tenant_id) if payroll.tenant_id else None,
                    'created_at': payroll.created_at.isoformat() if payroll.created_at else None,
                },
                correlation_id=f"payroll-{payroll.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published payroll.created event for {payroll.id}")
        except Exception as e:
            logger.error(f"Failed to publish payroll.created event: {e}")

    @staticmethod
    def publish_payroll_updated(payroll, changes=None):
        """Publish payroll updated event"""
        try:
            event = PayrollUpdatedEvent(
                data={
                    'payroll_id': str(payroll.id),
                    'employee_id': str(payroll.employee_id) if payroll.employee_id else None,
                    'changes': changes or {},
                    'updated_at': payroll.updated_at.isoformat() if payroll.updated_at else None,
                },
                correlation_id=f"payroll-{payroll.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published payroll.updated event for {payroll.id}")
        except Exception as e:
            logger.error(f"Failed to publish payroll.updated event: {e}")


# Django signal handlers for automatic event publishing

@receiver(post_save, sender=Employee)
def handle_employee_save(sender, instance, created, **kwargs):
    """Handle employee save events"""
    if created:
        HREventPublisher.publish_employee_created(instance)
    else:
        HREventPublisher.publish_employee_updated(instance)


@receiver(post_save, sender=LeaveRequest)
def handle_leave_request_save(sender, instance, created, **kwargs):
    """Handle leave request save events"""
    if created:
        HREventPublisher.publish_leave_requested(instance)


@receiver(post_save, sender=Payroll)
def handle_payroll_save(sender, instance, created, **kwargs):
    """Handle payroll save events"""
    if created:
        HREventPublisher.publish_payroll_created(instance)
    else:
        HREventPublisher.publish_payroll_updated(instance)
