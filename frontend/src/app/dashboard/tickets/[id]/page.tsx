"use client";

import { deleteTicket, getTicket, updateTicket } from "@/api/tickets";
import type { Ticket, UpdateTicketData } from "@/api/types";
import TicketDetailSection from "@/components/dashboard/tickets/TicketDetailSection";
import TicketModal from "@/components/dashboard/tickets/TicketModal";
import Loader from "@/components/shared/Loader";
import Button from "@/components/ui/Button";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function TicketDetailPage() {
  const params = useParams();
  const router = useRouter();
  const ticketId = Array.isArray(params.id) ? params.id[0] : params.id;
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    const fetchTicket = async () => {
      const token = localStorage.getItem("access_token");
      if (!token || !ticketId) {
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const data = await getTicket(token, String(ticketId));
        setTicket(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load ticket details.");
      } finally {
        setLoading(false);
      }
    };

    fetchTicket();
  }, [ticketId]);

  const handleDelete = async () => {
    if (!ticketId) return;
    if (!confirm("Are you sure you want to delete this ticket?")) return;

    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
      await deleteTicket(token, String(ticketId));
      router.push("/dashboard/tickets");
    } catch (err) {
      console.error(err);
      setError("Failed to delete ticket.");
    }
  };

  const handleSave = async (data: UpdateTicketData) => {
    if (!ticketId) return;
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
      const updated = await updateTicket(token, String(ticketId), data);
      setTicket(updated);
      setModalOpen(false);
    } catch (err) {
      console.error(err);
      setError("Failed to update ticket.");
    }
  };

  if (loading) {
    return <Loader />;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  if (!ticket) {
    return <div className="text-gray-500">Ticket not found.</div>;
  }

  return (
    <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">Tickets</p>
          <h1 className="h1-title">Ticket Details</h1>
        </div>
        <Button variant="outline" onClick={() => router.push("/dashboard/tickets")}>Back to Tickets</Button>
      </div>
      <TicketDetailSection ticket={ticket} onEdit={() => setModalOpen(true)} onDelete={handleDelete} />
      <TicketModal isOpen={modalOpen} onClose={() => setModalOpen(false)} mode="edit" ticket={ticket} onSave={handleSave} />
    </div>
  );
}
