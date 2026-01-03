from decimal import Decimal
from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from accounts.models import SoftDeleteMixin
from saasCRM.currency import CURRENCY_CHOICES


class Invoice(SoftDeleteMixin, models.Model):
    """Invoice model for financial billing and collection"""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    invoice_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="invoices",
        null=True,
        blank=True,
        db_index=True,
    )

    # Relationships to other apps
    client = models.ForeignKey(
        "project.Client", on_delete=models.CASCADE, related_name="invoices", db_index=True
    )
    project = models.ForeignKey(
        "project.Project", on_delete=models.SET_NULL, related_name="invoices", null=True, blank=True
    )

    # Financial details
    currency = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        choices=CURRENCY_CHOICES,
        help_text="Currency for this invoice",
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True, help_text="Payment terms and conditions")

    created_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_invoices",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["client", "status"]),
            models.Index(fields=["due_date", "status"]),
        ]

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

        # Generate invoice number if not provided
        if not self.invoice_number:
            # Simple invoice numbering: INV-{year}{month}-{sequential}
            today = timezone.now().date()
            year_month = today.strftime("%Y%m")
            # Count existing invoices for this month
            existing_count = Invoice.objects.filter(
                invoice_number__startswith=f"INV-{year_month}"
            ).count()
            self.invoice_number = f"INV-{year_month}-{existing_count + 1:03d}"

        # Set default currency from tenant if not provided
        if not self.currency:
            from saasCRM.currency import get_tenant_default_currency

            self.currency = get_tenant_default_currency(self.tenant)

        # Auto-set paid_at when status changes to paid
        if self.status == "paid" and not self.paid_at:
            self.paid_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        """Calculate total amount including tax and discount"""
        return self.amount + self.tax_amount - self.discount_amount

    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.due_date and self.status not in ["paid", "cancelled"]:
            return timezone.now().date() > self.due_date
        return False

    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0

    def __str__(self):
        return f"Invoice {self.invoice_number or self.id} - {self.client.name}"


class Payment(SoftDeleteMixin, models.Model):
    """Payment model for tracking financial collections"""

    PAYMENT_METHOD_CHOICES = [
        ("bank_transfer", "Bank Transfer"),
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
        ("cash", "Cash"),
        ("check", "Check"),
        ("online", "Online Payment"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    payment_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)

    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
        db_index=True,
    )

    # Relationships
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        db_index=True,
    )
    client = models.ForeignKey(
        "project.Client", on_delete=models.CASCADE, related_name="payments", db_index=True
    )

    # Payment details
    currency = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        choices=CURRENCY_CHOICES,
        help_text="Currency for this payment",
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default="bank_transfer"
    )

    # Status and dates
    paid_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    notes = models.TextField(blank=True)
    transaction_id = models.CharField(
        max_length=100, blank=True, help_text="External payment processor ID"
    )

    recorded_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_payments",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-paid_at"]
        indexes = [
            models.Index(fields=["tenant", "paid_at"]),
            models.Index(fields=["invoice", "paid_at"]),
            models.Index(fields=["client", "paid_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            invoice_id = self.invoice.id if self.invoice else "no-invoice"
            self.slug = slugify(f"payment-{invoice_id}-{self.amount}")
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Payment.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        # Generate payment reference if not provided
        if not self.payment_reference:
            today = timezone.now().date()
            year_month = today.strftime("%Y%m")
            existing_count = Payment.objects.filter(
                payment_reference__startswith=f"PAY-{year_month}"
            ).count()
            self.payment_reference = f"PAY-{year_month}-{existing_count + 1:03d}"

        # Set currency from invoice if not provided
        if not self.currency and self.invoice:
            self.currency = self.invoice.currency

        # Auto-set processed_at
        if not self.processed_at:
            self.processed_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.payment_reference or self.id} - {self.amount} {self.currency}"
