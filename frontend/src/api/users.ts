import { User, UserTenant, UserProfile } from './types';
import { API_BASE } from './index';
import { authFetch } from './client';

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
  const response = await authFetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
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

  // Transform UserTenant[] to User[], preserving RBAC fields
  return usersArray.map((ut: UserTenant) => ({
    id:          ut.user,
    email:       ut.user_email,
    first_name:  ut.user_first_name,
    last_name:   ut.user_last_name,
    is_active:   ut.is_approved,       // treat approved = active
    date_joined: '',                   // not available in UserTenant
    organization: ut.tenant_name,
    // RBAC fields — preserved as first-class properties
    role:        ut.role,
    is_owner:    ut.is_owner,
    is_approved: ut.is_approved,
    tenant:      ut.tenant,
    tenant_name: ut.tenant_name,
    // Backwards compat: job is still the role string for display components
    job:         ut.role,
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
  const response = await authFetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch profile');
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
  const response = await authFetch(url, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(profileData),
  });

  if (!response.ok) {
    throw new Error('Failed to update profile');
  }

  const data = await response.json();
  // Return the updated profile
  return await getUserProfile(token, id);
}

export async function createUser(token: string, userData: {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  job_title?: string;
  employee_id?: string;
  employee_number?: string;
  hire_date?: string;
  street_address?: string;
  city?: string;
  state_province?: string;
  postal_code?: string;
  country?: string;
  emergency_contact?: string;
  emergency_phone?: string;
  medical_aid_provider?: string;
  medical_aid_plan?: string;
  medical_aid_number?: string;
  medical_conditions?: string;
  allergies?: string;
  medications?: string;
  bank_name?: string;
  account_number?: string;
  branch_code?: string;
  account_type?: string;
  routing_number?: string;
  swift_code?: string;
  is_active?: boolean;
}): Promise<User> {
  // First, create the user account (assuming there's a user creation endpoint)
  // If not, this might need to be done through signup or another endpoint
  const createUserUrl = `${API_BASE}/users/`;
   const userResponse = await authFetch(createUserUrl, {
     method: "POST",
     headers: {
       Authorization: `Bearer ${token}`,
       "Content-Type": "application/json",
     },
     body: JSON.stringify({
       username: userData.email, // Use email as username for uniqueness
       first_name: userData.first_name,
       last_name: userData.last_name,
       email: userData.email,
       phone: userData.phone,
       job_title: userData.job_title,
       is_active: userData.is_active ?? true,
     }),
   });

  if (!userResponse.ok) {
    const errorData = await userResponse.json().catch(() => ({}));
    throw new Error(errorData.error || `Failed to create user: ${userResponse.status} ${userResponse.statusText}`);
  }

  const userDataResponse = await userResponse.json();

  // Then create/update the profile with additional employee details
  const profileData: Record<string, string> = {};

  // Only include fields that have actual values (not empty strings)
  if (userData.job_title?.trim()) profileData.job_title = userData.job_title.trim();
  if (userData.phone?.trim()) profileData.phone = userData.phone.trim();
  if (userData.employee_id?.trim()) profileData.employee_id = userData.employee_id.trim();
  if (userData.employee_number?.trim()) profileData.employee_number = userData.employee_number.trim();
  if (userData.hire_date?.trim()) profileData.hire_date = userData.hire_date.trim();
  if (userData.street_address?.trim()) profileData.street_address = userData.street_address.trim();
  if (userData.city?.trim()) profileData.city = userData.city.trim();
  if (userData.state_province?.trim()) profileData.state_province = userData.state_province.trim();
  if (userData.postal_code?.trim()) profileData.postal_code = userData.postal_code.trim();
  if (userData.country?.trim()) profileData.country = userData.country.trim();
  if (userData.emergency_contact?.trim()) profileData.emergency_contact = userData.emergency_contact.trim();
  if (userData.emergency_phone?.trim()) profileData.emergency_phone = userData.emergency_phone.trim();
  if (userData.medical_aid_provider?.trim()) profileData.medical_aid_provider = userData.medical_aid_provider.trim();
  if (userData.medical_aid_plan?.trim()) profileData.medical_aid_plan = userData.medical_aid_plan.trim();
  if (userData.medical_aid_number?.trim()) profileData.medical_aid_number = userData.medical_aid_number.trim();
  if (userData.medical_conditions?.trim()) profileData.medical_conditions = userData.medical_conditions.trim();
  if (userData.allergies?.trim()) profileData.allergies = userData.allergies.trim();
  if (userData.medications?.trim()) profileData.medications = userData.medications.trim();
  if (userData.bank_name?.trim()) profileData.bank_name = userData.bank_name.trim();
  if (userData.account_number?.trim()) profileData.account_number = userData.account_number.trim();
  if (userData.branch_code?.trim()) profileData.branch_code = userData.branch_code.trim();
  if (userData.account_type?.trim()) profileData.account_type = userData.account_type.trim();
  if (userData.routing_number?.trim()) profileData.routing_number = userData.routing_number.trim();
  if (userData.swift_code?.trim()) profileData.swift_code = userData.swift_code.trim();

  // Update profile if user was created successfully
  if (userDataResponse.id) {
    await updateUserProfile(token, userDataResponse.id, profileData);
  }

  // Return the created user
  return {
    id: userDataResponse.id,
    email: userData.email,
    first_name: userData.first_name,
    last_name: userData.last_name,
    is_active: userData.is_active ?? true,
    date_joined: userDataResponse.date_joined || '',
    organization: '', // Will be set when added to tenant
    job: userData.job_title || '',
  };
}

export async function updateUser(token: string, id: number, userData: Partial<{
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  job_title: string;
  employee_id: string;
  employee_number: string;
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
  is_active: boolean;
}>): Promise<User> {
   // Update user basic info
   const userUpdateData = {
     username: userData.email, // Update username to match email if email changed
     first_name: userData.first_name,
     last_name: userData.last_name,
     email: userData.email,
     phone: userData.phone,
     job_title: userData.job_title,
     is_active: userData.is_active,
   };

  // Remove undefined values
  Object.keys(userUpdateData).forEach(key => {
    if (userUpdateData[key as keyof typeof userUpdateData] === undefined) {
      delete userUpdateData[key as keyof typeof userUpdateData];
    }
  });

  if (Object.keys(userUpdateData).length > 0) {
    const userUrl = `${API_BASE}/users/${id}/`;
    const userResponse = await authFetch(userUrl, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userUpdateData),
    });

    if (!userResponse.ok) {
      const errorData = await userResponse.json().catch(() => ({}));
      throw new Error(errorData.error || `Failed to update user: ${userResponse.status} ${userResponse.statusText}`);
    }
  }

  // Update profile with employee details
  const profileUpdateData: Record<string, string> = {};

  // Only include fields that have actual values (not empty strings or undefined)
  if (userData.job_title?.trim()) profileUpdateData.job_title = userData.job_title.trim();
  if (userData.phone?.trim()) profileUpdateData.phone = userData.phone.trim();
  if (userData.employee_id?.trim()) profileUpdateData.employee_id = userData.employee_id.trim();
  if (userData.employee_number?.trim()) profileUpdateData.employee_number = userData.employee_number.trim();
  if (userData.hire_date?.trim()) profileUpdateData.hire_date = userData.hire_date.trim();
  if (userData.street_address?.trim()) profileUpdateData.street_address = userData.street_address.trim();
  if (userData.city?.trim()) profileUpdateData.city = userData.city.trim();
  if (userData.state_province?.trim()) profileUpdateData.state_province = userData.state_province.trim();
  if (userData.postal_code?.trim()) profileUpdateData.postal_code = userData.postal_code.trim();
  if (userData.country?.trim()) profileUpdateData.country = userData.country.trim();
  if (userData.emergency_contact?.trim()) profileUpdateData.emergency_contact = userData.emergency_contact.trim();
  if (userData.emergency_phone?.trim()) profileUpdateData.emergency_phone = userData.emergency_phone.trim();
  if (userData.medical_aid_provider?.trim()) profileUpdateData.medical_aid_provider = userData.medical_aid_provider.trim();
  if (userData.medical_aid_plan?.trim()) profileUpdateData.medical_aid_plan = userData.medical_aid_plan.trim();
  if (userData.medical_aid_number?.trim()) profileUpdateData.medical_aid_number = userData.medical_aid_number.trim();
  if (userData.medical_conditions?.trim()) profileUpdateData.medical_conditions = userData.medical_conditions.trim();
  if (userData.allergies?.trim()) profileUpdateData.allergies = userData.allergies.trim();
  if (userData.medications?.trim()) profileUpdateData.medications = userData.medications.trim();
  if (userData.bank_name?.trim()) profileUpdateData.bank_name = userData.bank_name.trim();
  if (userData.account_number?.trim()) profileUpdateData.account_number = userData.account_number.trim();
  if (userData.branch_code?.trim()) profileUpdateData.branch_code = userData.branch_code.trim();
  if (userData.account_type?.trim()) profileUpdateData.account_type = userData.account_type.trim();
  if (userData.routing_number?.trim()) profileUpdateData.routing_number = userData.routing_number.trim();
  if (userData.swift_code?.trim()) profileUpdateData.swift_code = userData.swift_code.trim();

  if (Object.keys(profileUpdateData).length > 0) {
    await updateUserProfile(token, id, profileUpdateData);
  }

  // Return updated user
  return await getUser(token, id);
}

export async function deleteUser(token: string, id: number): Promise<void> {
  const url = `${API_BASE}/users/${id}/`;
  const response = await authFetch(url, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `Failed to delete user: ${response.status} ${response.statusText}`);
  }
}
