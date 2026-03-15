"""
accounts/tests_rbac.py
=======================
RBAC unit tests for the accounts app.

Tests cover:
- ROLE_GROUP_MAP maps every valid role to a group name
- role_gte / can_invite_role helpers
- IsTenantAdmin permission class with all five roles
- sync_group_membership signal assigns correct group on create and role change
- No 'Manager' string survives in any ROLE_CHOICES or ROLE_GROUP_MAP
"""

from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from accounts.models import CustomUser, Tenant, UserProfile, UserTenant
from accounts.permissions import IsTenantAdmin
from accounts.rbac import (
    MANAGER_ROLES,
    ROLE_DEPT_MANAGER,
    ROLE_EMPLOYEE,
    ROLE_GENERAL_MANAGER,
    ROLE_GROUP_MAP,
    ROLE_HR_MANAGER,
    ROLE_TENANT_OWNER,
    VALID_ROLES,
    can_invite_role,
    get_group_for_role,
    role_gte,
)


class RBACConstantsTests(TestCase):
    """Verify the constants in accounts/rbac.py are internally consistent."""

    def test_valid_roles_matches_role_choices(self):
        """Every entry in ROLE_GROUP_MAP must be a valid ROLE_CHOICES value."""
        for role in ROLE_GROUP_MAP:
            self.assertIn(role, VALID_ROLES, f"Role '{role}' is in ROLE_GROUP_MAP but not in VALID_ROLES")

    def test_no_legacy_manager_string(self):
        """The legacy 'Manager' string must NOT appear anywhere in RBAC constants."""
        self.assertNotIn('Manager', VALID_ROLES)
        self.assertNotIn('Manager', ROLE_GROUP_MAP)
        self.assertNotIn('Manager', MANAGER_ROLES)

    def test_all_five_roles_have_group_mapping(self):
        roles = [ROLE_EMPLOYEE, ROLE_DEPT_MANAGER, ROLE_HR_MANAGER, ROLE_GENERAL_MANAGER, ROLE_TENANT_OWNER]
        for role in roles:
            group_name = get_group_for_role(role)
            self.assertIsNotNone(group_name)
            self.assertNotEqual(group_name, '')

    def test_unknown_role_falls_back_to_employees(self):
        from accounts.rbac import GROUP_EMPLOYEES
        self.assertEqual(get_group_for_role('Manager'), GROUP_EMPLOYEES)
        self.assertEqual(get_group_for_role(''), GROUP_EMPLOYEES)
        self.assertEqual(get_group_for_role('nonexistent'), GROUP_EMPLOYEES)

    def test_role_gte(self):
        self.assertTrue(role_gte(ROLE_TENANT_OWNER, ROLE_EMPLOYEE))
        self.assertTrue(role_gte(ROLE_GENERAL_MANAGER, ROLE_HR_MANAGER))
        self.assertTrue(role_gte(ROLE_EMPLOYEE, ROLE_EMPLOYEE))
        self.assertFalse(role_gte(ROLE_EMPLOYEE, ROLE_DEPT_MANAGER))
        self.assertFalse(role_gte(ROLE_HR_MANAGER, ROLE_GENERAL_MANAGER))
        # Unknown role is always False
        self.assertFalse(role_gte('Manager', ROLE_EMPLOYEE))

    def test_can_invite_role(self):
        # HR Manager can invite up to Department Manager
        self.assertTrue(can_invite_role(ROLE_HR_MANAGER, ROLE_EMPLOYEE))
        self.assertTrue(can_invite_role(ROLE_HR_MANAGER, ROLE_DEPT_MANAGER))
        self.assertFalse(can_invite_role(ROLE_HR_MANAGER, ROLE_HR_MANAGER))
        self.assertFalse(can_invite_role(ROLE_HR_MANAGER, ROLE_TENANT_OWNER))
        # General Manager can invite up to HR Manager
        self.assertTrue(can_invite_role(ROLE_GENERAL_MANAGER, ROLE_HR_MANAGER))
        self.assertFalse(can_invite_role(ROLE_GENERAL_MANAGER, ROLE_GENERAL_MANAGER))
        # Tenant Owner can invite anyone
        self.assertTrue(can_invite_role(ROLE_TENANT_OWNER, ROLE_TENANT_OWNER))
        # Employee cannot invite at all
        self.assertFalse(can_invite_role(ROLE_EMPLOYEE, ROLE_EMPLOYEE))
        self.assertFalse(can_invite_role(ROLE_DEPT_MANAGER, ROLE_EMPLOYEE))


