"""
HR models for HR service.
"""
from decimal import Decimal
import uuid
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class LeaveRequest(models.Model):
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
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    employee_id = models.UUIDField(db_index=True)
    tenant_id = models.UUIDField(db_index=True)
    
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.5")), MaxValueValidator(Decimal("365"))],
    )
    reason = models.TextField(blank=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending_department_manager")
    current_approval_level = models.CharField(
        max_length=20,
        choices=(
            ("department_manager", "Department Manager"),
            ("hr_manager", "HR Manager"),
            ("general_manager", "General Manager"),
        ),
        default="department_manager",
    )
    applied_date = models.DateTimeField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_date"]
        indexes = [
            models.Index(fields=["employee_id", "status"]),
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["status", "current_approval_level"]),
        ]
    
    def __str__(self):
        return f"Leave Request - {self.employee_id} ({self.get_leave_type_display()})"


class LeaveBalance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    employee_id = models.UUIDField(db_index=True)
    tenant_id = models.UUIDField(db_index=True)
    
    leave_type = models.CharField(max_length=20, choices=LeaveRequest.LEAVE_TYPE_CHOICES)
    year = models.IntegerField()
    
    total_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0"))],
    )
    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    carried_over = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-year", "leave_type"]
        unique_together = ["employee_id", "leave_type", "year"]
        indexes = [
            models.Index(fields=["tenant_id", "year"]),
            models.Index(fields=["employee_id", "year"]),
        ]
    
    @property
    def remaining_days(self):
        return self.total_days + self.carried_over - self.used_days
    
    def __str__(self):
        return f"Balance - {self.employee_id} ({self.leave_type} {self.year})"


class LeaveApproval(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    leave_request_id = models.UUIDField(db_index=True)
    approver_id = models.UUIDField(db_index=True)
    
    APPROVAL_LEVEL_CHOICES = [
        ("department_manager", "Department Manager"),
        ("hr_manager", "HR Manager"),
        ("general_manager", "General Manager"),
    ]
    
    approval_level = models.CharField(max_length=20, choices=APPROVAL_LEVEL_CHOICES)
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    approved_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    order = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["leave_request_id", "order"]
        indexes = [
            models.Index(fields=["leave_request_id", "status"]),
            models.Index(fields=["approver_id"]),
        ]
    
    def __str__(self):
        return f"Approval - {self.get_approval_level_display()} ({self.get_status_display()})"
