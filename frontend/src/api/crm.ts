import { Client, CreateClientData, UpdateClientData, UserTenant } from './types';
import { API_BASE } from './index';
import { PaginatedResponse } from './types';
import { apiCall } from './api-wrapper';

export async function getClients(params?: { search?: string; ordering?: string; status?: string; page?: number; limit?: number }): Promise<Client[] | PaginatedResponse<Client>> {
  const query = new URLSearchParams();
  if (params?.search) query.append('search', params.search);
  if (params?.ordering) query.append('ordering', params.ordering);
  if (params?.status) query.append('status', params.status);
  if (params?.page) query.append('page', params.page.toString());
  if (params?.limit) query.append('limit', params.limit.toString());

  const url = `${API_BASE}/clients/?${query.toString()}`;
   const data = await apiCall<Client[] | PaginatedResponse<Client>>(url, {
     method: "GET",
   });

   // If pagination params are provided, return paginated response
   if (params?.page || params?.limit) {
     return data as PaginatedResponse<Client>;
   }

   // Otherwise, return just the results array
   return (data as { results: Client[] }).results || data;
}

export async function createClient(clientData: CreateClientData): Promise<Client> {
  const url = `${API_BASE}/clients/`;
  const data = await apiCall<Client>(url, {
    method: "POST",
    body: JSON.stringify(clientData),
  });

  return data;
}

export async function updateClient(clientSlug: string, clientData: UpdateClientData): Promise<Client> {
  const url = `${API_BASE}/clients/${clientSlug}/`;
  const data = await apiCall<Client>(url, {
    method: "PUT",
    body: JSON.stringify(clientData),
  });

  return data;
}

export async function deleteClient(clientSlug: string): Promise<void> {
  const url = `${API_BASE}/clients/${clientSlug}/`;
  await apiCall<void>(url, {
    method: "DELETE",
  });
}

export async function getUserTenants(): Promise<UserTenant[]> {
  const url = `${API_BASE}/members/`;
  const data = await apiCall<UserTenant[]>(url, {
    method: "GET",
  });

  return (data as { results: UserTenant[] }).results || data;
}

