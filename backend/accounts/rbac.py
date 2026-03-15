"""
accounts/rbac.py
================
Single source of truth for all RBAC constants in the DjangoCRM backend.

Every permission class, view, signal, and management command that needs to
reference roles, groups, or the access matrix should import from here instead
of hard-coding string literals.

Role hierarchy (lowest → highest privilege):
    Employee < Department Manager < HR Manager < General Manager < Tenant Owner
"""

# ---------------------------------------------------------------------------
# Role constants — must match UserTenant.ROLE_CHOICES exactly
# ---------------------------------------------------------------------------

ROLE_EMPLOYEE = 'Employee'
ROLE_DEPT_MANAGER = 'Department Manager'
ROLE_HR_MANAGER = 'HR Manager'
ROLE_GENERAL_MANAGER = 'General Manager'
ROLE_TENANT_OWNER = 'Tenant Owner'

# Ordered from lowest to highest privilege
ROLE_HIERARCHY = [
    ROLE_EMPLOYEE,
    ROLE_DEPT_MANAGER,
    ROLE_HR_MANAGER,
    ROLE_GENERAL_MANAGER,
    ROLE_TENANT_OWNER,
]

# All valid role strings
VALID_ROLES = set(ROLE_HIERARCHY)

# Convenience groupings
MANAGER_ROLES = [ROLE_DEPT_MANAGER, ROLE_HR_MANAGER, ROLE_GENERAL_MANAGER, ROLE_TENANT_OWNER]
SENIOR_ROLES = [ROLE_GENERAL_MANAGER, ROLE_TENANT_OWNER]
HR_AND_ABOVE = [ROLE_HR_MANAGER, ROLE_GENERAL_MANAGER, ROLE_TENANT_OWNER]
ADMIN_ROLES = [ROLE_TENANT_OWNER]

# Roles that can approve leave (any level)
LEAVE_APPROVER_ROLES = [ROLE_DEPT_MANAGER, ROLE_HR_MANAGER, ROLE_GENERAL_MANAGER, ROLE_TENANT_OWNER]

# Roles that can invite new members
INVITER_ROLES = [ROLE_HR_MANAGER, ROLE_GENERAL_MANAGER, ROLE_TENANT_OWNER]

# Maximum role a given role can invite (cannot invite higher than yourself)
INVITE_CEILING = {
    ROLE_HR_MANAGER:      ROLE_DEPT_MANAGER,
    ROLE_GENERAL_MANAGER: ROLE_HR_MANAGER,
    ROLE_TENANT_OWNER:    ROLE_TENANT_OWNER,
}

# ---------------------------------------------------------------------------
# Django Group names — must match what setup_groups.py creates
# ---------------------------------------------------------------------------

GROUP_TENANT_OWNERS = 'Tenant Owners'
GROUP_GENERAL_MANAGERS = 'General Managers'
GROUP_HR_MANAGERS = 'HR Managers'
GROUP_DEPT_MANAGERS = 'Department Managers'
GROUP_PROJECT_MANAGERS = 'Project Managers'   # kept for backwards-compat; mapped from Dept Manager
GROUP_EMPLOYEES = 'Employees'

# Canonical mapping: UserTenant.role  →  Django Group name
ROLE_GROUP_MAP = {
    ROLE_TENANT_OWNER:    GROUP_TENANT_OWNERS,
    ROLE_GENERAL_MANAGER: GROUP_GENERAL_MANAGERS,
    ROLE_HR_MANAGER:      GROUP_HR_MANAGERS,
    ROLE_DEPT_MANAGER:    GROUP_DEPT_MANAGERS,
    ROLE_EMPLOYEE:        GROUP_EMPLOYEES,
}

# All group names created by setup_groups
ALL_GROUP_NAMES = list(ROLE_GROUP_MAP.values())

# ---------------------------------------------------------------------------
# Helper functions used in permission classes and views
# ---------------------------------------------------------------------------


def get_group_for_role(role: str) -> str:
    """Return the Django Group name for a given role string.

    Falls back to GROUP_EMPLOYEES for any unrecognised / legacy role value.
    """
    return ROLE_GROUP_MAP.get(role, GROUP_EMPLOYEES)


def role_gte(role: str, minimum: str) -> bool:
    """Return True if *role* is at least as privileged as *minimum*.

    Examples::
        role_gte('General Manager', 'HR Manager')   → True
        role_gte('Employee', 'Department Manager')  → False
    """
    try:
        return ROLE_HIERARCHY.index(role) >= ROLE_HIERARCHY.index(minimum)
    except ValueError:
        return False


def is_manager_or_above(role: str) -> bool:
    """Return True for Department Manager and above."""
    return role_gte(role, ROLE_DEPT_MANAGER)


def is_hr_or_above(role: str) -> bool:
    """Return True for HR Manager and above."""
    return role_gte(role, ROLE_HR_MANAGER)


def is_senior_or_above(role: str) -> bool:
    """Return True for General Manager and above."""
    return role_gte(role, ROLE_GENERAL_MANAGER)


def is_owner(role: str) -> bool:
    """Return True only for Tenant Owner."""
    return role == ROLE_TENANT_OWNER


def can_invite_role(inviter_role: str, target_role: str) -> bool:
    """Return True if a user with *inviter_role* is allowed to invite *target_role*.

    Rules:
    - Only HR Manager and above can send invitations at all.
    - You cannot invite someone to a role higher than your own invite ceiling.
    """
    if inviter_role not in INVITE_CEILING:
        return False
    ceiling = INVITE_CEILING[inviter_role]
    return role_gte(ceiling, target_role)
