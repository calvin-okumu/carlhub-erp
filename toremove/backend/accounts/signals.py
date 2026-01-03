from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile, UserTenant


@receiver(post_save, sender=UserTenant)
def create_user_profile_based_on_role(sender, instance, created, **kwargs):
    """Create UserProfile based on user role and approval status"""
    if created:
        if instance.is_owner:
            # Create profile immediately for tenant owners
            UserProfile.objects.get_or_create(user=instance.user)
        # For non-owners, profile will be created when approved (see below)


@receiver(post_save, sender=UserTenant)
def create_profile_for_approved_member(sender, instance, **kwargs):
    """Create UserProfile when non-owner members are approved"""
    if not instance.is_owner and instance.is_approved:
        # Check if profile already exists (don't create duplicate)
        UserProfile.objects.get_or_create(user=instance.user)


@receiver(post_save, sender=UserTenant)
def assign_default_group(sender, instance, created, **kwargs):
    """Assign default group when UserTenant is created and approved"""
    if created and instance.is_approved:
        # Map role to group name
        group_name = {
            "Tenant Owner": "Tenant Owners",
            "Employee": "Employees",
            "Manager": "Project Managers",
        }.get(instance.role, "Employees")

        try:
            group = Group.objects.get(name=group_name)
            instance.user.groups.add(group)
        except Group.DoesNotExist:
            # Fallback: create group if it doesn't exist
            group, created = Group.objects.get_or_create(name=group_name)
            instance.user.groups.add(group)
