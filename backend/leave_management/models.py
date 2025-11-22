import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


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
        ("pending_department_manager", "Pending Department Manager"),
        ("pending_hr_manager", "Pending HR Manager"),
        ("pending_general_manager", "Pending General Manager"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
        ("taken", "Leave Taken"),
    ]

    # Core request information
    employee = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="leave_requests",
        help_text="Employee requesting leave",
    )
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="leave_requests",
        db_index=True,
        help_text="Company/tenant the request belongs to",
    )

    # Leave details
    leave_type = models.CharField(
        max_length=20, choices=LEAVE_TYPE_CHOICES, help_text="Type of leave being requested"
    )
    start_date = models.DateField(help_text="First day of leave")
    end_date = models.DateField(help_text="Last day of leave")
    days_requested = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.5")), MaxValueValidator(Decimal("365"))],
        help_text="Total number of leave days requested",
    )
    reason = models.TextField(blank=True, help_text="Reason for the leave request")

    # Status and workflow
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending_department_manager",
        db_index=True,
        help_text="Current status of leave request",
    )

    # Workflow tracking
    current_approval_level = models.CharField(
        max_length=20,
        choices=(
            ("department_manager", "Department Manager"),
            ("hr_manager", "HR Manager"),
            ("general_manager", "General Manager"),
        ),
        default="department_manager",
        help_text="Current approval level in workflow",
    )
    applied_date = models.DateTimeField(
        auto_now_add=True, help_text="When the leave request was submitted"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveBalance(models.Model):
    """
    Model for tracking employee leave balances by year and leave type.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    employee = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="leave_balances",
        help_text="Employee whose leave balance this represents",
    )
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="leave_balances",
        db_index=True,
        help_text="Company/tenant the balance belongs to",
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LeaveRequest.LEAVE_TYPE_CHOICES,
        help_text="Type of leave this balance applies to",
    )
    year = models.IntegerField(help_text="Calendar year for this leave balance")

    # Balance tracking
    total_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Total leave days allocated for this year",
    )
    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Days already used this year",
    )
    carried_over = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Days carried over from previous year",
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-year", "leave_type"]
        unique_together = ["employee", "leave_type", "year"]
        indexes = [
            models.Index(fields=["tenant", "year"]),
            models.Index(fields=["employee", "year"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(used_days__lte=models.F("total_days") + models.F("carried_over")),
                name="leave_balance_used_within_total",
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
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="leave_policies",
        db_index=True,
        help_text="Company/tenant this policy applies to",
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LeaveRequest.LEAVE_TYPE_CHOICES,
        help_text="Type of leave this policy applies to",
    )

    # Policy settings
    annual_entitlement = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Default annual leave entitlement in days",
    )
    max_consecutive_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        help_text="Maximum consecutive days allowed for this leave type",
    )
    notice_period_days = models.IntegerField(
        default=7,
        validators=[MinValueValidator(0)],
        help_text="Minimum notice period required in working days",
    )

    # Carry-over rules
    carry_over_allowed = models.BooleanField(
        default=True, help_text="Whether unused leave can be carried over to next year"
    )
    max_carry_over = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Maximum days that can be carried over (null = unlimited)",
    )

    # Auto-approval rules
    auto_approve_max_days = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Maximum days that can be auto-approved (null = no auto-approval)",
    )

    # Approval workflow
    approval_workflow = models.ForeignKey(
        "LeaveApprovalWorkflow",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_policies",
        help_text="Custom approval workflow for this leave type (null = use default workflow)",
    )

    # Policy status
    is_active = models.BooleanField(
        default=True, help_text="Whether this policy is currently active"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["leave_type"]
        unique_together = ["tenant", "leave_type"]
        indexes = [
            models.Index(fields=["tenant", "is_active"]),
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


class LeaveApproval(models.Model):
    """
    Model for tracking multi-level approval workflow for leave requests.
    Each leave request can have multiple approval steps.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    # Relationship to leave request
    leave_request = models.ForeignKey(
        "LeaveRequest",
        on_delete=models.CASCADE,
        related_name="approvals",
        help_text="Leave request being approved",
    )

    # Approval details
    approver = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="leave_approvals",
        help_text="User who performed this approval step",
    )

    APPROVAL_LEVEL_CHOICES = [
        ("department_manager", "Department Manager"),
        ("hr_manager", "HR Manager"),
        ("general_manager", "General Manager"),
    ]

    approval_level = models.CharField(
        max_length=20, choices=APPROVAL_LEVEL_CHOICES, help_text="Approval level in the workflow"
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Status of this approval step",
    )

    # Approval metadata
    approved_date = models.DateTimeField(
        null=True, blank=True, help_text="When this approval step was completed"
    )
    notes = models.TextField(blank=True, help_text="Notes or comments from approver")
    order = models.IntegerField(help_text="Order in approval sequence (1=first, 2=second, 3=final)")

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["leave_request", "order"]
        unique_together = ["leave_request", "approval_level"]
        indexes = [
            models.Index(fields=["leave_request", "status"]),
            models.Index(fields=["approver"]),
            models.Index(fields=["approval_level", "status"]),
        ]

    def save(self, *args, **kwargs):
        # Generate slug if not present
        if not self.slug:
            from django.utils.text import slugify

            base_slug = f"approval-{self.leave_request.id}-{self.approval_level}"
            self.slug = slugify(base_slug)

            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while LeaveApproval.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        # Set approved_date when status changes to approved/rejected
        if self.status in ["approved", "rejected"] and not self.approved_date:
            from django.utils import timezone

            self.approved_date = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.leave_request} - {self.get_approval_level_display()} ({self.get_status_display()})"

    @property
    def is_pending(self):
        """Check if this approval step is pending."""
        return self.status == "pending"

    @property
    def is_approved(self):
        """Check if this approval step is approved."""
        return self.status == "approved"

    @property
    def is_rejected(self):
        """Check if this approval step is rejected."""
        return self.status == "rejected"


