import { API_BASE } from "./index";
import { LoginResponse, SignupResponse } from "./types";

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
  company_name?: string,
  invitation_token?: string,
): Promise<SignupResponse> {
  const body: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    invitation_token?: string;
    company_name?: string;
  } = { email, password, first_name, last_name };
  if (invitation_token) {
    body.invitation_token = invitation_token;
  } else {
    body.company_name = company_name;
  }

  const response = await fetch(`${API_BASE}/signup/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
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

export async function confirmEmail(
  token: string,
): Promise<{ message: string }> {
  const response = await fetch(
    `${API_BASE}/confirm-invitation/?token=${encodeURIComponent(token)}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to confirm email");
  }

  return data;
}

export async function getInvitationDetails(token: string): Promise<{
  invitation: {
    email: string;
    tenant_name: string;
    role: string;
    expires_at: string;
  };
}> {
  const response = await fetch(
    `${API_BASE}/confirm-invitation/?token=${encodeURIComponent(token)}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to get invitation details");
  }

  return data;
}

export async function resendInvitation(
  token: string,
): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/resend-invitation/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ token }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to resend invitation");
  }

  return data;
}

export async function deleteInvitation(
  token: string,
  invitationSlug: string,
): Promise<void> {
  const response = await fetch(`${API_BASE}/invitations/${invitationSlug}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || "Failed to delete invitation");
  }
}

export async function changePassword(
  token: string,
  currentPassword: string,
  newPassword: string,
): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/change-password/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to change password");
  }

  return data;
}