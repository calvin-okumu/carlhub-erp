from decimal import Decimal
from uuid import uuid4

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from saasCRM.currency import CURRENCY_CHOICES


class Customer(models.Model):
    """Customer/Prospect management for sales"""

    STATUS_CHOICES = [
        ("prospect", "Prospect"),
        ("qualified", "Qualified Lead"),
        ("proposal", "Proposal Sent"),
        ("negotiation", "In Negotiation"),
        ("won", "Won"),
        ("lost", "Lost"),
        ("inactive", "Inactive"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    # Basic info
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Enter a valid phone number.")],
    )

    # Sales qualification
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="prospect", db_index=True
    )
    lead_source = models.CharField(
        max_length=50,
        choices=[
            ("website", "Website"),
            ("referral", "Referral"),
            ("social_media", "Social Media"),
            ("cold_outreach", "Cold Outreach"),
            ("trade_show", "Trade Show"),
            ("advertising", "Advertising"),
            ("other", "Other"),
        ],
        blank=True,
        help_text="How did we acquire this lead?",
    )

    lead_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Lead qualification score (0-100)",
    )

    # Company details
    company_name = models.CharField(max_length=255, blank=True)
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

    # Contact info
    primary_contact = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=100, blank=True)

    # Sales tracking
    assigned_to = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_customers",
    )

    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Estimated deal value",
    )

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")

    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)

    # Communication tracking
    last_contact = models.DateTimeField(null=True, blank=True)
    next_followup = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    # Multi-tenancy
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="sales_customers",
        null=True,
        blank=True,
        db_index=True,
    )

    # Audit
    created_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_sales_customers",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["lead_score"]),
            models.Index(fields=["expected_close_date"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Customer.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def days_since_last_contact(self):
        """Calculate days since last contact"""
        if self.last_contact:
            return (timezone.now() - self.last_contact).days
        return None

    @property
    def days_until_expected_close(self):
        """Calculate days until expected close"""
        if self.expected_close_date:
            return (self.expected_close_date - timezone.now().date()).days
        return None


class Opportunity(models.Model):
    """Sales opportunity/pipeline management"""

    STAGE_CHOICES = [
        ("prospecting", "Prospecting"),
        ("qualification", "Qualification"),
        ("proposal", "Proposal"),
        ("negotiation", "Negotiation"),
        ("closed_won", "Closed Won"),
        ("closed_lost", "Closed Lost"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    # Relationships
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="opportunities")

    assigned_to = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_opportunities",
    )

    # Opportunity details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Financials
    value = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")

    probability = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Win probability percentage (0-100)",
    )

    # Pipeline
    stage = models.CharField(
        max_length=20, choices=STAGE_CHOICES, default="prospecting", db_index=True
    )

    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)

    # Competition
    competitors = models.TextField(blank=True)
    competitive_advantage = models.TextField(blank=True)

    # Requirements
    requirements = models.TextField(blank=True)
    pain_points = models.TextField(blank=True)

    # Next steps
    next_steps = models.TextField(blank=True)
    next_followup = models.DateTimeField(null=True, blank=True)

    # Multi-tenancy
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="opportunities",
        null=True,
        blank=True,
        db_index=True,
    )

    # Audit
    created_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_opportunities",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "stage"]),
            models.Index(fields=["customer", "stage"]),
            models.Index(fields=["assigned_to", "stage"]),
            models.Index(fields=["expected_close_date"]),
            models.Index(fields=["probability"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.customer.name}-{self.title}")
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Opportunity.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.customer.name} (${self.value})"

    @property
    def weighted_value(self):
        """Calculate weighted value based on probability"""
        return (self.value * self.probability) / 100

    @property
    def days_in_stage(self):
        """Calculate days in current stage"""
        return (timezone.now().date() - self.created_at.date()).days

    @property
    def is_overdue(self):
        """Check if opportunity is overdue"""
        if self.expected_close_date:
            return timezone.now().date() > self.expected_close_date
        return False


class SalesActivity(models.Model):
    """Track all sales activities and interactions"""

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

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    # Relationships
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="activities")

    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, null=True, blank=True, related_name="activities"
    )

    performed_by = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name="sales_activities"
    )

    # Activity details
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES, db_index=True)

    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Timing
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    # Outcome
    outcome = models.TextField(blank=True)
    next_action = models.TextField(blank=True)
    next_action_date = models.DateTimeField(null=True, blank=True)

    # Duration (for calls/meetings)
    duration_minutes = models.IntegerField(null=True, blank=True)

    # Multi-tenancy
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="sales_activities",
        null=True,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-completed_date", "-scheduled_date", "-created_at"]
        indexes = [
            models.Index(fields=["tenant", "activity_type"]),
            models.Index(fields=["customer", "activity_type"]),
            models.Index(fields=["opportunity", "activity_type"]),
            models.Index(fields=["performed_by", "activity_type"]),
            models.Index(fields=["scheduled_date"]),
            models.Index(fields=["completed_date"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.customer.name}"

    @property
    def is_completed(self):
        """Check if activity is completed"""
        return self.completed_date is not None

    @property
    def is_overdue(self):
        """Check if scheduled activity is overdue"""
        if self.scheduled_date and not self.is_completed:
            return timezone.now() > self.scheduled_date
        return False


class SalesTeam(models.Model):
    """Sales team and territory management"""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Team structure
    manager = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_sales_teams",
    )

    members = models.ManyToManyField("accounts.CustomUser", related_name="sales_teams", blank=True)

    # Territory/Region
    territory = models.CharField(max_length=100, blank=True)
    target_quota = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")

    # Performance tracking
    current_quota_progress = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    # Multi-tenancy
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="sales_teams",
        null=True,
        blank=True,
        db_index=True,
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant", "is_active"]),
            models.Index(fields=["manager"]),
            models.Index(fields=["territory"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.territory})"

    @property
    def quota_percentage(self):
        """Calculate quota completion percentage"""
        if self.target_quota > 0:
            return (self.current_quota_progress / self.target_quota) * 100
        return 0

    @property
    def member_count(self):
        """Get number of team members"""
        return self.members.count()
