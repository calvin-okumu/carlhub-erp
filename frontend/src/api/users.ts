import { User, UserTenant, UserProfile } from './types';
import { API_BASE } from './index';

// Type for API response that might contain nested arrays
interface ApiResponse {
  results?: UserTenant[];
  data?: UserTenant[];
  users?: UserTenant[];
  members?: UserTenant[];
  items?: UserTenant[];
  [key: string]: unknown; // For any other properties
}

export async function getUsers(token: string): Promise<User[]> {
  const url = `${API_BASE}/members/`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  let data: unknown;
  try {
    data = await response.json();
  } catch {
    throw new Error(`Members endpoint not available at ${url}: ${response.status} ${response.statusText}`);
  }

  if (!response.ok) {
    const errorData = data as {error?: string};
    throw new Error(errorData.error || `Failed to fetch members from ${url}: ${response.status} ${response.statusText}`);
  }

  // Handle different response formats
  let usersArray: UserTenant[] | undefined;
  if (Array.isArray(data)) {
    usersArray = data;
  } else if (data && typeof data === 'object') {
    // Check for common nested array patterns
    const possibleKeys = ['results', 'data', 'users', 'members', 'items'];
    for (const key of possibleKeys) {
      if (key in data && Array.isArray((data as ApiResponse)[key as keyof ApiResponse])) {
        usersArray = (data as ApiResponse)[key as keyof ApiResponse] as UserTenant[];
        break;
      }
    }
  }

  if (!usersArray) {
    console.error('Unexpected API response structure:', data);
    console.log('Full response data:', JSON.stringify(data, null, 2));
    throw new Error(`Expected an array of users or an object with a nested array ('results', 'data', 'users', 'members', 'items'), but got: ${typeof data}. Check console for full structure.`);
  }

  // Transform UserTenant[] to User[]
  return usersArray.map((ut: UserTenant) => ({
    id: ut.user,
    email: ut.user_email,
    first_name: ut.user_first_name,
    last_name: ut.user_last_name,
    is_active: true, // Assume active since they're members
    date_joined: '', // Not available in UserTenant
    organization: ut.tenant_name,
    job: ut.role,
  }));
}

export async function getUser(token: string, id: number): Promise<User> {
   // Since backend doesn't have /users/{id}, fetch all members and find the one
   const users = await getUsers(token);
   const user = users.find(u => u.id === id);
   if (!user) {
     throw new Error(`User with id ${id} not found`);
   }
   return user;
}

export async function getCurrentUser(token: string): Promise<User> {
    // Get user ID from localStorage or assume it's stored there
    const userStr = localStorage.getItem("user");
    if (!userStr) {
      throw new Error("No user found in localStorage");
    }
    const user = JSON.parse(userStr);
    return getUser(token, user.id);
}

export async function getUserProfile(token: string, id: number): Promise<UserProfile> {
  const url = `${API_BASE}/accounts/profile/`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch profile: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  // Transform backend data to match UserProfile type
  return {
    id: data.id,
    user: data.user,
    job_title: data.job_title || '',
    phone: data.phone || '',
    linkedin_profile: data.linkedin_profile || '',
    employee_id: data.employee_id || '',
    employee_number: data.employee_number || '',
    tax_number: data.tax_number || '',
    hire_date: data.hire_date || '',
    street_address: data.street_address || '',
    city: data.city || '',
    state_province: data.state_province || '',
    postal_code: data.postal_code || '',
    country: data.country || '',
    emergency_contact: data.emergency_contact || '',
    emergency_phone: data.emergency_phone || '',
    medical_aid_provider: data.medical_aid_provider || '',
    medical_aid_plan: data.medical_aid_plan || '',
    medical_aid_number: data.medical_aid_number || '',
    medical_conditions: data.medical_conditions || '',
    allergies: data.allergies || '',
    medications: data.medications || '',
    bank_name: data.bank_name || '',
    account_number: data.account_number || '',
    branch_code: data.branch_code || '',
    account_type: data.account_type || '',
    routing_number: data.routing_number || '',
    swift_code: data.swift_code || '',
    created_at: data.created_at || '',
    updated_at: data.updated_at || '',
    first_name: data.user_first_name || '',
    last_name: data.user_last_name || '',
    email: data.user_email || '',
    is_active: true,
    date_joined: data.user_date_joined || '',
    organization: data.tenant_name || '',
  };
}

export async function updateUserProfile(token: string, id: number, profileData: Partial<UserProfile>): Promise<UserProfile> {
  const url = `${API_BASE}/accounts/profile/`;
  const response = await fetch(url, {
    method: "PATCH",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(profileData),
  });

  if (!response.ok) {
    throw new Error(`Failed to update profile: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  // Return the updated profile
  return await getUserProfile(token, id);
}