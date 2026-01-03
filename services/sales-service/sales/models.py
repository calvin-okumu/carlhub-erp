"""
Sales models for sales service.
"""
from decimal import Decimal
import uuid
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


class Customer(models.Model):
    STATUS_CHOICES = [
        ("prospect", "Prospect"),
        ("qualified", "Qualified Lead"),
        ("proposal", "Proposal Sent"),
        ("negotiation", "In Negotiation"),
        ("won", "Won"),
        ("lost", "Lost"),
        ("inactive", "Inactive"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^\\+?1?\\d{9,15}$", "Enter a valid phone number.")],
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="prospect", db_index=True)
    lead_source = models.CharField(max_length=50, blank=True)
    lead_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    
    company_name = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    
    primary_contact = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    
    assigned_to_id = models.UUIDField(null=True, blank=True, db_index=True)
    
    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    currency = models.CharField(max_length=3, default="USD")
    
    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)
    
    last_contact = models.DateTimeField(null=True, blank=True)
    next_followup = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    tenant_id = models.UUIDField(null=True, blank=True, db_index=True)
    created_by_id = models.UUIDField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["assigned_to_id", "status"]),
            models.Index(fields=["lead_score"]),
            models.Index(fields=["expected_close_date"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class Opportunity(models.Model):
    STAGE_CHOICES = [
        ("prospecting", "Prospecting"),
        ("qualification", "Qualification"),
        ("proposal", "Proposal"),
        ("negotiation", "Negotiation"),
        ("closed_won", "Closed Won"),
        ("closed_lost", "Closed Lost"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    
    customer_id = models.UUIDField(db_index=True)
    assigned_to_id = models.UUIDField(null=True, blank=True)
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    value = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    currency = models.CharField(max_length=3, default="USD")
    probability = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    
    stage = models.CharField(
        max_length=20, choices=STAGE_CHOICES, default="prospecting", db_index=True
    )
    
    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)
    
    competitors = models.TextField(blank=True)
    competitive_advantage = models.TextField(blank=True)
    
    requirements = models.TextField(blank=True)
    pain_points = models.TextField(blank=True)
    
    next_steps = models.TextField(blank=True)
    next_followup = models.DateTimeField(null=True, blank=True)
    
    tenant_id = models.UUIDField(null=True, blank=True, db_index=True)
    created_by_id = models.UUIDField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "stage"]),
            models.Index(fields=["customer_id", "stage"]),
            models.Index(fields=["assigned_to_id", "stage"]),
            models.Index(fields=["expected_close_date"]),
            models.Index(fields=["probability"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return f"{self.title} - ${self.value}"
    
    @property
    def weighted_value(self):
        return (self.value * self.probability) / 100


class SalesActivity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ("call", "Phone Call"),
        ("email", "Email"),
        ("meeting", "Meeting"),
        ("demo", "Product Demo"),
        ("proposal", "Proposal Sent"),
        ("followup", "Follow-up"),
        ("negotiation", "Negotiation"),
        ("note", "Internal Note"),
        ("other", "Other"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    customer_id = models.UUIDField(db_index=True)
    opportunity_id = models.UUIDField(null=True, blank=True)
    performed_by_id = models.UUIDField(null=True, blank=True)
    
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES, db_index=True)
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    outcome = models.TextField(blank=True)
    next_action = models.TextField(blank=True)
    next_action_date = models.DateTimeField(null=True, blank=True)
    
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    tenant_id = models.UUIDField(null=True, blank=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-completed_date", "-scheduled_date", "-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "activity_type"]),
            models.Index(fields=["customer_id", "activity_type"]),
            models.Index(fields=["opportunity_id", "activity_type"]),
            models.Index(fields=["performed_by_id", "activity_type"]),
            models.Index(fields=["scheduled_date"]),
            models.Index(fields=["completed_date"]),
        ]

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.customer_id}"
