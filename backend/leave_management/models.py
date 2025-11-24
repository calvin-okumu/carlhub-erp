import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def validate_approval_levels(value):
    """Validate that approval levels is a list with max 5 items."""
    if not isinstance(value, list):
        raise ValidationError("Approval levels must be a list.")
    if len(value) > 5:
        raise ValidationError("Maximum 5 approval levels allowed.")


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

    def get_approval_history(self):
        """Get the approval history for this leave request."""
        return self.approvals.all().order_by("order")

    def get_current_approver(self):
        """Get the current approver in the workflow."""
        # Find the first pending approval in order
        pending_approval = self.approvals.filter(status="pending").order_by("order").first()
        return pending_approval.approver if pending_approval else None

    @property
    def is_pending(self):
        """Check if the leave request is still pending approval."""
        return self.status.startswith("pending_")

    @property
    def is_approved(self):
        """Check if the leave request is approved."""
        return self.status == "approved"

    @property
    def is_rejected(self):
        """Check if the leave request is rejected."""
        return self.status == "rejected"

    class Meta:
        ordering = ["-applied_date"]
        indexes = [
            models.Index(fields=["employee", "status"]),
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["status", "current_approval_level"]),
        ]

    def save(self, *args, **kwargs):
        # Generate slug if not present
        if not self.slug:
            from django.utils.text import slugify

            base_slug = f"request-{self.employee.id}-{self.start_date}-{self.end_date}"
            self.slug = slugify(base_slug)

            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while LeaveRequest.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"


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

    # Approval workflow configuration
    approval_levels = models.JSONField(
        default=list,
        help_text="Configured approval levels for this policy (max 5 levels)",
        validators=[validate_approval_levels],
    )

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

    def get_effective_approval_levels(self):
        """Get the effective approval levels for this policy."""
        # If custom approval levels are configured, use them
        if self.approval_levels and len(self.approval_levels) > 0:
            return self.approval_levels

        # Otherwise, use the workflow if configured
        if self.approval_workflow:
            return self.approval_workflow.approval_level_list

        # Default: 1 level for HR
        return ["hr_manager"]

    @property
    def number_of_approval_levels(self):
        """Get the number of approval levels configured."""
        return len(self.get_effective_approval_levels())


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
    Configurable approval workflow for leave requests.
    Defines the sequence of approval levels for different leave types.
    """

    APPROVAL_LEVEL_CHOICES = [
        ("department_manager", "Department Manager"),
        ("hr_manager", "HR Manager"),
        ("general_manager", "General Manager"),
        ("tenant_owner", "Tenant Owner"),
        ("custom", "Custom Role"),
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

    # Configurable approval levels - maximum 5 levels
    approval_levels = models.JSONField(
        default=list,
        help_text="List of approval levels required (max 5 levels)",
        validators=[validate_approval_levels],
    )

    # Default number of levels for HR if not configured (1-5)
    default_hr_levels = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Default number of approval levels for HR (1-5)",
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
        if isinstance(self.approval_levels, list):
            return self.approval_levels
        return []

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

        # Validate approval levels
        if not isinstance(self.approval_levels, list):
            raise ValidationError("Approval levels must be a list.")
        if len(self.approval_levels) > 5:
            raise ValidationError("Maximum 5 approval levels allowed.")
        if len(self.approval_levels) == 0:
            raise ValidationError("At least one approval level is required.")

        # Validate each level
        valid_levels = [choice[0] for choice in self.APPROVAL_LEVEL_CHOICES]
        for level in self.approval_levels:
            if level not in valid_levels:
                raise ValidationError(f"Invalid approval level: {level}")


class LeaveSale(models.Model):
    """
    Model for employee leave sales - allowing employees to sell back unused leave days.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    # Relationships
    employee = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="leave_sales",
        help_text="Employee selling leave days",
    )
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="leave_sales",
        db_index=True,
        help_text="Company/tenant the sale belongs to",
    )

    # Sale details
    leave_type = models.CharField(
        max_length=20,
        choices=LeaveRequest.LEAVE_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="Type of leave being sold (set by HR during approval)",
    )
    days_to_sell = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.5")), MaxValueValidator(Decimal("365"))],
        help_text="Number of leave days to sell (set by HR during approval)",
    )
    sale_price_per_day = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Sale price per day in company currency (set by HR during approval)",
    )

    # Calculated total
    total_sale_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Total sale amount (calculated as days_to_sell * sale_price_per_day)",
    )

    # Status and workflow
    STATUS_CHOICES = [
        ("pending", "Pending Approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
        help_text="Current status of the leave sale request",
    )

    # Approval details
    approved_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leave_sales",
        help_text="User who approved this sale",
    )
    approved_date = models.DateTimeField(
        null=True, blank=True, help_text="When the sale was approved"
    )
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection if applicable")

    # Request metadata
    applied_date = models.DateTimeField(
        auto_now_add=True, help_text="When the sale request was submitted"
    )
    reason = models.TextField(blank=True, help_text="Employee's reason for selling leave")

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_date"]
        indexes = [
            models.Index(fields=["employee", "status"]),
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["status", "applied_date"]),
        ]

    def save(self, *args, **kwargs):
        # Calculate total amount if both price and days are set
        if self.sale_price_per_day is not None and self.days_to_sell is not None:
            self.total_sale_amount = self.days_to_sell * self.sale_price_per_day
        else:
            self.total_sale_amount = Decimal("0")

        # Generate slug if not present
        if not self.slug:
            from django.utils.text import slugify

            if self.applied_date:
                applied_date = self.applied_date
            else:
                applied_date = timezone.now()

            # Use defaults if leave_type/days not set yet
            leave_type = self.leave_type or "leave"
            days = self.days_to_sell or 0
            base_slug = f"sale-{self.employee.id}-{leave_type}-{days}-{applied_date.date()}"
            self.slug = slugify(base_slug)

            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while LeaveSale.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        # Set approved_date when status changes to approved
        if self.status in ["approved", "rejected"] and not self.approved_date:
            self.approved_date = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.days_to_sell} days {self.leave_type} sale"

    @property
    def is_pending(self):
        """Check if the sale request is pending."""
        return self.status == "pending"

    @property
    def is_approved(self):
        """Check if the sale request is approved."""
        return self.status == "approved"

    @property
    def is_rejected(self):
        """Check if the sale request is rejected."""
        return self.status == "rejected"

    @property
    def is_completed(self):
        """Check if the sale has been completed."""
        return self.status == "completed"

    def can_be_cancelled(self):
        """Check if the sale can still be cancelled."""
        return self.status in ["pending", "approved"]

    def complete_sale(self):
        """Mark the sale as completed and update leave balance."""
        if self.status != "approved":
            raise ValueError("Only approved sales can be completed")

        # Update leave balance - reduce available days
        try:
            balance = LeaveBalance.objects.get(
                employee=self.employee,
                tenant=self.tenant,
                leave_type=self.leave_type,
                year=self.applied_date.year,
            )
            # Check if sufficient balance
            if balance.remaining_days >= self.days_to_sell:
                balance.used_days += self.days_to_sell
                balance.save()
                self.status = "completed"
                self.save()
                return True
            else:
                raise ValueError("Insufficient leave balance")
        except LeaveBalance.DoesNotExist:
            raise ValueError("No leave balance found for this leave type") from None

    def cancel_sale(self):
        """Cancel the sale request."""
        if not self.can_be_cancelled():
            raise ValueError("Sale cannot be cancelled at this stage")
        self.status = "cancelled"
        self.save()
