"""
accounts/signals.py
====================
Signal handlers for the accounts app.

Key responsibilities:
  1. Create UserProfile when a UserTenant is created/approved.
  2. Assign the correct Django auth Group whenever a UserTenant is created OR
     whenever its *role* changes — keeping group membership in sync with the
     access matrix defined in accounts/rbac.py.
"""

import logging

from django.contrib.auth.models import Group
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import UserProfile, UserTenant
from .rbac import get_group_for_role

logger = logging.getLogger('accounts')


# ---------------------------------------------------------------------------
# UserProfile creation
# ---------------------------------------------------------------------------

@receiver(post_save, sender=UserTenant)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for a UserTenant as soon as they are approved.

    Covers both owners (approved at creation) and invited members (approved
    later by an owner).
    """
    if instance.is_approved:
        UserProfile.objects.get_or_create(user=instance.user)


# ---------------------------------------------------------------------------
# Group assignment — fires on create AND role/approval changes
# ---------------------------------------------------------------------------

@receiver(pre_save, sender=UserTenant)
def capture_previous_role(sender, instance, **kwargs):
    """Store the old role on the instance before it is written to the DB.

    This lets sync_group_membership know which group to remove when a role
    upgrade or downgrade occurs.
    """
    if instance.pk:
        try:
            instance._previous_role = UserTenant.objects.filter(pk=instance.pk).values_list('role', flat=True).first()
        except Exception:
            instance._previous_role = None
    else:
        instance._previous_role = None


@receiver(post_save, sender=UserTenant)
def sync_group_membership(sender, instance, created, **kwargs):
    """Keep Django Group membership in sync with UserTenant.role.

    Rules:
    - If the user is not yet approved, do nothing (still a pending invite).
    - On creation (is_approved=True): add to the correct group.
    - On role change: remove from the old group, add to the new group.
    - When is_approved transitions to True: add to the correct group.
    """
    if not instance.is_approved:
        return

    new_group_name = get_group_for_role(instance.role)
    previous_role = getattr(instance, '_previous_role', None)

    # Remove from old group when role changes on an existing record
    if previous_role and previous_role != instance.role:
        old_group_name = get_group_for_role(previous_role)
        if old_group_name != new_group_name:
            try:
                old_group = Group.objects.get(name=old_group_name)
                instance.user.groups.remove(old_group)
                logger.info(
                    'RBAC: removed user %s from group "%s" (role %s → %s)',
                    instance.user.email, old_group_name, previous_role, instance.role,
                )
            except Group.DoesNotExist:
                logger.warning(
                    'RBAC: old group "%s" not found — run `manage.py setup_groups`',
                    old_group_name,
                )

    # Add to the new group (get_or_create keeps things working even if
    # setup_groups has not been run yet in this environment).
    new_group, group_created = Group.objects.get_or_create(name=new_group_name)
    if group_created:
        logger.warning(
            'RBAC: group "%s" was missing and was created on-the-fly. '
            'Run `python manage.py setup_groups` to populate its permissions.',
            new_group_name,
        )

    instance.user.groups.add(new_group)
    logger.info(
        'RBAC: user %s is now in group "%s" (role=%s)',
        instance.user.email, new_group_name, instance.role,
    )
