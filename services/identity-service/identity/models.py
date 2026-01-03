"""
Identity Service Models

This module contains the core models for the Identity Service microservice.
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom manager for User model"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User model for Identity Service"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_superuser = models.BooleanField(_('superuser status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), null=True, blank=True)

    # Tenant relationship
    tenant_id = models.UUIDField(_('tenant ID'), null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'identity_users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tenant_id']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the user's short name"""
        return self.first_name


class Tenant(models.Model):
    """Tenant model for multi-tenancy support"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('tenant name'), max_length=255, unique=True)
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    domain = models.CharField(_('domain'), max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    # Contact information
    address = models.TextField(_('address'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    website = models.URLField(_('website'), blank=True)

    # Business information
    industry = models.CharField(_('industry'), max_length=100, blank=True)
    company_size = models.CharField(
        _('company size'),
        max_length=50,
        blank=True,
        choices=[
            ('1-10', '1-10 employees'),
            ('11-50', '11-50 employees'),
            ('51-200', '51-200 employees'),
            ('201-1000', '201-1000 employees'),
            ('1000+', '1000+ employees'),
        ],
    )

    class Meta:
        db_table = 'identity_tenants'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['domain']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name


class UserSession(models.Model):
    """Model to track user sessions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(_('session key'), max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    expires_at = models.DateTimeField(_('expires at'))
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        db_table = 'identity_user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Session for {self.user.email}"

    @property
    def is_expired(self):
        """Check if the session has expired"""
        return timezone.now() > self.expires_at


class RefreshToken(models.Model):
    """Model to store refresh tokens"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(_('token'), max_length=255, unique=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    expires_at = models.DateTimeField(_('expires at'))
    is_active = models.BooleanField(_('active'), default=True)
    revoked_at = models.DateTimeField(_('revoked at'), null=True, blank=True)

    class Meta:
        db_table = 'identity_refresh_tokens'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Refresh token for {self.user.email}"

    @property
    def is_expired(self):
        """Check if the token has expired"""
        return timezone.now() > self.expires_at

    @property
    def is_revoked(self):
        """Check if the token has been revoked"""
        return self.revoked_at is not None

    def revoke(self):
        """Revoke the token"""
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save()
