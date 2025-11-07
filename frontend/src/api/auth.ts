import { LoginResponse, SignupResponse } from './types';
import { API_BASE } from './index';

export async function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/login/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Login failed");
  }

  return data;
}

export async function signup(
  email: string,
  password: string,
  first_name: string,
  last_name: string,
  company_name: string,
): Promise<SignupResponse> {
  const response = await fetch(`${API_BASE}/signup/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password, first_name, last_name, company_name }),
  });

  const data = await response.json();

  if (!response.ok) {
    let errorMessage = "Signup failed";
    if (typeof data === "object" && data !== null) {
      if (data.error) {
        errorMessage = data.error;
      } else {
        // Handle DRF field errors
        const errors = Object.values(data).flat() as string[];
        errorMessage = errors.join(" ");
      }
    }
    throw new Error(errorMessage);
  }

  return data;
}

export async function confirmEmail(token: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/confirm-invitation/?token=${encodeURIComponent(token)}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to confirm email");
  }

  return data;
}

export async function changePassword(token: string, currentPassword: string, newPassword: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/change-password/`, {
    method: "POST",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to change password");
  }

  return data;
}