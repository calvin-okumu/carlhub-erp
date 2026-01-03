import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.text import slugify

from accounts.models import SoftDeleteMixin
from saasCRM.currency import CURRENCY_CHOICES


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("prospect", "Prospect"),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Enter a valid phone number.")],
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="prospect", db_index=True
    )
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="clients",
        null=True,
        blank=True,
        db_index=True,
    )

    # Enhanced client lifecycle fields
    lead_source = models.CharField(
        max_length=50,
        choices=[
            ("website", "Website"),
            ("referral", "Referral"),
            ("social_media", "Social Media"),
            ("cold_outreach", "Cold Outreach"),
            ("trade_show", "Trade Show"),
            ("other", "Other"),
        ],
        blank=True,
        help_text="How did we acquire this client?",
    )

    lead_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Lead qualification score (0-100)",
    )

    industry = models.CharField(max_length=100, blank=True)

    company_size = models.CharField(
        max_length=20,
        choices=[
            ("1-10", "1-10 employees"),
            ("11-50", "11-50 employees"),
            ("51-200", "51-200 employees"),
            ("201-1000", "201-1000 employees"),
            ("1000+", "1000+ employees"),
        ],
        blank=True,
    )

    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)

    # Relationship management
    primary_contact = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_clients",
    )

    account_manager = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_clients",
    )

    # Financial info
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    payment_terms = models.CharField(
        max_length=50,
        choices=[
            ("immediate", "Immediate"),
            ("net_15", "Net 15"),
            ("net_30", "Net 30"),
            ("net_45", "Net 45"),
            ("net_60", "Net 60"),
            ("custom", "Custom"),
        ],
        default="net_30",
    )

    tax_id = models.CharField(max_length=50, blank=True)

    # Communication & tracking
    last_contact = models.DateTimeField(null=True, blank=True)
    next_followup = models.DateTimeField(null=True, blank=True)

    satisfaction_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Client satisfaction rating (1-5)",
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["name", "tenant"], name="unique_client_name_per_tenant")
        ]
        indexes = [
            models.Index(
                fields=["tenant", "status", "created_at"], name="client_tenant_status_created"
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Client.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Contract(models.Model):
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

    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="contracts",
        null=True,
        blank=True,
        db_index=True,
    )

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="contracts", db_index=True
    )

    project = models.OneToOneField(
        "Project", on_delete=models.CASCADE, related_name="contract_link"
    )

    contract_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Financial details
    total_value = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")

    payment_schedule = models.JSONField(default=dict, help_text="Payment milestones and amounts")

    # Dates
    issued_date = models.DateField()
    signed_date = models.DateField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    # Documents
    contract_file = models.FileField(upload_to="contracts/", null=True, blank=True)

    signed_contract_file = models.FileField(upload_to="contracts/signed/", null=True, blank=True)

    # Approval workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    approved_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_contracts",
    )

    approved_date = models.DateTimeField(null=True, blank=True)

    # Rejection handling
    rejection_reason = models.TextField(blank=True)

    # Audit
    created_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_contracts",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["client", "status"]),
            models.Index(fields=["contract_number"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            self.slug = slugify(f"contract-{self.contract_number}")

            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Contract.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.contract_number} - {self.client.name}"


class Project(SoftDeleteMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="projects",
        null=True,
        blank=True,
        db_index=True,
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="projects", db_index=True
    )
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
    tags = models.CharField(max_length=500, blank=True)  # Comma-separated
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="projects", blank=True
    )
    access_groups = models.ManyToManyField(Group, related_name="projects", blank=True)
    progress = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Enhanced lifecycle management
    PHASE_CHOICES = [
        ("initiation", "Initiation"),
        ("planning", "Planning"),
        ("execution", "Execution"),
        ("monitoring", "Monitoring & Control"),
        ("closure", "Closure"),
    ]

    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default="initiation")

    # Contract relationship
    contract = models.OneToOneField(
        Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name="project_link"
    )

    # Resource management
    estimated_hours = models.DecimalField(
        max_digits=8,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    actual_hours = models.DecimalField(
        max_digits=8,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    # Risk management
    risk_level = models.CharField(
        max_length=20,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        default="low",
    )

    # Quality metrics
    quality_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Project quality rating (1-5)",
    )

    client_feedback = models.TextField(blank=True)

    # Automation settings
    auto_complete_on_invoice_paid = models.BooleanField(default=False)
    notify_on_phase_change = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date.")

    def calculate_progress(self):
        """Calculate progress as average of milestone progress using database aggregation"""
        from django.db.models import Avg

        # Use database aggregation for better performance
        result = self.milestones.aggregate(avg_progress=Avg("progress"))
        return int(result["avg_progress"] or 0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Project.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["client", "created_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "client", "tenant"], name="unique_project_name_per_client_tenant"
            )
        ]
        indexes = [
            models.Index(
                fields=["tenant", "status", "created_at"], name="project_tenant_status_created"
            ),
            models.Index(
                fields=["tenant", "client", "status"], name="project_tenant_client_status"
            ),
        ]


class Milestone(SoftDeleteMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("active", "Active"),
        ("completed", "Completed"),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="planning")
    planned_start = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="milestones",
        null=True,
        blank=True,
        db_index=True,
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="milestones",
    )
    progress = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )  # 0-100
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="milestones",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.planned_start and self.due_date and self.planned_start >= self.due_date:
            raise ValidationError("Due date must be after planned start date.")
        # Validate dates within project
        if (
            self.project
            and self.planned_start
            and self.project.start_date
            and self.planned_start < self.project.start_date
        ):
            raise ValidationError("Milestone start date must be after project start date.")
        if (
            self.project
            and self.due_date
            and self.project.end_date
            and self.due_date > self.project.end_date
        ):
            raise ValidationError("Milestone end date must be before project end date.")

    def calculate_progress(self):
        """Calculate progress based on completed sprints ratio using database aggregation"""
        from django.db.models import Count, Q

        # Use single query with aggregation for better performance
        result = self.sprints.aggregate(
            total=Count("id"), completed=Count("id", filter=Q(status="completed"))
        )

        total = result["total"]
        completed = result["completed"]

        return 0 if total == 0 else int((completed / total) * 100)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Milestone.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.project.name})"

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "status", "created_at"], name="milestone_t_status_created"
            ),
            models.Index(fields=["project", "status"], name="milestone_project_status"),
        ]


