import uuid
from decimal import Decimal

from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
    URLValidator,
)
from django.db import models
from django.utils.text import slugify


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
    phone = models.CharField(max_length=20, blank=True, validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="prospect", db_index=True)
    tenant = models.ForeignKey(
        'accounts.Tenant', on_delete=models.CASCADE, related_name="clients", null=True, blank=True, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

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


class Project(models.Model):
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
        'accounts.Tenant', on_delete=models.CASCADE, related_name="projects", null=True, blank=True, db_index=True
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="projects", db_index=True
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="planning")
    priority = models.CharField(
        max_length=6, choices=PRIORITY_CHOICES, default="medium"
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))]
    )
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True)  # Comma-separated
    team_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="projects", blank=True)
    access_groups = models.ManyToManyField(Group, related_name="projects", blank=True)
    progress = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('End date must be after start date.')

    def calculate_progress(self):
        """Calculate progress as average of milestone progress using database aggregation"""
        from django.db.models import Avg

        # Use database aggregation for better performance
        result = self.milestones.aggregate(avg_progress=Avg('progress'))
        return int(result['avg_progress'] or 0)

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


class Milestone(models.Model):
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
        'accounts.Tenant', on_delete=models.CASCADE, related_name="milestones", null=True, blank=True, db_index=True
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
        Project, on_delete=models.CASCADE, related_name="milestones", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.planned_start and self.due_date and self.planned_start >= self.due_date:
            raise ValidationError('Due date must be after planned start date.')
        # Validate dates within project
        if self.project and self.planned_start and self.project.start_date and self.planned_start < self.project.start_date:
            raise ValidationError('Milestone start date must be after project start date.')
        if self.project and self.due_date and self.project.end_date and self.due_date > self.project.end_date:
            raise ValidationError('Milestone end date must be before project end date.')

    def calculate_progress(self):
        """Calculate progress based on completed sprints ratio using database aggregation"""
        from django.db.models import Count, Q

        # Use single query with aggregation for better performance
        result = self.sprints.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed'))
        )

        total = result['total']
        completed = result['completed']

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


class Sprint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="planned", db_index=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    tenant = models.ForeignKey(
        'accounts.Tenant', on_delete=models.CASCADE, related_name="sprints", null=True, blank=True, db_index=True
    )
    milestone = models.ForeignKey(
        Milestone, on_delete=models.CASCADE, related_name="sprints", db_index=True
    )
    progress = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('End date must be after start date.')
        # Validate dates within milestone
        if self.milestone and self.start_date and self.milestone.planned_start and self.start_date < self.milestone.planned_start:
            raise ValidationError('Sprint start date must be after milestone start date.')
        if self.milestone and self.end_date and self.milestone.due_date and self.end_date > self.milestone.due_date:
            raise ValidationError('Sprint end date must be before milestone end date.')

        # Sprint completion validation
        if self.status == 'completed':
            incomplete_tasks = self.tasks.exclude(status='done')
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
                'planned': ['active', 'canceled'],
                'active': ['completed', 'canceled'],
                'completed': [],  # Cannot change from completed
                'canceled': ['planned'],  # Allow restart
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


class Task(models.Model):
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
        'accounts.Tenant', on_delete=models.CASCADE, related_name="tasks", null=True, blank=True, db_index=True
    )
    milestone = models.ForeignKey(
        Milestone, on_delete=models.CASCADE, related_name="tasks", db_index=True
    )
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks", db_index=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(null=True, blank=True, help_text="Approximate hours expected")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('End date must be after start date.')
        if self.sprint and self.sprint.milestone != self.milestone:
            raise ValidationError('Task milestone must match sprint milestone.')
        # Validate dates within milestone
        if self.milestone and self.start_date and self.milestone.planned_start and self.start_date < self.milestone.planned_start:
            raise ValidationError('Task start date must be after milestone start date.')
        if self.milestone and self.end_date and self.milestone.due_date and self.end_date > self.milestone.due_date:
            raise ValidationError('Task end date must be before milestone end date.')

    @property
    def progress(self):
        status_weights = {
            'to_do': 0,
            'in_progress': 25,
            'in_review': 50,
            'testing': 75,
            'done': 100
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


# Financial models
class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    tenant = models.ForeignKey(
        'accounts.Tenant', on_delete=models.CASCADE, related_name="invoices", null=True, blank=True, db_index=True
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="invoices", db_index=True
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="invoices", null=True, blank=True
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))]
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(f"invoice-{self.client.name}-{self.amount}")
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Invoice.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.id or 'Unsaved'} - {self.client.name}"


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    tenant = models.ForeignKey(
        'accounts.Tenant', on_delete=models.CASCADE, related_name="payments", null=True, blank=True, db_index=True
    )
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="payments", db_index=True
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))]
    )
    paid_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(f"payment-{self.invoice.id}-{self.amount}")
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Payment.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.id or 'Unsaved'} for Invoice {self.invoice.id or 'Unsaved'}"

