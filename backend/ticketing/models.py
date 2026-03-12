import hashlib
import secrets
import uuid

from django.conf import settings
from django.db import models


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("blocked", "Blocked"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="tickets",
        null=True,
        blank=True,
        db_index=True,
    )
    client = models.ForeignKey(
        "project.Client",
        on_delete=models.CASCADE,
        related_name="tickets",
        db_index=True,
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open", db_index=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium", db_index=True)
    category = models.CharField(max_length=100, blank=True, default="")
    source = models.CharField(max_length=50, blank=True, default="")
    external_id = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    requester_name = models.CharField(max_length=200, blank=True, default="")
    requester_email = models.EmailField(blank=True, default="")
    first_logged_at = models.DateTimeField(auto_now_add=True)
    first_response_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["client", "external_id"], name="unique_ticket_external_id_per_client")
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"


class TicketComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments", db_index=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_comments",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment on {self.ticket_id}"


class TicketAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="attachments", db_index=True)
    comment = models.ForeignKey(
        TicketComment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attachments",
    )
    file = models.FileField(upload_to="ticket_attachments/%Y/%m/%d/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_attachments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Attachment for {self.ticket_id}"


class TicketStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="status_history", db_index=True)
    from_status = models.CharField(max_length=20, blank=True, default="")
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_status_changes",
    )
    note = models.TextField(blank=True, default="")
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]

    def __str__(self) -> str:
        return f"{self.ticket_id}: {self.from_status} -> {self.to_status}"


class ClientIntegration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.OneToOneField(
        "project.Client",
        on_delete=models.CASCADE,
        related_name="integration",
    )
    api_key_prefix = models.CharField(max_length=12, db_index=True)
    api_key_hash = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_raw_key() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_key() -> str:
        return secrets.token_urlsafe(32)

    def set_key(self, raw_key: str) -> None:
        self.api_key_prefix = raw_key[:8]
        self.api_key_hash = self.hash_key(raw_key)

    def verify_key(self, raw_key: str) -> bool:
        return self.api_key_hash == self.hash_key(raw_key)

    def __str__(self) -> str:
        return f"Integration for {self.client_id}"
