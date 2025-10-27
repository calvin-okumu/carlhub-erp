import { Client, CreateClientData, UpdateClientData, UserTenant } from './types';
import { API_BASE } from './index';
import { PaginatedResponse } from './types';

export async function getClients(token: string, params?: { search?: string; ordering?: string; status?: string; page?: number; limit?: number }): Promise<Client[] | PaginatedResponse<Client>> {
  const query = new URLSearchParams();
  if (params?.search) query.append('search', params.search);
  if (params?.ordering) query.append('ordering', params.ordering);
  if (params?.status) query.append('status', params.status);
  if (params?.page) query.append('page', params.page.toString());
  if (params?.limit) query.append('limit', params.limit.toString());

  const url = `${API_BASE}/clients/?${query.toString()}`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch clients");
  }

  // If pagination params are provided, return paginated response
  if (params?.page || params?.limit) {
    return data as PaginatedResponse<Client>;
  }

  // Otherwise, return just the results array
  return data.results || data;
}

export async function createClient(token: string, clientData: CreateClientData): Promise<Client> {
  const response = await fetch(`${API_BASE}/clients/`, {
    method: "POST",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(clientData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to create client");
  }

  return data;
}

export async function updateClient(token: string, clientSlug: string, clientData: UpdateClientData): Promise<Client> {
  const response = await fetch(`${API_BASE}/clients/${clientSlug}/`, {
    method: "PUT",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(clientData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to update client");
  }

  return data;
}

export async function deleteClient(token: string, clientSlug: string): Promise<void> {
  const response = await fetch(`${API_BASE}/clients/${clientSlug}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || "Failed to delete client");
  }
}

export async function getUserTenants(token: string): Promise<UserTenant[]> {
  const response = await fetch(`${API_BASE}/members/`, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch user tenants");
  }

  return data.results || data;
}

