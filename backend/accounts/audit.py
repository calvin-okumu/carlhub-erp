import json
from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import AuditLog, Tenant

User = get_user_model()


class AuditLogger:
    """
    Centralized audit logging utility for DjangoCRM.
    """

    @staticmethod
    def log_event(
        action: str,
        resource_type: str,
        tenant: Optional[Tenant] = None,
        user: Optional[User] = None,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Log an audit event.

        Args:
            action: The action performed (e.g., 'user_signup', 'invitation_sent')
            resource_type: Type of resource affected (e.g., 'user', 'invitation')
            tenant: The tenant context (if applicable)
            user: The user performing the action
            resource_id: UUID of the affected resource
            old_values: Previous state of the resource
            new_values: New state of the resource
            ip_address: IP address of the request
            user_agent: User agent string
            metadata: Additional context data

        Returns:
            The created AuditLog instance
        """
        # Ensure old_values and new_values are JSON serializable
        if old_values:
            old_values = AuditLogger._make_json_serializable(old_values)
        if new_values:
            new_values = AuditLogger._make_json_serializable(new_values)
        if metadata:
            metadata = AuditLogger._make_json_serializable(metadata)

        audit_log = AuditLog.objects.create(
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

        return audit_log

    @staticmethod
    def _make_json_serializable(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert data to JSON-serializable format.
        Handles datetime objects and other non-serializable types.
        """
        def serialize_value(value):
            if hasattr(value, 'isoformat'):  # datetime objects
                return value.isoformat()
            elif hasattr(value, '__str__'):
                return str(value)
            else:
                return value

        return {key: serialize_value(value) for key, value in data.items()}

    @staticmethod
    def log_user_signup(user: User, tenant: Tenant, invitation_used: bool = False, ip_address: Optional[str] = None):
        """Log user signup event."""
        metadata = {'invitation_used': invitation_used}
        return AuditLogger.log_event(
            action='user_signup',
            resource_type='user',
            tenant=tenant,
            user=user,
            resource_id=str(user.id),
            new_values={'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name},
            ip_address=ip_address,
            metadata=metadata
        )

    @staticmethod
    def log_invitation_sent(invitation, ip_address: Optional[str] = None):
        """Log invitation sent event."""
        return AuditLogger.log_event(
            action='invitation_sent',
            resource_type='invitation',
            tenant=invitation.tenant,
            user=invitation.invited_by,
            resource_id=str(invitation.slug),
            new_values={
                'email': invitation.email,
                'role': invitation.role,
                'expires_at': invitation.expires_at
            },
            ip_address=ip_address
        )

    @staticmethod
    def log_invitation_used(invitation, user: User, ip_address: Optional[str] = None):
        """Log invitation used event."""
        return AuditLogger.log_event(
            action='invitation_used',
            resource_type='invitation',
            tenant=invitation.tenant,
            user=user,
            resource_id=str(invitation.id),
            old_values={'is_used': False},
            new_values={'is_used': True},
            ip_address=ip_address
        )

    @staticmethod
    def log_member_approved(member_user_tenant, approved_by: User, ip_address: Optional[str] = None):
        """Log member approval event."""
        return AuditLogger.log_event(
            action='member_approved',
            resource_type='user',
            tenant=member_user_tenant.tenant,
            user=approved_by,
            resource_id=str(member_user_tenant.user.id),
            old_values={'is_approved': False},
            new_values={'is_approved': True, 'role': member_user_tenant.role},
            ip_address=ip_address
        )

    @staticmethod
    def log_failed_login(email: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log failed login attempt."""
        return AuditLogger.log_event(
            action='security_failed_login',
            resource_type='user',
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={'attempted_email': email}
        )

    @staticmethod
    def log_bulk_invitation_started(bulk_invitation, ip_address: Optional[str] = None):
        """Log bulk invitation operation started."""
        return AuditLogger.log_event(
            action='bulk_invitation_started',
            resource_type='bulk_invitation',
            tenant=bulk_invitation.tenant,
            user=bulk_invitation.created_by,
            resource_id=str(bulk_invitation.id),
            new_values={
                'filename': bulk_invitation.filename,
                'total_count': bulk_invitation.total_count
            },
            ip_address=ip_address
        )


def get_client_ip(request) -> Optional[str]:
    """
    Get the client IP address from the request.
    Handles X-Forwarded-For header for proxy setups.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request) -> Optional[str]:
    """Get the user agent string from the request."""
    return request.META.get('HTTP_USER_AGENT')