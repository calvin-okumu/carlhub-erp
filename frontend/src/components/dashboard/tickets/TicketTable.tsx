"use client";

import Loader from "@/components/shared/Loader";
import Table from "@/components/ui/Table";
import type { Ticket } from "@/api/types";
import Button from "@/components/ui/Button";
import { Edit, Trash2 } from "lucide-react";
import Link from "next/link";

interface TicketTableProps {
  tickets: Ticket[];
  loading: boolean;
  error: string | null;
  onEditTicket: (ticket: Ticket) => void;
  onDeleteTicket: (ticketId: string) => void;
  pagination?: {
    count: number;
    next: string | null;
    previous: string | null;
  } | null;
  currentPage: number;
  onPageChange: (page: number) => void;
  searchValue: string;
}

const statusClasses: Record<string, string> = {
  open: "bg-amber-100 text-amber-800",
  in_progress: "bg-blue-100 text-blue-800",
  blocked: "bg-rose-100 text-rose-800",
  resolved: "bg-emerald-100 text-emerald-800",
  closed: "bg-slate-200 text-slate-700",
};

const priorityClasses: Record<string, string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-indigo-100 text-indigo-700",
  high: "bg-amber-100 text-amber-800",
  urgent: "bg-rose-100 text-rose-800",
};

export default function TicketTable({
  tickets,
  loading,
  error,
  onEditTicket,
  onDeleteTicket,
  pagination,
  currentPage,
  onPageChange,
  searchValue,
}: TicketTableProps) {
  const headers = ["Title", "Client", "Status", "Priority", "Assignee", "Created", "Actions"];

  const rows = tickets.map((ticket) => ({
    key: ticket.id,
    data: [
      <Link key={`${ticket.id}-title`} href={`/dashboard/tickets/${ticket.id}`} className="text-blue-600 hover:text-blue-800 hover:underline">
        {ticket.title}
      </Link>,
      ticket.client_name || "-",
      <span
        key={`${ticket.id}-status`}
        className={`px-2 py-1 text-xs font-semibold rounded-full ${statusClasses[ticket.status] || "bg-slate-100 text-slate-700"}`}
      >
        {ticket.status.replace("_", " ")}
      </span>,
      <span
        key={`${ticket.id}-priority`}
        className={`px-2 py-1 text-xs font-semibold rounded-full ${priorityClasses[ticket.priority] || "bg-slate-100 text-slate-700"}`}
      >
        {ticket.priority}
      </span>,
      ticket.assignee_name || "Unassigned",
      new Date(ticket.created_at).toLocaleDateString(),
      <div key={`${ticket.id}-actions`} className="flex gap-2">
        <Button onClick={() => onEditTicket(ticket)} variant="outline" size="sm">
          <Edit className="h-4 w-4" />
        </Button>
        <Button
          onClick={() => {
            if (confirm("Are you sure you want to delete this ticket?")) {
              onDeleteTicket(ticket.id);
            }
          }}
          variant="danger"
          size="sm"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>,
    ],
  }));

  if (loading) {
    return <Loader />;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  if (!loading && !error && tickets.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 p-8 text-center text-gray-500">
        {searchValue ? `No tickets found matching "${searchValue}"` : "No tickets found"}
      </div>
    );
  }

  const totalPages = pagination ? Math.ceil(pagination.count / 10) : 1;

  return (
    <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
      <Table
        headers={headers}
        rows={rows}
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={onPageChange}
        itemsPerPage={10}
        totalItems={pagination?.count || tickets.length}
      />
    </div>
  );
}