class Sprint(SoftDeleteMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="planned", db_index=True
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="sprints",
        null=True,
        blank=True,
        db_index=True,
    )
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sprints",
        db_index=True,
    )
    progress = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")
        # Validate dates within milestone
        if (
            self.milestone
            and self.start_date
            and self.milestone.planned_start
            and self.start_date < self.milestone.planned_start
        ):
            raise ValidationError("Sprint start date must be after milestone start date.")
        if (
            self.milestone
            and self.end_date
            and self.milestone.due_date
            and self.end_date > self.milestone.due_date
        ):
            raise ValidationError("Sprint end date must be before milestone end date.")

        # Sprint completion validation
        if self.status == "completed":
            incomplete_tasks = self.tasks.exclude(status="done")
            if incomplete_tasks.exists():
                task_titles = [task.title for task in incomplete_tasks[:3]]
                raise ValidationError(
                    f"Cannot complete sprint '{self.name}'. "
                    f"{incomplete_tasks.count()} tasks are not done: {', '.join(task_titles)}"
                )

        # Status transition validation
        if self.pk:  # Existing instance
            old_instance = Sprint.objects.get(pk=self.pk)
            valid_transitions = {
                "planned": ["active", "canceled"],
                "active": ["completed", "canceled"],
                "completed": [],  # Cannot change from completed
                "canceled": ["planned"],  # Allow restart
            }
            if self.status not in valid_transitions.get(old_instance.status, []):
                raise ValidationError(
                    f"Invalid status transition from '{old_instance.status}' to '{self.status}'"
                )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Sprint.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.milestone.name})"

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "status", "created_at"], name="sprint_tenant_status_created"
            ),
            models.Index(fields=["milestone", "status"], name="sprint_milestone_status"),
        ]


class Task(SoftDeleteMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ("to_do", "To Do"),
        ("in_progress", "In Progress"),
        ("in_review", "In Review"),
        ("testing", "Testing"),
        ("done", "Done"),
    ]
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="to_do", db_index=True)
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True,
        db_index=True,
    )
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        db_index=True,
    )
    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        db_index=True,
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(
        null=True, blank=True, help_text="Approximate hours expected"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")
        if self.sprint and self.sprint.milestone != self.milestone:
            raise ValidationError("Task milestone must match sprint milestone.")
        # Validate dates within milestone
        if (
            self.milestone
            and self.start_date
            and self.milestone.planned_start
            and self.start_date < self.milestone.planned_start
        ):
            raise ValidationError("Task start date must be after milestone start date.")
        if (
            self.milestone
            and self.end_date
            and self.milestone.due_date
            and self.end_date > self.milestone.due_date
        ):
            raise ValidationError("Task end date must be before milestone end date.")

    @property
    def progress(self):
        status_weights = {
            "to_do": 0,
            "in_progress": 25,
            "in_review": 50,
            "testing": 75,
            "done": 100,
        }
        return status_weights.get(self.status, 0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Task.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "status", "created_at"], name="task_tenant_status_created"
            ),
            models.Index(
                fields=["tenant", "assignee", "status"], name="task_tenant_assignee_status"
            ),
            models.Index(fields=["milestone", "status"], name="task_milestone_status"),
            models.Index(fields=["sprint", "status"], name="task_sprint_status"),
        ]
