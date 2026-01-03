"""
Audit log models for audit service.
"""
import uuid
from django.db import models


class AuditLog(models.Model):
    """
    Comprehensive audit logging for all services.
    """

    ACTION_CHOICES = [
        ("user_signup", "User Signup"),
        ("user_login", "User Login"),
        ("user_logout", "User Logout"),
        ("user_profile_update", "Profile Update"),
        ("user_password_change", "Password Change"),
        ("invitation_sent", "Invitation Sent"),
        ("invitation_confirmed", "Invitation Confirmed"),
        ("invitation_used", "Invitation Used"),
        ("invitation_cancelled", "Invitation Cancelled"),
        ("invitation_expired", "Invitation Expired"),
        ("member_approved", "Member Approved"),
        ("member_rejected", "Member Rejected"),
        ("role_created", "Role Created"),
        ("role_updated", "Role Updated"),
        ("role_assigned", "Role Assigned"),
        ("project_created", "Project Created"),
        ("project_updated", "Project Updated"),
        ("project_deleted", "Project Deleted"),
        ("invoice_created", "Invoice Created"),
        ("invoice_paid", "Invoice Paid"),
        ("payment_received", "Payment Received"),
        ("leave_requested", "Leave Requested"),
        ("leave_approved", "Leave Approved"),
        ("leave_rejected", "Leave Rejected"),
        ("sale_created", "Sale Created"),
        ("opportunity_created", "Opportunity Created"),
        ("customer_created", "Customer Created"),
        ("security_failed_login", "Failed Login Attempt"),
        ("security_token_misuse", "Token Misuse"),
        ("admin_user_suspended", "User Suspended"),
        ("admin_user_activated", "User Activated"),
    ]

    RESOURCE_TYPE_CHOICES = [
        ("user", "User"),
        ("invitation", "Invitation"),
        ("role", "Role"),
        ("tenant", "Tenant"),
        ("profile", "User Profile"),
        ("project", "Project"),
        ("invoice", "Invoice"),
        ("payment", "Payment"),
        ("leave_request", "Leave Request"),
        ("customer", "Customer"),
        ("opportunity", "Opportunity"),
        ("sales_activity", "Sales Activity"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    tenant_id = models.UUIDField(null=True, blank=True, db_index=True)
    user_id = models.UUIDField(null=True, blank=True, db_index=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPE_CHOICES, db_index=True)
    resource_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['tenant_id', 'timestamp']),
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]

    def __str__(self):
        user_info = f" by {self.user_id}" if self.user_id else ""
        return f"{self.get_action_display()} on {self.get_resource_type_display()}{user_info} at {self.timestamp}"
