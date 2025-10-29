import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class LeaveRequest(models.Model):
    """
    Model for employee leave requests with comprehensive tracking and approval workflow.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    LEAVE_TYPE_CHOICES = [
        ("annual_leave", "Annual Leave"),
        ("sick_leave", "Sick Leave"),
        ("personal_leave", "Personal Leave"),
        ("maternity_leave", "Maternity/Paternity Leave"),
        ("emergency_leave", "Emergency Leave"),
        ("unpaid_leave", "Unpaid Leave"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending Approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
        ("taken", "Leave Taken"),
    ]

    # Core request information
    employee = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='leave_requests',
        help_text="Employee requesting leave"
    )
    tenant = models.ForeignKey(
        'accounts.Tenant',
        on_delete=models.CASCADE,
        related_name='leave_requests',
        db_index=True,
        help_text="Company/tenant the request belongs to"
    )

    # Leave details
    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_TYPE_CHOICES,
        help_text="Type of leave being requested"
    )
    start_date = models.DateField(help_text="First day of leave")
    end_date = models.DateField(help_text="Last day of leave")
    days_requested = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0.5), MaxValueValidator(365)],
        help_text="Total number of leave days requested"
    )
    reason = models.TextField(
        blank=True,
        help_text="Reason for the leave request"
    )

    # Status and workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Current status of the leave request"
    )
    applied_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When the leave request was submitted"
    )

    # Approval information
    approved_by = models.ForeignKey(
        'accounts.CustomUser',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_leave_requests',
        help_text="Manager who approved/rejected the request"
    )
    approved_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request was approved/rejected"
    )
    approval_notes = models.TextField(
        blank=True,
        help_text="Notes from the approver"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_date']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_date__lte=models.F('end_date')),
                name='leave_request_start_before_end'
            ),
            models.CheckConstraint(
                check=models.Q(days_requested__gt=0),
                name='leave_request_positive_days'
            ),
        ]

    def clean(self):
        """Validate leave request data."""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Start date cannot be after end date.")

            # Calculate business days (excluding weekends) only if days_requested is not set
            if not self.days_requested:
                from datetime import timedelta
                business_days = 0
                current_date = self.start_date
                while current_date <= self.end_date:
                    # Monday = 0, Sunday = 6
                    if current_date.weekday() < 5:  # Monday to Friday
                        business_days += 1
                    current_date += timedelta(days=1)
                self.days_requested = Decimal(str(business_days))

    def save(self, *args, **kwargs):
        # Generate slug if not present
        if not self.slug:
            base_slug = f"leave-{self.employee.id}-{self.start_date}"
            self.slug = slugify(base_slug)

            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while LeaveRequest.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        # Run validation
        self.clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type} ({self.start_date} to {self.end_date})"

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def duration_display(self):
        """Human-readable duration display."""
        if self.days_requested == 1:
            return "1 day"
        elif self.days_requested % 1 == 0:
            return f"{int(self.days_requested)} days"
        else:
            return f"{self.days_requested} days"


class LeaveBalance(models.Model):
    """
    Model for tracking employee leave balances by year and leave type.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    employee = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='leave_balances',
        help_text="Employee whose leave balance this represents"
    )
    tenant = models.ForeignKey(
        'accounts.Tenant',
        on_delete=models.CASCADE,
        related_name='leave_balances',
        db_index=True,
        help_text="Company/tenant the balance belongs to"
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LeaveRequest.LEAVE_TYPE_CHOICES,
        help_text="Type of leave this balance applies to"
    )
    year = models.IntegerField(
        help_text="Calendar year for this leave balance"
    )

    # Balance tracking
    total_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(0)],
        help_text="Total leave days allocated for this year"
    )
    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Days already used this year"
    )
    carried_over = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Days carried over from previous year"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'leave_type']
        unique_together = ['employee', 'leave_type', 'year']
        indexes = [
            models.Index(fields=['tenant', 'year']),
            models.Index(fields=['employee', 'year']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(used_days__lte=models.F('total_days') + models.F('carried_over')),
                name='leave_balance_used_within_total'
            ),
        ]

    def save(self, *args, **kwargs):
        # Generate slug if not present
        if not self.slug:
            base_slug = f"balance-{self.employee.id}-{self.leave_type}-{self.year}"
            self.slug = slugify(base_slug)

            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while LeaveBalance.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type} ({self.year})"

    @property
    def remaining_days(self):
        """Calculate remaining leave days."""
        return self.total_days + self.carried_over - self.used_days

    @property
    def utilization_percentage(self):
        """Calculate leave utilization as percentage."""
        total_available = self.total_days + self.carried_over
        if total_available == 0:
            return 0
        return round((self.used_days / total_available) * 100, 1)


class LeavePolicy(models.Model):
    """
    Model for company-wide leave policies and rules.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    tenant = models.ForeignKey(
        'accounts.Tenant',
        on_delete=models.CASCADE,
        related_name='leave_policies',
        db_index=True,
        help_text="Company/tenant this policy applies to"
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LeaveRequest.LEAVE_TYPE_CHOICES,
        help_text="Type of leave this policy applies to"
    )

    # Policy settings
    annual_entitlement = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0)],
        help_text="Default annual leave entitlement in days"
    )
    max_consecutive_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        help_text="Maximum consecutive days allowed for this leave type"
    )
    notice_period_days = models.IntegerField(
        default=7,
        validators=[MinValueValidator(0)],
        help_text="Minimum notice period required in working days"
    )

    # Carry-over rules
    carry_over_allowed = models.BooleanField(
        default=True,
        help_text="Whether unused leave can be carried over to next year"
    )
    max_carry_over = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum days that can be carried over (null = unlimited)"
    )

    # Auto-approval rules
    auto_approve_max_days = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum days that can be auto-approved (null = no auto-approval)"
    )

    # Policy status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this policy is currently active"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['leave_type']
        unique_together = ['tenant', 'leave_type']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
        ]

    def save(self, *args, **kwargs):
        # Generate slug if not present
        if not self.slug:
            base_slug = f"policy-{self.tenant.id}-{self.leave_type}"
            self.slug = slugify(base_slug)

            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while LeavePolicy.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant.name} - {self.leave_type} Policy"

    def allows_auto_approval(self, days_requested):
        """Check if the requested days qualify for auto-approval."""
        if not self.auto_approve_max_days:
            return False
        return days_requested <= self.auto_approve_max_days