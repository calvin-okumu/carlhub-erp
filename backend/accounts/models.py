import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SoftDeleteManager(models.Manager):
    """
    Manager that excludes soft deleted objects by default.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteAllManager(models.Manager):
    """
    Manager that includes soft deleted objects.
    """

    def get_queryset(self):
        return super().get_queryset()


class SoftDeleteMixin(models.Model):
    """
    Mixin to add soft delete functionality to models.
    """

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteAllManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the instance by setting is_deleted=True and deleted_at.
        """
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=["is_deleted", "deleted_at"])

    def restore(self, using=None):
        """
        Restore a soft deleted instance by setting is_deleted=False and deleted_at=None.
        """

        self.is_deleted = False
        self.deleted_at = None
        self.save(using=using, update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the instance.
        """
        super().delete(using=using, keep_parents=keep_parents)


class CustomUserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("username", email)  # Set username to email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(SoftDeleteMixin, AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            base_slug = slugify(f"{self.first_name}-{self.last_name}")
            self.slug = base_slug
            # Ensure uniqueness
            counter = 1
            while CustomUser.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, unique=True, default="")
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ("1-10", "1-10 employees"),
            ("11-50", "11-50 employees"),
            ("51-200", "51-200 employees"),
            ("201-1000", "201-1000 employees"),
            ("1000+", "1000+ employees"),
        ],
    )
    default_currency = models.CharField(
        max_length=3,
        default="USD",
        choices=[
            ("USD", "US Dollar"),
            ("EUR", "Euro"),
            ("GBP", "British Pound"),
            ("JPY", "Japanese Yen"),
            ("CAD", "Canadian Dollar"),
            ("AUD", "Australian Dollar"),
            ("CHF", "Swiss Franc"),
            ("CNY", "Chinese Yuan"),
            ("INR", "Indian Rupee"),
            ("BRL", "Brazilian Real"),
            ("ZAR", "South African Rand"),
            ("KES", "Kenyan Shilling"),
        ],
        help_text="Default currency for invoices and payments",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who originally created this tenant during signup",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()  # Default manager

    def __str__(self):
        return self.name


class UserTenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tenant = models.ForeignKey("accounts.Tenant", on_delete=models.CASCADE, db_index=True)
    is_owner = models.BooleanField(default=False)
    is_approved = models.BooleanField(
        default=True
    )  # Default True for owners, False for invited members

    ROLE_CHOICES = [
        ("Employee", "Employee"),
        ("Department Manager", "Department Manager"),
        ("HR Manager", "HR Manager"),
        ("General Manager", "General Manager"),
        ("Tenant Owner", "Tenant Owner"),
    ]

    role = models.CharField(
        max_length=100,
        choices=ROLE_CHOICES,
        default="Employee",
        help_text="User role within the tenant",
    )

    # Department assignment
    department = models.ForeignKey(
        "accounts.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
        help_text="Department this user belongs to",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            self.slug = slugify(f"member-{self.user.email}-{self.tenant.name}")
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while UserTenant.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @classmethod
    def transfer_ownership(cls, tenant, from_user, to_user):
        """
        Transfer ownership from one user to another for a tenant.
        Ensures at least one owner remains.
        """
        if not isinstance(tenant, Tenant):
            raise ValueError("tenant must be a Tenant instance")
        if not isinstance(from_user, get_user_model()):
            raise ValueError("from_user must be a User instance")
        if not isinstance(to_user, get_user_model()):
            raise ValueError("to_user must be a User instance")

        # Get the UserTenant relationships
        try:
            from_user_tenant = cls.objects.get(user=from_user, tenant=tenant, is_owner=True)
        except cls.DoesNotExist:
            raise ValueError("from_user is not an owner of this tenant")

        try:
            to_user_tenant = cls.objects.get(user=to_user, tenant=tenant, is_approved=True)
        except cls.DoesNotExist:
            raise ValueError("to_user is not an approved member of this tenant")

        # Check if this would leave no owners
        owner_count = cls.objects.filter(tenant=tenant, is_owner=True).count()
        if owner_count <= 1:
            raise ValueError("Cannot transfer ownership: tenant must have at least one owner")

        # Perform the transfer
        from_user_tenant.is_owner = False
        from_user_tenant.role = "Employee"  # Downgrade role
        from_user_tenant.save()

        to_user_tenant.is_owner = True
        to_user_tenant.role = "Tenant Owner"  # Upgrade role
        to_user_tenant.save()

        return from_user_tenant, to_user_tenant

    @classmethod
    def ensure_minimum_owners(cls, tenant):
        """
        Ensure a tenant has at least one owner.
        If no owners exist, promote the first approved member to owner.
        """
        if not isinstance(tenant, Tenant):
            raise ValueError("tenant must be a Tenant instance")

        owners = cls.objects.filter(tenant=tenant, is_owner=True)
        if owners.exists():
            return  # Already has owners

        # Find an approved member to promote
        approved_members = (
            cls.objects.filter(tenant=tenant, is_approved=True)
            .exclude(user=tenant.created_by)
            .order_by("created_at")
        )

        if approved_members.exists():
            member = approved_members.first()
            member.is_owner = True
            member.role = "Tenant Owner"
            member.save()
            return member

        # If no approved members, promote the creator if they're still a member
        if tenant.created_by:
            try:
                creator_membership = cls.objects.get(
                    user=tenant.created_by, tenant=tenant, is_approved=True
                )
                creator_membership.is_owner = True
                creator_membership.role = "Tenant Owner"
                creator_membership.save()
                return creator_membership
            except cls.DoesNotExist:
                pass

        # Last resort: create a system owner (shouldn't happen in normal operation)
        raise ValueError("No eligible users to promote to owner")

    def __str__(self):
        return f"{self.user.email} - {self.tenant.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")

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
    country = models.CharField(max_length=100, blank=True, default="USA")

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
    account_type = models.CharField(
        max_length=20,
        choices=[
            ("checking", "Checking"),
            ("savings", "Savings"),
        ],
        blank=True,
    )
    routing_number = models.CharField(max_length=20, blank=True)
    swift_code = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Profile"


class EmployeeDocument(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document_file = models.FileField(upload_to="employee_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # File metadata
    file_size = models.PositiveIntegerField(default=0)
    file_type = models.CharField(max_length=10, blank=True, default="")

    # Security constraints
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES = [
        'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt',  # Documents
        'jpg', 'jpeg', 'png', 'gif', 'bmp',  # Images
        'xls', 'xlsx', 'csv', 'ods'  # Spreadsheets
    ]

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def clean(self):
        """Validate file security constraints"""
        if self.document_file and hasattr(self.document_file, 'size'):
            # Check file size
            if self.document_file.size > self.MAX_FILE_SIZE:
                raise ValidationError(f'File size cannot exceed {self.MAX_FILE_SIZE // (1024*1024)}MB')

            # Check file type
            if self.document_file.name:
                file_extension = self.document_file.name.split('.')[-1].lower()
                if file_extension not in self.ALLOWED_FILE_TYPES:
                    raise ValidationError(f'File type {file_extension} is not allowed. Allowed types: {", ".join(self.ALLOWED_FILE_TYPES)}')

    def save(self, *args, **kwargs):
        self.clean()
        if self.document_file and hasattr(self.document_file, 'size'):
            self.file_size = self.document_file.size
            self.file_type = self.document_file.name.split(".")[-1].lower()
        super().save(*args, **kwargs)


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField()
    tenant = models.ForeignKey("accounts.Tenant", on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    role = models.CharField(max_length=100, default="Employee")  # e.g., 'Employee', 'Manager'
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(
        default=False
    )  # Track if invitation email has been confirmed

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
        ("user_signup", "User Signup"),
        ("user_login", "User Login"),
        ("user_logout", "User Logout"),
        ("user_profile_update", "Profile Update"),
        ("user_password_change", "Password Change"),
        ("invitation_sent", "Invitation Sent"),
        ("invitation_confirmed", "Invitation Confirmed"),
        ("invitation_used", "Invitation Used"),
        ("invitation_cancelled", "Invitation Cancelled"),
        ("invitation_expired", "Invitation Expired"),
        ("member_approved", "Member Approved"),
        ("member_rejected", "Member Rejected"),
        ("role_created", "Role Created"),
        ("role_updated", "Role Updated"),
        ("role_assigned", "Role Assigned"),
        ("project_created", "Project Created"),
        ("bulk_invitation_started", "Bulk Invitation Started"),
        ("bulk_invitation_completed", "Bulk Invitation Completed"),
        ("security_failed_login", "Failed Login Attempt"),
        ("security_token_misuse", "Token Misuse"),
        ("admin_user_suspended", "User Suspended"),
        ("admin_user_activated", "User Activated"),
    ]

    RESOURCE_TYPE_CHOICES = [
        ("user", "User"),
        ("invitation", "Invitation"),
        ("role", "Role"),
        ("tenant", "Tenant"),
        ("profile", "User Profile"),
        ("bulk_invitation", "Bulk Invitation"),
    ]

    tenant = models.ForeignKey("accounts.Tenant", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    resource_id = models.CharField(
        max_length=255, null=True, blank=True
    )  # String reference to resource (UUID or other identifier)
    old_values = models.JSONField(null=True, blank=True)  # Previous state
    new_values = models.JSONField(null=True, blank=True)  # New state
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)  # Additional context

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["tenant", "timestamp"]),
            models.Index(fields=["user"]),
            models.Index(fields=["action"]),
            models.Index(fields=["resource_type", "resource_id"]),
        ]

    def __str__(self):
        user_info = f" by {self.user.email}" if self.user else ""
        return f"{self.get_action_display()} on {self.get_resource_type_display()}{user_info} at {self.timestamp}"


class CustomPermission(models.Model):
    """
    Custom permissions that can be created by admins
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=100,
        choices=[
            ("project", "Project Management"),
            ("leave", "Leave Management"),
            ("crm", "CRM"),
            ("finance", "Finance"),
            ("admin", "Administration"),
            ("custom", "Custom"),
        ],
        default="custom",
    )
    app_label = models.CharField(max_length=100, default="accounts")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            while CustomPermission.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category}: {self.name}"

    class Meta:
        ordering = ["category", "name"]
        indexes = [
            models.Index(fields=["created_by"]),
        ]