class SyncGroupMembershipSignalTests(TestCase):
    """Verify that sync_group_membership keeps Django Group membership current."""

    def setUp(self):
        # Pre-create the groups the signal expects (without running full setup_groups
        # which requires all app permissions to be migrated)
        from accounts.rbac import ALL_GROUP_NAMES
        for name in ALL_GROUP_NAMES:
            Group.objects.get_or_create(name=name)

        self.tenant = Tenant.objects.create(name='Test Tenant', domain='test.example.com')
        self.user = CustomUser.objects.create_user(
            username='signaltest@example.com',
            email='signaltest@example.com',
            password='testpass123',
            first_name='Signal',
            last_name='Test',
        )

    def _create_user_tenant(self, role, is_owner=False, is_approved=True):
        return UserTenant.objects.create(
            user=self.user,
            tenant=self.tenant,
            role=role,
            is_owner=is_owner,
            is_approved=is_approved,
        )

    def test_employee_gets_employees_group(self):
        self._create_user_tenant(ROLE_EMPLOYEE)
        group_names = list(self.user.groups.values_list('name', flat=True))
        self.assertIn('Employees', group_names)

    def test_tenant_owner_gets_tenant_owners_group(self):
        self._create_user_tenant(ROLE_TENANT_OWNER, is_owner=True)
        group_names = list(self.user.groups.values_list('name', flat=True))
        self.assertIn('Tenant Owners', group_names)

    def test_dept_manager_gets_dept_managers_group(self):
        self._create_user_tenant(ROLE_DEPT_MANAGER)
        group_names = list(self.user.groups.values_list('name', flat=True))
        self.assertIn('Department Managers', group_names)
        self.assertNotIn('Employees', group_names)

    def test_hr_manager_gets_hr_managers_group(self):
        self._create_user_tenant(ROLE_HR_MANAGER)
        group_names = list(self.user.groups.values_list('name', flat=True))
        self.assertIn('HR Managers', group_names)

    def test_general_manager_gets_general_managers_group(self):
        self._create_user_tenant(ROLE_GENERAL_MANAGER)
        group_names = list(self.user.groups.values_list('name', flat=True))
        self.assertIn('General Managers', group_names)

    def test_unapproved_user_gets_no_group(self):
        self._create_user_tenant(ROLE_EMPLOYEE, is_approved=False)
        group_names = list(self.user.groups.values_list('name', flat=True))
        self.assertEqual(group_names, [])

    def test_role_change_updates_group(self):
        """Changing role from Employee to HR Manager swaps groups."""
        ut = self._create_user_tenant(ROLE_EMPLOYEE)
        self.assertIn('Employees', list(self.user.groups.values_list('name', flat=True)))

        ut.role = ROLE_HR_MANAGER
        ut.save()

        group_names = list(self.user.groups.values_list('name', flat=True))
        self.assertIn('HR Managers', group_names)
        self.assertNotIn('Employees', group_names)

    def test_profile_created_on_approval(self):
        ut = self._create_user_tenant(ROLE_EMPLOYEE, is_approved=True)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())


class IsTenantAdminPermissionTests(TestCase):
    """Verify IsTenantAdmin allows the correct roles."""

    def setUp(self):
        from accounts.rbac import ALL_GROUP_NAMES
        for name in ALL_GROUP_NAMES:
            Group.objects.get_or_create(name=name)
        self.tenant = Tenant.objects.create(name='Perm Test Tenant', domain='permtest.example.com')
        self.factory = APIRequestFactory()

    def _make_user_with_role(self, role, is_owner=False):
        email = f'{role.lower().replace(" ", "")}@example.com'
        user = CustomUser.objects.create_user(
            username=email, email=email, password='pass', first_name='A', last_name='B'
        )
        UserTenant.objects.create(
            user=user, tenant=self.tenant, role=role, is_owner=is_owner, is_approved=True,
        )
        return user

    def _check_perm(self, user):
        request = self.factory.get('/')
        request.user = user
        perm = IsTenantAdmin()
        return perm.has_permission(request, None)

    def test_tenant_owner_is_admin(self):
        user = self._make_user_with_role(ROLE_TENANT_OWNER, is_owner=True)
        self.assertTrue(self._check_perm(user))

    def test_general_manager_is_admin(self):
        user = self._make_user_with_role(ROLE_GENERAL_MANAGER)
        self.assertTrue(self._check_perm(user))

    def test_hr_manager_is_admin(self):
        user = self._make_user_with_role(ROLE_HR_MANAGER)
        self.assertTrue(self._check_perm(user))

    def test_dept_manager_is_admin(self):
        user = self._make_user_with_role(ROLE_DEPT_MANAGER)
        self.assertTrue(self._check_perm(user))

    def test_employee_is_not_admin(self):
        user = self._make_user_with_role(ROLE_EMPLOYEE)
        self.assertFalse(self._check_perm(user))

    def test_superuser_is_always_admin(self):
        superuser = CustomUser.objects.create_superuser(
            username='super@example.com', email='super@example.com', password='pass'
        )
        self.assertTrue(self._check_perm(superuser))
