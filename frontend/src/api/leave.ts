import { apiCall } from "./api-wrapper";
import { API_BASE } from "./index";
import type {
  ApproveLeaveRequestData,
  CreateLeaveRequestData,
  LeaveBalance,
  LeavePolicy,
  LeaveRequest,
  PaginatedResponse,
} from "./types";

// Leave Requests API
export const getLeaveRequests = async (params?: {
  status?: string;
  leave_type?: string;
  employee?: number;
  approved_by?: number;
  page?: number;
  page_size?: number;
}): Promise<PaginatedResponse<LeaveRequest>> => {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
  }

  return await apiCall<PaginatedResponse<LeaveRequest>>(
    `${API_BASE}/leave/requests/?${searchParams}`,
    {
      method: "GET",
    },
  );
};

export const getLeaveRequest = async (id: string): Promise<LeaveRequest> => {
  return await apiCall<LeaveRequest>(`${API_BASE}/leave/requests/${id}/`, {
    method: "GET",
  });
};

export const createLeaveRequest = async (
  data: CreateLeaveRequestData,
): Promise<LeaveRequest> => {
  return await apiCall<LeaveRequest>(`${API_BASE}/leave/requests/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
};

export const updateLeaveRequest = async (
  id: string,
  data: Partial<CreateLeaveRequestData>,
): Promise<LeaveRequest> => {
  return await apiCall<LeaveRequest>(`${API_BASE}/leave/requests/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
};

export const deleteLeaveRequest = async (id: string): Promise<void> => {
  await apiCall<void>(`${API_BASE}/leave/requests/${id}/`, {
    method: "DELETE",
  });
};

export const approveLeaveRequest = async (
  slug: string,
  data?: ApproveLeaveRequestData,
): Promise<LeaveRequest> => {
  return await apiCall<LeaveRequest>(
    `${API_BASE}/leave/requests/${slug}/approve/`,
    {
      method: "POST",
      body: JSON.stringify(data || {}),
    },
  );
};

export const rejectLeaveRequest = async (
  slug: string,
  data?: ApproveLeaveRequestData,
): Promise<LeaveRequest> => {
  return await apiCall<LeaveRequest>(
    `${API_BASE}/leave/requests/${slug}/reject/`,
    {
      method: "POST",
      body: JSON.stringify(data || {}),
    },
  );
};

export const cancelLeaveRequest = async (slug: string): Promise<LeaveRequest> => {
  return await apiCall<LeaveRequest>(
    `${API_BASE}/leave/requests/${slug}/cancel/`,
    {
      method: "POST",
    },
  );
};

// Leave Balances API
export const getLeaveBalances = async (params?: {
  employee?: number;
  leave_type?: string;
  year?: number;
  page?: number;
  page_size?: number;
}): Promise<PaginatedResponse<LeaveBalance>> => {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
  }

  return await apiCall<PaginatedResponse<LeaveBalance>>(
    `${API_BASE}/leave/balances/?${searchParams}`,
    {
      method: "GET",
    },
  );
};

export const getLeaveBalance = async (id: string): Promise<LeaveBalance> => {
  return await apiCall<LeaveBalance>(`${API_BASE}/leave/balances/${id}/`, {
    method: "GET",
  });
};

// Leave Policies API
export const getLeavePolicies = async (params?: {
  leave_type?: string;
  is_active?: boolean;
  page?: number;
  page_size?: number;
}): Promise<PaginatedResponse<LeavePolicy>> => {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
  }

  return await apiCall<PaginatedResponse<LeavePolicy>>(
    `${API_BASE}/leave/policies/?${searchParams}`,
    {
      method: "GET",
    },
  );
};

export const getLeavePolicy = async (id: string): Promise<LeavePolicy> => {
  return await apiCall<LeavePolicy>(`${API_BASE}/leave/policies/${id}/`, {
    method: "GET",
  });
};

export const createLeavePolicy = async (data: {
  leave_type: string;
  annual_entitlement: number;
  max_consecutive_days: number;
  notice_period_days: number;
  carry_over_allowed: boolean;
  max_carry_over?: number;
  auto_approve_max_days?: number;
  is_active: boolean;
}): Promise<LeavePolicy> => {
  return await apiCall<LeavePolicy>(`${API_BASE}/leave/policies/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
};
export const updateLeavePolicy = async (
  slug: string,
  data: Partial<LeavePolicy>,
): Promise<LeavePolicy> => {
  return await apiCall<LeavePolicy>(`${API_BASE}/leave/policies/${slug}/`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
};
export const patchLeavePolicy = async (
  slug: string,
  data: Partial<LeavePolicy>,
): Promise<LeavePolicy> => {
  return await apiCall<LeavePolicy>(`${API_BASE}/leave/policies/${slug}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
};
export const deleteLeavePolicy = async (slug: string): Promise<void> => {
  await apiCall<void>(`${API_BASE}/leave/policies/${slug}/`, {
    method: "DELETE",
  });
};

