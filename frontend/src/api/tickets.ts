import { API_BASE } from "./index";
import type { CreateTicketData, PaginatedResponse, Ticket, UpdateTicketData } from "./types";

export async function getTickets(
  token: string,
  params?: { search?: string; ordering?: string; status?: string; priority?: string; page?: number; limit?: number }
): Promise<Ticket[] | PaginatedResponse<Ticket>> {
  const query = new URLSearchParams();
  if (params?.search) query.append("search", params.search);
  if (params?.ordering) query.append("ordering", params.ordering);
  if (params?.status) query.append("status", params.status);
  if (params?.priority) query.append("priority", params.priority);
  if (params?.page) query.append("page", params.page.toString());
  if (params?.limit) query.append("limit", params.limit.toString());

  const url = `${API_BASE}/tickets/?${query.toString()}`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch tickets");
  }

  if (params?.page || params?.limit) {
    return data as PaginatedResponse<Ticket>;
  }

  return data.results || data;
}

export async function getTicket(token: string, ticketId: string): Promise<Ticket> {
  const response = await fetch(`${API_BASE}/tickets/${ticketId}/`, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch ticket");
  }

  return data;
}

export async function createTicket(token: string, ticketData: CreateTicketData): Promise<Ticket> {
  const response = await fetch(`${API_BASE}/tickets/`, {
    method: "POST",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(ticketData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to create ticket");
  }

  return data;
}

export async function updateTicket(
  token: string,
  ticketId: string,
  ticketData: UpdateTicketData
): Promise<Ticket> {
  const response = await fetch(`${API_BASE}/tickets/${ticketId}/`, {
    method: "PATCH",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(ticketData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to update ticket");
  }

  return data;
}

export async function deleteTicket(token: string, ticketId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/tickets/${ticketId}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || "Failed to delete ticket");
  }
}
