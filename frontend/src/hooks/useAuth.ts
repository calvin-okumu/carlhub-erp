/**
 * frontend/src/hooks/useAuth.ts
 * ==============================
 * Central authentication & RBAC hook.
 *
 * Reads the session stored in localStorage under the key "user" and exposes:
 *   - The full session object
 *   - Role / ownership helpers
 *   - A `can(permission)` check backed by the access matrix in permissions.ts
 *
 * Usage:
 *   const { user, role, isOwner, can, isRole } = useAuth();
 *   if (can('create_projects')) { ... }
 *   if (isRole('HR Manager', 'General Manager')) { ... }
 */

'use client';

import { useMemo } from 'react';
import {
  type Permission,
  type Role,
  hasPermission,
  invitableRoles,
  isHROrAbove,
  isManagerOrAbove,
  isSeniorOrAbove,
  isTenantOwner,
  roleGte,
} from '@/utils/permissions';

// ---------------------------------------------------------------------------
// Session shape stored in localStorage after login
// ---------------------------------------------------------------------------
export interface Session {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  /** UserTenant.role — one of the five valid role strings */
  role: Role;
  /** UserTenant.is_owner */
  is_owner: boolean;
  /** UserTenant.is_approved */
  is_approved: boolean;
  /** Tenant UUID string */
  tenant: string | null;
  /** Tenant display name */
  tenant_name: string | null;
  /** Department name if assigned */
  department: string | null;
}

const DEFAULT_SESSION: Session = {
  id: 0,
  email: '',
  first_name: '',
  last_name: '',
  role: 'Employee',
  is_owner: false,
  is_approved: false,
  tenant: null,
  tenant_name: null,
  department: null,
};

// ---------------------------------------------------------------------------
// Storage helpers — exported so login/logout can call them directly
// ---------------------------------------------------------------------------

export function getSession(): Session {
  if (typeof window === 'undefined') return DEFAULT_SESSION;
  try {
    const raw = localStorage.getItem('user');
    if (!raw) return DEFAULT_SESSION;
    const parsed = JSON.parse(raw);
    // Back-fill defaults for any missing keys (old session format)
    return { ...DEFAULT_SESSION, ...parsed };
  } catch {
    return DEFAULT_SESSION;
  }
}

export function setSession(data: Partial<Session>): void {
  if (typeof window === 'undefined') return;
  const current = getSession();
  localStorage.setItem('user', JSON.stringify({ ...current, ...data }));
}

export function clearSession(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('user');
  localStorage.removeItem('access_token');
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useAuth() {
  // Read synchronously from localStorage — no async, no server fetching.
  // Components that need to re-render on auth change should use a context
  // provider wrapping AuthRefresh (already present in dashboard/layout.tsx).
  const session = useMemo(() => getSession(), []);
  const role = session.role;

  return {
    /** Full session object */
    user: session,

    /** The user's role string */
    role,

    /** Whether the user is the tenant owner */
    isOwner: session.is_owner,

    /** Whether the membership has been approved */
    isApproved: session.is_approved,

    /** Display name */
    displayName: session.first_name
      ? `${session.first_name} ${session.last_name}`.trim()
      : session.email,

    /** Check a specific permission against the access matrix */
    can: (permission: Permission) => hasPermission(role, permission),

    /** Check if the user's role is one of the given roles */
    isRole: (...roles: Role[]) => roles.includes(role),

    /** True if role is Department Manager or above */
    isManager: isManagerOrAbove(role),

    /** True if role is HR Manager or above */
    isHR: isHROrAbove(role),

    /** True if role is General Manager or above */
    isSenior: isSeniorOrAbove(role),

    /** True only for Tenant Owner */
    isTenantOwner: isTenantOwner(role),

    /** True if role >= minimum */
    roleGte: (minimum: Role) => roleGte(role, minimum),

    /** Roles this user may invite */
    invitableRoles: () => invitableRoles(role),
  };
}
