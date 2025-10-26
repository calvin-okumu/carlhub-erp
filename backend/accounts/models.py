import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)  # Set username to email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, unique=True, default='')
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True, choices=[
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-1000', '201-1000 employees'),
        ('1000+', '1000+ employees'),
    ])
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='User who originally created this tenant during signup'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserTenant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tenant = models.ForeignKey('accounts.Tenant', on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)  # Default True for owners, False for invited members
    role = models.CharField(max_length=100, default='Employee')

    def __str__(self):
        return f"{self.user.email} - {self.tenant.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')

    # Basic Info (extends CustomUser)
    job_title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin_profile = models.URLField(blank=True)

    # Employee Info
    employee_id = models.CharField(max_length=50, blank=True)
    employee_number = models.CharField(max_length=50, blank=True)
    tax_number = models.CharField(max_length=50, blank=True)
    hire_date = models.DateField(null=True, blank=True)

    # Address Info
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default='USA')

    # Emergency & Medical Info
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    medical_aid_provider = models.CharField(max_length=100, blank=True)
    medical_aid_plan = models.CharField(max_length=100, blank=True)
    medical_aid_number = models.CharField(max_length=50, blank=True)
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    medications = models.TextField(blank=True)

    # Banking Info
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    branch_code = models.CharField(max_length=20, blank=True)
    account_type = models.CharField(max_length=20, choices=[
        ('checking', 'Checking'),
        ('savings', 'Savings'),
    ], blank=True)
    routing_number = models.CharField(max_length=20, blank=True)
    swift_code = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Profile"


class EmployeeDocument(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document_file = models.FileField(upload_to='employee_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # File metadata
    file_size = models.PositiveIntegerField(default=0)
    file_type = models.CharField(max_length=10, blank=True, default='')

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def save(self, *args, **kwargs):
        if self.document_file:
            self.file_size = self.document_file.size
            self.file_type = self.document_file.name.split('.')[-1].lower()
        super().save(*args, **kwargs)


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField()
    tenant = models.ForeignKey('accounts.Tenant', on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    role = models.CharField(max_length=100, default='Employee')  # e.g., 'Employee', 'Manager'
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)  # Track if invitation email has been confirmed

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(f"invite-{self.email}")
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Invitation.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invite {self.email} to {self.tenant.name}"

    def is_expired(self):
        """Check if the invitation has expired."""
        from django.utils import timezone
        return timezone.now() > self.expires_at


class AuditLog(models.Model):
    """
    Comprehensive audit logging for user lifecycle and security events.
    """
    ACTION_CHOICES = [
        ('user_signup', 'User Signup'),
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('user_profile_update', 'Profile Update'),
        ('user_password_change', 'Password Change'),
        ('invitation_sent', 'Invitation Sent'),
        ('invitation_confirmed', 'Invitation Confirmed'),
        ('invitation_used', 'Invitation Used'),
        ('invitation_cancelled', 'Invitation Cancelled'),
        ('invitation_expired', 'Invitation Expired'),
        ('member_approved', 'Member Approved'),
        ('member_rejected', 'Member Rejected'),
        ('role_created', 'Role Created'),
        ('role_updated', 'Role Updated'),
        ('role_assigned', 'Role Assigned'),
        ('project_created', 'Project Created'),
        ('bulk_invitation_started', 'Bulk Invitation Started'),
        ('bulk_invitation_completed', 'Bulk Invitation Completed'),
        ('security_failed_login', 'Failed Login Attempt'),
        ('security_token_misuse', 'Token Misuse'),
        ('admin_user_suspended', 'User Suspended'),
        ('admin_user_activated', 'User Activated'),
    ]

    RESOURCE_TYPE_CHOICES = [
        ('user', 'User'),
        ('invitation', 'Invitation'),
        ('role', 'Role'),
        ('tenant', 'Tenant'),
        ('profile', 'User Profile'),
        ('bulk_invitation', 'Bulk Invitation'),
    ]

    tenant = models.ForeignKey('accounts.Tenant', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    resource_id = models.CharField(max_length=255, null=True, blank=True)  # String reference to resource (UUID or other identifier)
    old_values = models.JSONField(null=True, blank=True)  # Previous state
    new_values = models.JSONField(null=True, blank=True)  # New state
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)  # Additional context

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['tenant', 'timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]

    def __str__(self):
        user_info = f" by {self.user.email}" if self.user else ""
        return f"{self.get_action_display()} on {self.get_resource_type_display()}{user_info} at {self.timestamp}"
