/**
 * frontend/src/utils/permissions.ts
 * ===================================
 * Single source of truth for frontend RBAC.
 *
 * This file mirrors accounts/rbac.py on the backend.  Keep the role names and
 * permission keys in sync when the access matrix changes.
 *
 * Usage:
 *   import { hasPermission, Role } from '@/utils/permissions';
 *   const canCreate = hasPermission(role, 'create_projects');
 */

// ---------------------------------------------------------------------------
// Role type — mirrors UserTenant.ROLE_CHOICES
// ---------------------------------------------------------------------------
export type Role =
  | 'Employee'
  | 'Department Manager'
  | 'HR Manager'
  | 'General Manager'
  | 'Tenant Owner';

export const ROLE_HIERARCHY: Role[] = [
  'Employee',
  'Department Manager',
  'HR Manager',
  'General Manager',
  'Tenant Owner',
];

// ---------------------------------------------------------------------------
// Permission keys
// ---------------------------------------------------------------------------
export type Permission =
  // Project Management
  | 'view_projects'
  | 'create_projects'
  | 'edit_projects'
  | 'delete_projects'
  | 'view_tasks'
  | 'create_tasks'
  | 'edit_own_tasks'
  | 'edit_tasks'
  | 'delete_tasks'
  | 'manage_milestones'
  | 'manage_sprints'
  // CRM
  | 'view_clients'
  | 'create_clients'
  | 'edit_clients'
  | 'delete_clients'
  // Finance
  | 'view_finance'
  | 'manage_finance'
  | 'delete_invoices'
  // Ticketing
  | 'view_tickets'
  | 'create_tickets'
  | 'edit_tickets'
  | 'delete_tickets'
  // Leave Management
  | 'view_own_leave'
  | 'create_leave'
  | 'view_all_leave'
  | 'approve_leave'
  | 'manage_leave_balances'
  | 'manage_leave_policies'
  // People / HR
  | 'view_own_profile'
  | 'edit_own_profile'
  | 'view_all_employees'
  | 'invite_members'
  | 'approve_members'
  | 'manage_departments'
  // Administration
  | 'view_audit_logs'
  | 'manage_permissions'
  | 'assign_admin'
  | 'manage_tenant';

// ---------------------------------------------------------------------------
// Access matrix — one Set<Permission> per role
// ---------------------------------------------------------------------------

const EMPLOYEE_PERMS: Set<Permission> = new Set([
  'view_projects', 'view_tasks', 'create_tasks', 'edit_own_tasks',
  'view_clients',
  'view_tickets', 'create_tickets',
  'view_own_leave', 'create_leave',
  'view_own_profile', 'edit_own_profile',
]);

const DEPT_MANAGER_PERMS: Set<Permission> = new Set([
  ...EMPLOYEE_PERMS,
  'create_projects', 'edit_projects',
  'edit_tasks', 'delete_tasks',
  'manage_milestones', 'manage_sprints',
  'create_clients', 'edit_clients',
  'edit_tickets',
  'view_all_leave', 'approve_leave',
  'view_all_employees',
  'manage_departments',
]);

const HR_MANAGER_PERMS: Set<Permission> = new Set([
  ...DEPT_MANAGER_PERMS,
  'manage_leave_balances', 'manage_leave_policies',
  'invite_members',
]);

const GENERAL_MANAGER_PERMS: Set<Permission> = new Set([
  ...HR_MANAGER_PERMS,
  'delete_projects',
  'delete_clients',
  'delete_tickets',
  'view_finance', 'manage_finance',
  'view_audit_logs',
]);

const TENANT_OWNER_PERMS: Set<Permission> = new Set([
  ...GENERAL_MANAGER_PERMS,
  'delete_invoices',
  'manage_permissions',
  'assign_admin',
  'approve_members',
  'manage_tenant',
]);

export const ACCESS_MATRIX: Record<Role, Set<Permission>> = {
  'Employee':           EMPLOYEE_PERMS,
  'Department Manager': DEPT_MANAGER_PERMS,
  'HR Manager':         HR_MANAGER_PERMS,
  'General Manager':    GENERAL_MANAGER_PERMS,
  'Tenant Owner':       TENANT_OWNER_PERMS,
};

// ---------------------------------------------------------------------------
// Helper functions
// ---------------------------------------------------------------------------

/**
 * Returns true if the given role has the specified permission.
 * Falls back to the Employee permission set for unknown/null roles.
 */
export function hasPermission(role: Role | string | null | undefined, permission: Permission): boolean {
  const normalizedRole = (role as Role) in ACCESS_MATRIX ? (role as Role) : 'Employee';
  return ACCESS_MATRIX[normalizedRole].has(permission);
}

/**
 * Returns true if role is at least as privileged as minimum.
 */
export function roleGte(role: Role | string | null | undefined, minimum: Role): boolean {
  const roleIdx = ROLE_HIERARCHY.indexOf(role as Role);
  const minIdx  = ROLE_HIERARCHY.indexOf(minimum);
  if (roleIdx === -1 || minIdx === -1) return false;
  return roleIdx >= minIdx;
}

/**
 * Returns true if role is Department Manager or above.
 */
export function isManagerOrAbove(role: Role | string | null | undefined): boolean {
  return roleGte(role, 'Department Manager');
}

/**
 * Returns true if role is HR Manager or above.
 */
export function isHROrAbove(role: Role | string | null | undefined): boolean {
  return roleGte(role, 'HR Manager');
}

/**
 * Returns true if role is General Manager or above.
 */
export function isSeniorOrAbove(role: Role | string | null | undefined): boolean {
  return roleGte(role, 'General Manager');
}

/**
 * Returns true only for Tenant Owner.
 */
export function isTenantOwner(role: Role | string | null | undefined): boolean {
  return role === 'Tenant Owner';
}

/**
 * Display label for a role (handles null gracefully).
 */
export function roleLabel(role: Role | string | null | undefined): string {
  return (role as string) || 'Employee';
}

/**
 * Returns the roles a given inviter may invite.
 * Tenant Owner can invite anyone; General Manager up to HR Manager; etc.
 */
export function invitableRoles(inviterRole: Role | string | null | undefined): Role[] {
  if (inviterRole === 'Tenant Owner') return [...ROLE_HIERARCHY];
  if (inviterRole === 'General Manager') return ['Employee', 'Department Manager', 'HR Manager'];
  if (inviterRole === 'HR Manager') return ['Employee', 'Department Manager'];
  return [];
}
