import { useCallback, useState } from "react";
import type { CreateTicketData, PaginatedResponse, Ticket, UpdateTicketData } from "../api";
import { createTicket, deleteTicket, getTickets, updateTicket } from "../api";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

export function useTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<{ count: number; next: string | null; previous: string | null } | null>(null);

  const fetchTickets = useCallback(
    async (params?: { page?: number; limit?: number; search?: string; ordering?: string; status?: string; priority?: string }) => {
      const token = getToken();
      if (!token) return;

      setLoading(true);
      try {
        const data = await getTickets(token, { ordering: "-created_at", ...params });
        if (params?.page || params?.limit) {
          const paginatedData = data as PaginatedResponse<Ticket>;
          setTickets(paginatedData.results);
          setPagination({
            count: paginatedData.count,
            next: paginatedData.next,
            previous: paginatedData.previous,
          });
        } else {
          setTickets(data as Ticket[]);
          setPagination(null);
        }
      } catch (err) {
        console.error(err);
        setError("Failed to load tickets. Please try again.");
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    tickets,
    loading,
    error,
    pagination,
    addTicket: async (data: CreateTicketData, refreshParams?: { page?: number; limit?: number; search?: string; ordering?: string; status?: string; priority?: string }) => {
      const token = getToken();
      if (!token) return;

      setLoading(true);
      try {
        await createTicket(token, data);
        await fetchTickets(refreshParams);
      } catch (err) {
        console.error(err);
        setError(err instanceof Error ? err.message : "Failed to create ticket.");
      } finally {
        setLoading(false);
      }
    },
    editTicket: async (ticketId: string, data: UpdateTicketData) => {
      const token = getToken();
      if (!token) return;

      setLoading(true);
      try {
        const updatedTicket = await updateTicket(token, ticketId, data);
        setTickets((prev) => prev.map((ticket) => (ticket.id === ticketId ? updatedTicket : ticket)));
      } catch (err) {
        console.error(err);
        setError(err instanceof Error ? err.message : "Failed to update ticket.");
      } finally {
        setLoading(false);
      }
    },
    removeTicket: async (ticketId: string) => {
      const token = getToken();
      if (!token) return;

      const ticketToRemove = tickets.find((ticket) => ticket.id === ticketId);
      if (!ticketToRemove) return;

      setTickets((prev) => prev.filter((ticket) => ticket.id !== ticketId));

      setLoading(true);
      try {
        await deleteTicket(token, ticketId);
      } catch (err) {
        setTickets((prev) => [...prev, ticketToRemove]);
        setError(err instanceof Error ? err.message : "Failed to delete ticket.");
      } finally {
        setLoading(false);
      }
    },
    refetch: fetchTickets,
    setError,
  };
}
