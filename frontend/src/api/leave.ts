import { API_BASE } from "./index";
import type {
  LeaveRequest,
  LeaveBalance,
  LeavePolicy,
  CreateLeaveRequestData,
  ApproveLeaveRequestData,
  PaginatedResponse
} from "./types";

// Leave Requests API
export const getLeaveRequests = async (
  params?: {
    status?: string;
    leave_type?: string;
    employee?: number;
    approved_by?: number;
    page?: number;
    page_size?: number;
  }
): Promise<PaginatedResponse<LeaveRequest>> => {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
  }

  const response = await fetch(`${API_BASE}/leave/requests/?${searchParams}`, {
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch leave requests');
  }

  return response.json();
};

export const getLeaveRequest = async (id: string): Promise<LeaveRequest> => {
  const response = await fetch(`${API_BASE}/leave/requests/${id}/`, {
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch leave request');
  }

  return response.json();
};

export const createLeaveRequest = async (data: CreateLeaveRequestData): Promise<LeaveRequest> => {
  const response = await fetch(`${API_BASE}/leave/requests/`, {
    method: "POST",
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const errorMessage = errorData.detail || errorData.error || errorData.non_field_errors?.[0] || 'Failed to create leave request';
    throw new Error(errorMessage);
  }

  return response.json();
};

export const updateLeaveRequest = async (id: string, data: Partial<CreateLeaveRequestData>): Promise<LeaveRequest> => {
  const response = await fetch(`${API_BASE}/leave/requests/${id}/`, {
    method: "PATCH",
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Failed to update leave request');
  }

  return response.json();
};

export const deleteLeaveRequest = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/leave/requests/${id}/`, {
    method: "DELETE",
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to delete leave request');
  }
};

export const approveLeaveRequest = async (id: string, data?: ApproveLeaveRequestData): Promise<LeaveRequest> => {
  const response = await fetch(`${API_BASE}/leave/requests/${id}/approve/`, {
    method: "POST",
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data || {}),
  });

  if (!response.ok) {
    throw new Error('Failed to approve leave request');
  }

  return response.json();
};

export const rejectLeaveRequest = async (id: string, data?: ApproveLeaveRequestData): Promise<LeaveRequest> => {
  const response = await fetch(`${API_BASE}/leave/requests/${id}/reject/`, {
    method: "POST",
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data || {}),
  });

  if (!response.ok) {
    throw new Error('Failed to reject leave request');
  }

  return response.json();
};

export const cancelLeaveRequest = async (id: string): Promise<LeaveRequest> => {
  const response = await fetch(`${API_BASE}/leave/requests/${id}/cancel/`, {
    method: "POST",
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to cancel leave request');
  }

  return response.json();
};

// Leave Balances API
export const getLeaveBalances = async (
  params?: {
    employee?: number;
    leave_type?: string;
    year?: number;
    page?: number;
    page_size?: number;
  }
): Promise<PaginatedResponse<LeaveBalance>> => {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
  }

  const response = await fetch(`${API_BASE}/leave/balances/?${searchParams}`, {
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch leave balances');
  }

  return response.json();
};

export const getLeaveBalance = async (id: string): Promise<LeaveBalance> => {
  const response = await fetch(`${API_BASE}/leave/balances/${id}/`, {
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch leave balance');
  }

  return response.json();
};

// Leave Policies API
export const getLeavePolicies = async (
  params?: {
    leave_type?: string;
    is_active?: boolean;
    page?: number;
    page_size?: number;
  }
): Promise<PaginatedResponse<LeavePolicy>> => {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
  }

  const response = await fetch(`${API_BASE}/leave/policies/?${searchParams}`, {
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch leave policies');
  }

  return response.json();
};

export const getLeavePolicy = async (id: string): Promise<LeavePolicy> => {
  const response = await fetch(`${API_BASE}/leave/policies/${id}/`, {
    headers: {
      'Authorization': `Token ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch leave policy');
  }

  return response.json();
};