class PermissionGroup(models.Model):
    """
    Enhanced groups with custom permissions and metadata
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_system_group = models.BooleanField(default=False)  # Prevent deletion of system groups
    tenant = models.ForeignKey("accounts.Tenant", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_groups",
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="permission_groups"
    )
    custom_permissions = models.ManyToManyField(CustomPermission, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            while PermissionGroup.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"

    class Meta:
        ordering = ["tenant", "name"]
        unique_together = [["name", "tenant"]]


class Department(models.Model):
    """
    Model for organizing employees into departments with hierarchical management.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    name = models.CharField(max_length=100, help_text="Department name")
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.CASCADE,
        related_name="departments",
        db_index=True,
        help_text="Company/tenant this department belongs to",
    )

    # Management structure
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments",
        help_text="Department manager (typically Department Manager role)",
    )

    # Department details
    description = models.TextField(
        blank=True, help_text="Department description and responsibilities"
    )
    parent_department = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_departments",
        help_text="Parent department for hierarchical structure",
    )

    # Status and metadata
    is_active = models.BooleanField(
        default=True, help_text="Whether this department is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tenant", "name"]
        unique_together = ["name", "tenant"]
        indexes = [
            models.Index(fields=["tenant", "is_active"]),
            models.Index(fields=["manager"]),
            models.Index(fields=["parent_department"]),
        ]

    def save(self, *args, **kwargs):
        # Generate slug if not present
        if not self.slug:
            from django.utils.text import slugify

            base_slug = f"dept-{self.tenant.id}-{self.name}"
            self.slug = slugify(base_slug)

            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Department.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant.name}: {self.name}"

    @property
    def employee_count(self):
        """Get the number of employees in this department."""
        return UserTenant.objects.filter(department=self, is_approved=True).count()

    def get_all_sub_departments(self):
        """Get all sub-departments recursively."""
        sub_depts = list(self.sub_departments.all())
        for sub_dept in sub_depts[:]:  # Copy list to avoid modification during iteration
            sub_depts.extend(sub_dept.get_all_sub_departments())
        return sub_depts
