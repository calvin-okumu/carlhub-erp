"""
Project models for project service.
"""
import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Client(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("prospect", "Prospect"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="prospect", db_index=True)
    tenant_id = models.UUIDField(db_index=True)
    
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    
    primary_contact_id = models.UUIDField(null=True, blank=True)
    account_manager_id = models.UUIDField(null=True, blank=True)
    
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    payment_terms = models.CharField(max_length=50, default="net_30")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("active", "Active"),
        ("on_hold", "On Hold"),
        ("completed", "Completed"),
        ("archived", "Archived"),
    ]
    
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    tenant_id = models.UUIDField(db_index=True)
    client_id = models.UUIDField(db_index=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="planning")
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default="medium")
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True)
    
    progress = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["client_id", "created_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name


class Milestone(models.Model):
    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("active", "Active"),
        ("completed", "Completed"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="planning")
    
    planned_start = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    
    tenant_id = models.UUIDField(db_index=True)
    assignee_id = models.UUIDField(null=True, blank=True)
    progress = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    project_id = models.UUIDField(db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["project_id", "status"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.project_id})"


class Task(models.Model):
    STATUS_CHOICES = [
        ("to_do", "To Do"),
        ("in_progress", "In Progress"),
        ("in_review", "In Review"),
        ("testing", "Testing"),
        ("done", "Done"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="to_do", db_index=True)
    
    tenant_id = models.UUIDField(db_index=True)
    milestone_id = models.UUIDField(null=True, blank=True, db_index=True)
    assignee_id = models.UUIDField(null=True, blank=True)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["tenant_id", "assignee_id", "status"]),
            models.Index(fields=["milestone_id", "status"]),
        ]

    def __str__(self):
        return self.title
