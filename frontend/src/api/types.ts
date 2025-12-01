export interface LoginResponse {
  access: string;
  refresh: string;
  token_type: string;
  expires_in: number;
  user_id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  message: string;
}

export interface SignupResponse {
  access: string;
  refresh: string;
  token_type: string;
  expires_in: number;
  user_id: number;
  email: string;
  first_name: string;
  last_name: string;
  tenant: string;
  message: string;
}

export interface Client {
  id: string;
  slug: string;
  name: string;
  email: string;
  phone: string;
  status: string;
  tenant: number;
  tenant_name: string;
  projects_count: string;
  created_at: string;
  updated_at: string;
}

export interface CreateClientData {
  name: string;
  email: string;
  phone?: string;
  status: string;
  tenant: number;
}

export interface UpdateClientData {
  name?: string;
  email?: string;
  phone?: string;
  status?: string;
  tenant?: number;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  date_joined: string;
  organization?: string;
  job?: string;
}

export interface UserProfile {
  id: number;
  user: number;
  job_title: string;
  phone: string;
  linkedin_profile: string;
  employee_id: string;
  employee_number: string;
  tax_number: string;
  hire_date: string;
  street_address: string;
  city: string;
  state_province: string;
  postal_code: string;
  country: string;
  emergency_contact: string;
  emergency_phone: string;
  medical_aid_provider: string;
  medical_aid_plan: string;
  medical_aid_number: string;
  medical_conditions: string;
  allergies: string;
  medications: string;
  bank_name: string;
  account_number: string;
  branch_code: string;
  account_type: string;
  routing_number: string;
  swift_code: string;
  created_at: string;
  updated_at: string;
  // User fields
  first_name: string;
  last_name: string;
  email: string;
  is_active: boolean;
  date_joined: string;
  organization: string;
}

export interface UserTenant {
  id: number;
  user: number;
  user_email: string;
  user_first_name: string;
  user_last_name: string;
  tenant: number;
  tenant_name: string;
  is_owner: boolean;
  is_approved: boolean;
  role: string;
}

export interface Project {
  id: string;
  name: string;
  slug: string;
  client: number;
  client_name: string;
  status: string;
  priority: string;
  start_date: string;
  end_date: string;
  budget?: string;
  description?: string;
  tags?: string;
  team_members: number[];
  access_groups: number[];
  milestones_count: number;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface Milestone {
  id: string;
  slug: string;
  name: string;
  description?: string;
  status: string;
  planned_start?: string;
  actual_start?: string;
  due_date?: string;
  assignee?: number;
  progress: number;
  project: string;
  project_name: string;
  sprints_count: number;
  created_at: string;
}

export interface Sprint {
  id: string;
  slug: string;
  name: string;
  status: string;
  start_date?: string;
  end_date?: string;
  milestone: string;
  milestone_name?: string;
  tasks_count: number;
  progress: number;
  created_at: string;
}

export interface Task {
  id: string;
  slug: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  milestone: string;
  milestone_name: string;
  sprint?: string;
  sprint_name?: string;
  assignee?: number;
  start_date?: string;
  end_date?: string;
  estimated_hours?: number;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Leave Management Types
export interface LeaveApproval {
  id: string;
  slug: string;
  leave_request: string;
  approval_level: "department_manager" | "hr_manager" | "general_manager";
  level_display: string;
  approver: number;
  approver_name: string;
  status: "pending" | "approved" | "rejected";
  approved_date?: string;
  notes?: string;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface LeaveRequest {
  id: string;
  slug: string;
  employee: number;
  employee_name: string;
  tenant: number;
  tenant_name: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days_requested: number;
  reason: string;
  status: "pending_department_manager" | "pending_hr_manager" | "pending_general_manager" | "approved" | "rejected" | "cancelled" | "taken";
  applied_date: string;
  duration_display: string;
  current_approval_level: "department_manager" | "hr_manager" | "general_manager";
  next_approval_level: string;
  approval_notes?: string;
  final_approver?: string;
  workflow_status: LeaveWorkflowStatus;
  approval_history: LeaveApproval[];
  current_approver: string;
  can_approve: boolean;
  created_at: string;
  updated_at: string;
}

export interface LeaveBalance {
  id: string;
  slug: string;
  employee: number;
  employee_name: string;
  tenant: number;
  tenant_name: string;
  leave_type: string;
  year: number;
  total_days: number;
  used_days: number;
  carried_over: number;
  remaining_days: number;
  utilization_percentage: number;
  created_at: string;
  updated_at: string;
}

export interface LeavePolicy {
  id: string;
  slug: string;
  tenant: number;
  tenant_name: string;
  leave_type: string;
  annual_entitlement: number;
  max_consecutive_days: number;
  notice_period_days: number;
  carry_over_allowed: boolean;
  max_carry_over?: number;
  auto_approve_max_days?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateLeaveRequestData {
  leave_type: string;
  start_date: string;
  end_date: string;
  days_requested?: number;
  reason?: string;
  tenant?: number;
}

export interface ApproveLeaveRequestData {
  action: "approve" | "reject";
  notes?: string;
}

export interface LeaveApprovalAction {
  action: "approve" | "reject";
  notes?: string;
}

export interface WorkflowStep {
  level: string;
  level_display: string;
  approver?: string;
  status: string;
  approved_date?: string;
  notes?: string;
  order: number;
}

export interface LeaveWorkflowStatus {
  current_status: string;
  current_level: string;
  is_pending: boolean;
  is_approved: boolean;
  is_rejected: boolean;
  next_approver?: string;
  steps: WorkflowStep[];
  current_level: string;
  next_level?: string;
  is_completed: boolean;
  total_levels: number;
  completed_levels: number;
  pending_approvals: number;
  can_approve: boolean;
  current_approver?: string;
}

export interface CreateLeavePolicy {
  leave_type: string;
  annual_entitlement: number;
  max_consecutive_days: number;
  notice_period_days: number;
  carry_over_allowed: boolean;
  max_carry_over?: number;
  auto_approve_max_days?: number;
  is_active: boolean;
}
