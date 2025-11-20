// Export types
export type {
  Client,
  CreateClientData,
  LeaveBalance,
  LeavePolicy,
  LeaveRequest,
  LoginResponse,
  Milestone,
  PaginatedResponse,
  Project,
  SignupResponse,
  Sprint,
  Task,
  UpdateClientData,
  User,
  UserTenant,
} from "./types";

// Export auth functions
export { login, signup, confirmEmail, getInvitationDetails, resendInvitation, deleteInvitation } from "./auth";

// Export CRM functions
export {
  createClient,
  deleteClient,
  getClients,
  getUserTenants,
  updateClient,
} from "./crm";

// Export Project Management functions
export {
  assignTaskToSprint,
  createMilestone,
  createProject,
  createSprint,
  createTask,
  createTaskInSprint,
  deleteMilestone,
  deleteSprint,
  deleteTask,
  getMilestone,
  getMilestones,
  getProject,
  getProjects,
  getSprint,
  getSprints,
  getTask,
  getTasks,
  unassignTaskFromSprint,
  updateMilestone,
  updateSprint,
  updateTask,
} from "./project_mgmt";

// Export Leave Management functions
export {
  approveLeaveRequest,
  cancelLeaveRequest,
  createLeavePolicy,
  createLeaveRequest,
  deleteLeavePolicy,
  deleteLeaveRequest,
  getLeaveBalance,
  getLeaveBalances,
  getLeavePolicies,
  getLeavePolicy,
  getLeaveRequest,
  getLeaveRequests,
  patchLeavePolicy,
  rejectLeaveRequest,
  updateLeavePolicy,
  updateLeaveRequest,
} from "./leave";

// Export API base URL
export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