class LeaveApprovalWorkflow(models.Model):
    """
    Simple approval workflow for leave requests.
    Defines the sequence of approval levels for different leave types.
    """

    APPROVAL_LEVEL_CHOICES = [
        ("department_manager", "Department Manager Only"),
        ("department_manager,hr_manager", "Department Manager → HR Manager"),
        (
            "department_manager,hr_manager,general_manager",
            "Department Manager → HR Manager → General Manager",
        ),
        ("hr_manager", "HR Manager Only"),
        ("hr_manager,general_manager", "HR Manager → General Manager"),
        ("general_manager", "General Manager Only"),
        ("custom", "Custom Approval Chain"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="leave_approval_workflows",
        help_text="Tenant this workflow belongs to",
    )

    name = models.CharField(
        max_length=100,
        help_text="Descriptive name for the workflow (e.g., 'Standard Approval', 'Executive Approval')",
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description of when to use this workflow",
    )

    # Simple approval chain - just select from predefined options
    approval_levels = models.CharField(
        max_length=100,
        choices=APPROVAL_LEVEL_CHOICES,
        default="department_manager",
        help_text="The sequence of approval levels required",
    )

    # Optional: Allow custom approval levels for advanced users
    custom_approvers = models.JSONField(
        null=True,
        blank=True,
        help_text="Custom approver configuration for 'custom' approval type",
    )

    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default workflow for the tenant",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this workflow is available for use",
    )

    # Audit fields
    created_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_leave_workflows",
        help_text="User who created this workflow",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["tenant", "name"]
        indexes = [
            models.Index(fields=["tenant", "is_default"]),
            models.Index(fields=["tenant", "is_active"]),
        ]

    def save(self, *args, **kwargs):
        # Generate slug if not present
        if not self.slug:
            from django.utils.text import slugify

            base_slug = f"workflow-{self.tenant.id}-{self.name}"
            self.slug = slugify(base_slug)

            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while LeaveApprovalWorkflow.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant.name} - {self.name}"

    @property
    def approval_level_list(self):
        """Get the approval levels as a list."""
        if self.approval_levels == "custom" and self.custom_approvers:
            # For custom workflows, return the custom approver roles
            if isinstance(self.custom_approvers, list):
                return [
                    approver.get("role", "")
                    for approver in self.custom_approvers
                    if approver.get("role")
                ]
        return self.approval_levels.split(",") if self.approval_levels else []

    @property
    def number_of_levels(self):
        """Get the number of approval levels."""
        return len(self.approval_level_list)

    def clean(self):
        """Validate workflow configuration."""
        if self.is_default:
            # Ensure only one default per tenant
            existing_default = LeaveApprovalWorkflow.objects.filter(
                tenant=self.tenant, is_default=True
            ).exclude(pk=self.pk)
            if existing_default.exists():
                raise ValidationError("Only one default workflow allowed per tenant.")

        # Validate custom approvers
        if self.approval_levels == "custom":
            if not self.custom_approvers:
                raise ValidationError(
                    "Custom approvers configuration is required when using custom approval chain."
                )
            if not isinstance(self.custom_approvers, list) or len(self.custom_approvers) == 0:
                raise ValidationError("Custom approvers must be a non-empty list.")
            for i, approver in enumerate(self.custom_approvers):
                if not isinstance(approver, dict):
                    raise ValidationError(f"Custom approver {i+1} must be a dictionary.")
                if not approver.get("role"):
                    raise ValidationError(f"Custom approver {i+1} must have a 'role' field.")
