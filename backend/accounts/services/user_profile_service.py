"""
User profile service for handling user profile operations.
"""

from typing import Any, Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..audit import AuditLogger, get_client_ip
from ..models import UserProfile, UserTenant

User = get_user_model()


class UserProfileService:
    """Service for managing user profiles."""

    @staticmethod
    def get_user_profile(user: User) -> UserProfile | None:
        """Get user profile for a given user."""
        try:
            return user.profile
        except UserProfile.DoesNotExist:
            return None

    @staticmethod
    def create_user_profile(user: User, **profile_data) -> UserProfile:
        """Create a new user profile."""
        if hasattr(user, "profile"):
            raise ValidationError("User already has a profile")

        profile = UserProfile.objects.create(user=user, **profile_data)

        # Log profile creation
        tenant = UserProfileService._get_user_tenant(user)
        if tenant:
            AuditLogger.log_event(
                action="profile_created",
                resource_type="user_profile",
                tenant=tenant,
                user=user,
                resource_id=str(user.id),
                new_values=profile_data,
                ip_address=None,  # No request context here
            )

        return profile

    @staticmethod
    def update_user_profile(user: User, profile_data: dict[str, Any], request=None) -> UserProfile:
        """Update user profile with audit logging."""
        profile = UserProfileService.get_user_profile(user)
        if not profile:
            raise ValidationError("User profile does not exist")

        # Store old values for audit
        old_data = {
            "job_title": profile.job_title,
            "phone": profile.phone,
            "linkedin_profile": profile.linkedin_profile,
            "employee_id": profile.employee_id,
            "street_address": profile.street_address,
            "city": profile.city,
            "country": profile.country,
        }

        # Update profile
        for field, value in profile_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)

        profile.updated_at = timezone.now()
        profile.save()

        # Get new values for audit
        new_data = {
            "job_title": profile.job_title,
            "phone": profile.phone,
            "linkedin_profile": profile.linkedin_profile,
            "employee_id": profile.employee_id,
            "street_address": profile.street_address,
            "city": profile.city,
            "country": profile.country,
        }

        # Log profile update
        tenant = UserProfileService._get_user_tenant(user)
        if tenant:
            AuditLogger.log_event(
                action="profile_updated",
                resource_type="user_profile",
                tenant=tenant,
                user=user,
                resource_id=str(user.id),
                old_values=old_data,
                new_values=new_data,
                ip_address=get_client_ip(request) if request else None,
            )

        return profile

    @staticmethod
    def get_or_create_profile(user: User) -> UserProfile:
        """Get existing profile or create a new one."""
        profile = UserProfileService.get_user_profile(user)
        if not profile:
            # Create profile for approved users
            try:
                user_tenant = UserTenant.objects.get(user=user, is_approved=True)
                profile = UserProfileService.create_user_profile(user)
            except UserTenant.DoesNotExist:
                # User not approved, don't create profile
                raise ValidationError("User is not approved for any tenant")

        return profile

    @staticmethod
    def _get_user_tenant(user: User) -> Optional["Tenant"]:
        """Get the tenant context for a user."""
        try:
            user_tenant = user.usertenants.filter(is_approved=True).first()
            return user_tenant.tenant if user_tenant else None
        except:
            return None

    @staticmethod
    def can_access_profile(user: User, target_user: User) -> bool:
        """Check if user can access target user's profile."""
        # Users can always access their own profile
        if user == target_user:
            return True

        # Superusers can access any profile
        if user.is_superuser:
            return True

        # Check if users are in the same tenant
        try:
            user_tenant = user.usertenants.filter(is_approved=True).first()
            target_tenant = target_user.usertenants.filter(is_approved=True).first()

            if user_tenant and target_tenant:
                return user_tenant.tenant == target_tenant.tenant
        except:
            pass

        return False
