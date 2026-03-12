import { API_BASE } from "./index";
import { authFetch } from "./client";
import type { CreateTicketData, PaginatedResponse, Ticket, TicketAttachment, UpdateTicketData } from "./types";

export async function getTickets(
  token: string,
  params?: {
    search?: string;
    ordering?: string;
    status?: string;
    priority?: string;
    assignee?: string;
    client?: string;
    created_at?: string;
    page?: number;
    limit?: number;
  }
): Promise<Ticket[] | PaginatedResponse<Ticket>> {
  const query = new URLSearchParams();
  if (params?.search) query.append("search", params.search);
  if (params?.ordering) query.append("ordering", params.ordering);
  if (params?.status) query.append("status", params.status);
  if (params?.priority) query.append("priority", params.priority);
  if (params?.assignee) query.append("assignee", params.assignee);
  if (params?.client) query.append("client", params.client);
  if (params?.created_at) query.append("created_at", params.created_at);
  if (params?.page) query.append("page", params.page.toString());
  if (params?.limit) query.append("limit", params.limit.toString());

  const url = `${API_BASE}/tickets/?${query.toString()}`;
  const response = await authFetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  }, { token });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || data.detail || "Failed to fetch tickets");
  }

  if (params?.page || params?.limit) {
    return data as PaginatedResponse<Ticket>;
  }

  return data.results || data;
}

export async function getTicket(token: string, ticketId: string): Promise<Ticket> {
  const response = await authFetch(`${API_BASE}/tickets/${ticketId}/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  }, { token });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || data.detail || "Failed to fetch ticket");
  }

  return data;
}

export async function createTicket(token: string, ticketData: CreateTicketData): Promise<Ticket> {
  const response = await authFetch(`${API_BASE}/tickets/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(ticketData),
  }, { token });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || data.detail || "Failed to create ticket");
  }

  return data;
}

export async function updateTicket(
  token: string,
  ticketId: string,
  ticketData: UpdateTicketData
): Promise<Ticket> {
  const response = await authFetch(`${API_BASE}/tickets/${ticketId}/`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(ticketData),
  }, { token });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || data.detail || "Failed to update ticket");
  }

  return data;
}

export async function deleteTicket(token: string, ticketId: string): Promise<void> {
  const response = await authFetch(`${API_BASE}/tickets/${ticketId}/`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  }, { token });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || data.detail || "Failed to delete ticket");
  }
}

export async function getTicketAttachments(token: string, ticketId: string): Promise<TicketAttachment[]> {
  const response = await authFetch(`${API_BASE}/tickets/${ticketId}/attachments/`, {
    method: "GET",
    headers: {
    },
  }, { token });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || data.detail || "Failed to fetch attachments");
  }

  return data as TicketAttachment[];
}

export async function uploadTicketAttachment(
  token: string,
  ticketId: string,
  file: File
): Promise<TicketAttachment> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await authFetch(`${API_BASE}/tickets/${ticketId}/attachments/`, {
    method: "POST",
    headers: {
    },
    body: formData,
  }, { token });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || data.detail || "Failed to upload attachment");
  }

  return data as TicketAttachment;
}
