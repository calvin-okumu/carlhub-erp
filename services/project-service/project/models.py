"""
Project models for project service.
"""

import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)


class Client(SoftDeleteMixin, models.Model):
    """Client model for project service"""
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("prospect", "Prospect"),
    ]

    LEAD_SOURCE_CHOICES = [
        ("website", "Website"),
        ("referral", "Referral"),
        ("social_media", "Social Media"),
        ("cold_outreach", "Cold Outreach"),
        ("trade_show", "Trade Show"),
        ("other", "Other"),
    ]

    COMPANY_SIZE_CHOICES = [
        ("1-10", "1-10 employees"),
        ("11-50", "11-50 employees"),
        ("51-200", "51-200 employees"),
        ("201-1000", "201-1000 employees"),
        ("1000+", "1000+ employees"),
    ]

    PAYMENT_TERMS_CHOICES = [
        ("immediate", "Immediate"),
        ("net_15", "Net 15"),
        ("net_30", "Net 30"),
        ("net_45", "Net 45"),
        ("net_60", "Net 60"),
        ("custom", "Custom"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Enter a valid phone number.")]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="prospect", db_index=True)
    tenant_id = models.UUIDField(db_index=True)

    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True)
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

    payment_terms = models.CharField(max_length=50, choices=PAYMENT_TERMS_CHOICES, default="net_30")
    tax_id = models.CharField(max_length=50, blank=True)

    lead_source = models.CharField(
        max_length=50,
        choices=LEAD_SOURCE_CHOICES,
        blank=True,
        help_text="How did we acquire this client?"
    )
    lead_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Lead qualification score (0-100)"
    )

    last_contact = models.DateTimeField(null=True, blank=True)
    next_followup = models.DateTimeField(null=True, blank=True)
    satisfaction_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Client satisfaction rating (1-5)"
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["primary_contact_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while Client.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class Contract(SoftDeleteMixin, models.Model):
    """LPO/Contract management system"""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent to Client"),
        ("signed", "Signed"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    tenant_id = models.UUIDField(db_index=True)
    client_id = models.UUIDField(db_index=True)
    project_id = models.UUIDField(db_index=True, unique=True)

    contract_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft", db_index=True)

    total_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    currency = models.CharField(max_length=3, default="USD")
    payment_schedule = models.TextField(blank=True)

    issued_date = models.DateField(null=True, blank=True)
    signed_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    contract_file = models.FileField(upload_to="contracts/", null=True, blank=True)
    signed_contract_file = models.FileField(upload_to="contracts/signed/", null=True, blank=True)

    approved_by_id = models.UUIDField(null=True, blank=True, db_index=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    created_by_id = models.UUIDField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["client_id", "status"]),
            models.Index(fields=["project_id"]),
            models.Index(fields=["contract_number"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.contract_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"contract-{self.contract_number}")
            original_slug = self.slug
            counter = 1
            while Contract.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date")


class Project(SoftDeleteMixin, models.Model):
    """Project model with denormalized user references from JWT token"""
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

    PHASE_CHOICES = [
        ("initiation", "Initiation"),
        ("planning", "Planning"),
        ("execution", "Execution"),
        ("monitoring", "Monitoring"),
        ("closure", "Closure"),
    ]

    RISK_LEVEL_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    tenant_id = models.UUIDField(db_index=True)
    client_id = models.UUIDField(db_index=True, null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="planning")
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default="medium")
    phase = models.CharField(max_length=10, choices=PHASE_CHOICES, default="initiation")
    risk_level = models.CharField(max_length=8, choices=RISK_LEVEL_CHOICES, default="low")

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

    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    actual_hours = models.PositiveIntegerField(default=0)

    quality_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Project quality rating (1-5)"
    )
    client_feedback = models.TextField(blank=True)

    auto_complete_on_invoice_paid = models.BooleanField(default=False)
    notify_on_phase_change = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["client_id", "created_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["phase"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.name

    def calculate_progress(self):
        from django.db.models import Avg
        milestones = Milestone.objects.filter(project_id=self.id, is_deleted=False)
        if milestones.exists():
            avg_progress = milestones.aggregate(avg_progress=Avg('progress'))['avg_progress']
            return int(avg_progress) if avg_progress else 0
        return 0

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date")


class Milestone(SoftDeleteMixin, models.Model):
    """Milestone model for project service"""
    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("archived", "Archived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="New Milestone")
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="planning")

    planned_start = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    tenant_id = models.UUIDField(db_index=True)
    project_id = models.UUIDField(db_index=True)
    assignee_id = models.UUIDField(null=True, blank=True, db_index=True)

    progress = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["project_id", "status"]),
            models.Index(fields=["assignee_id", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title

    def calculate_progress(self):
        from django.db.models import Avg
        sprints = Sprint.objects.filter(milestone_id=self.id, is_deleted=False)
        if sprints.exists():
            avg_progress = sprints.aggregate(avg_progress=Avg('progress'))['avg_progress']
            return int(avg_progress) if avg_progress else 0

        tasks = Task.objects.filter(milestone_id=self.id, is_deleted=False)
        if tasks.exists():
            completed_tasks = tasks.filter(status='done').count()
            progress = int((completed_tasks / tasks.count()) * 100)
            return progress
        return 0

    def clean(self):
        if self.planned_start and self.due_date and self.planned_start > self.due_date:
            raise ValidationError("Planned start date must be before due date")


class Sprint(SoftDeleteMixin, models.Model):
    """Sprint model for agile project management"""
    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="planned")

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    tenant_id = models.UUIDField(db_index=True)
    milestone_id = models.UUIDField(db_index=True)
    project_id = models.UUIDField(db_index=True)

    progress = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["milestone_id", "status"]),
            models.Index(fields=["project_id", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.name

    def calculate_progress(self):
        tasks = Task.objects.filter(sprint_id=self.id, is_deleted=False)
        if tasks.exists():
            completed_tasks = tasks.filter(status='done').count()
            progress = int((completed_tasks / tasks.count()) * 100)
            return progress
        return 0

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Sprint start date must be before end date")

        if self.milestone_id:
            from .models import Milestone
            try:
                milestone = Milestone.objects.get(id=self.milestone_id)
                if self.start_date and milestone.planned_start and self.start_date < milestone.planned_start:
                    raise ValidationError("Sprint start date must be after milestone start date")
                if self.end_date and milestone.due_date and self.end_date > milestone.due_date:
                    raise ValidationError("Sprint end date must be before milestone due date")
            except Milestone.DoesNotExist:
                pass


class Task(SoftDeleteMixin, models.Model):
    """Task model with denormalized assignee fields from JWT token"""
    STATUS_CHOICES = [
        ("to_do", "To Do"),
        ("in_progress", "In Progress"),
        ("in_review", "In Review"),
        ("testing", "Testing"),
        ("done", "Done"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="New Task")
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="to_do", db_index=True)

    tenant_id = models.UUIDField(db_index=True)
    milestone_id = models.UUIDField(null=True, blank=True, db_index=True)
    project_id = models.UUIDField(db_index=True)
    sprint_id = models.UUIDField(null=True, blank=True, db_index=True)

    # Denormalized user fields (from JWT token)
    assignee_id = models.UUIDField(null=True, blank=True, db_index=True, help_text="UUID of task assignee")
    assignee_email = models.EmailField(null=True, blank=True, help_text="Email of task assignee")
    assignee_name = models.CharField(max_length=200, null=True, blank=True, help_text="Full name of task assignee")

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["project_id", "status"]),
            models.Index(fields=["milestone_id", "status"]),
            models.Index(fields=["sprint_id", "status"]),
            models.Index(fields=["assignee_id", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title

    @property
    def progress(self):
        status_progress_map = {
            "to_do": 0,
            "in_progress": 25,
            "in_review": 75,
            "testing": 90,
            "done": 100,
        }
        return status_progress_map.get(self.status, 0)

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date")

        if self.sprint_id and self.milestone_id:
            from .models import Sprint
            try:
                sprint = Sprint.objects.get(id=self.sprint_id)
                if sprint.milestone_id != self.milestone_id:
                    raise ValidationError("Task milestone must match sprint milestone")
            except Sprint.DoesNotExist:
                pass
