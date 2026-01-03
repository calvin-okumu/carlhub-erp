"""
Accounting models for accounting service.
"""
from decimal import Decimal
from django.db import models
import uuid
from django.core.validators import MinValueValidator
from django.utils import timezone


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    invoice_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    tenant_id = models.UUIDField(db_index=True)
    client_id = models.UUIDField(db_index=True)
    project_id = models.UUIDField(null=True, blank=True)
    
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    created_by = models.UUIDField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['tenant_id', 'status']),
            models.Index(fields=['client_id', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]

    @property
    def total_amount(self):
        return self.amount + self.tax_amount - self.discount_amount
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ["paid", "cancelled"]:
            return timezone.now().date() > self.due_date
        return False
    
    def __str__(self):
        return f"Invoice {self.invoice_number or self.id}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("bank_transfer", "Bank Transfer"),
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
        ("cash", "Cash"),
        ("check", "Check"),
        ("online", "Online Payment"),
        ("other", "Other"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    payment_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    tenant_id = models.UUIDField(db_index=True)
    invoice_id = models.UUIDField(null=True, blank=True)
    client_id = models.UUIDField(db_index=True)
    
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="bank_transfer")
    
    paid_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    recorded_by = models.UUIDField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-paid_at']
        indexes = [
            models.Index(fields=['tenant_id', 'paid_at']),
            models.Index(fields=['invoice_id', 'paid_at']),
            models.Index(fields=['client_id', 'paid_at']),
        ]
    
    def __str__(self):
        return f"Payment {self.payment_reference or self.id} - {self.amount} {self.currency}"
