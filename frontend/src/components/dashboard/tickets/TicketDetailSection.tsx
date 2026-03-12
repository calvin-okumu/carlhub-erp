"use client";

import type { Ticket } from "@/api/types";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { Edit, Trash2 } from "lucide-react";

interface TicketDetailSectionProps {
  ticket: Ticket;
  onEdit: () => void;
  onDelete: () => void;
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

const formatDate = (value?: string | null) => {
  if (!value) return "—";
  return new Date(value).toLocaleDateString();
};

const formatDateTime = (value?: string | null) => {
  if (!value) return "—";
  return new Date(value).toLocaleString();
};

export default function TicketDetailSection({ ticket, onEdit, onDelete }: TicketDetailSectionProps) {
  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div className="space-y-2">
            <p className="text-sm text-gray-500">Ticket</p>
            <h2 className="text-2xl font-semibold text-gray-900">{ticket.title}</h2>
            <div className="flex flex-wrap items-center gap-2">
              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusClasses[ticket.status] || "bg-slate-100 text-slate-700"}`}>
                {ticket.status.replace("_", " ")}
              </span>
              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${priorityClasses[ticket.priority] || "bg-slate-100 text-slate-700"}`}>
                {ticket.priority}
              </span>
              <span className="text-xs text-gray-500">{ticket.client_name}</span>
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={onEdit} variant="outline" size="sm">
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
            <Button onClick={onDelete} variant="danger" size="sm">
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>
        {ticket.description ? <p className="mt-4 text-sm text-gray-600 leading-relaxed">{ticket.description}</p> : null}
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="p-5">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Details</h3>
          <div className="divide-y divide-gray-100">
            <div className="py-2 flex justify-between text-sm">
              <span className="text-gray-600">Category</span>
              <span className="font-medium text-gray-900">{ticket.category || "—"}</span>
            </div>
            <div className="py-2 flex justify-between text-sm">
              <span className="text-gray-600">Source</span>
              <span className="font-medium text-gray-900">{ticket.source || "—"}</span>
            </div>
            <div className="py-2 flex justify-between text-sm">
              <span className="text-gray-600">Assignee</span>
              <span className="font-medium text-gray-900">{ticket.assignee_name || "Unassigned"}</span>
            </div>
            <div className="py-2 flex justify-between text-sm">
              <span className="text-gray-600">External ID</span>
              <span className="font-medium text-gray-900">{ticket.external_id || "—"}</span>
            </div>
          </div>
        </Card>

        <Card className="p-5">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Requester</h3>
          <div className="divide-y divide-gray-100">
            <div className="py-2 flex justify-between text-sm">
              <span className="text-gray-600">Name</span>
              <span className="font-medium text-gray-900">{ticket.requester_name || "—"}</span>
            </div>
            <div className="py-2 flex justify-between text-sm">
              <span className="text-gray-600">Email</span>
              <span className="font-medium text-gray-900">{ticket.requester_email || "—"}</span>
            </div>
          </div>
        </Card>

        <Card className="p-5">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
          <div className="divide-y divide-gray-100">
            <div className="py-2 flex justify-between text-sm">
              <span className="text-gray-600">First Logged</span>
              <span className="font-medium text-gray-900">{formatDateTime(ticket.first_logged_at)}</span>
            </div>
            <div className="py-2 flex justify-between text-sm">
              <span className="text-gray-600">First Response</span>
              <span className="font-medium text-gray-900">{formatDateTime(ticket.first_response_at)}</span>
            </div>
            <div className="py-2 flex justify-between text-sm">
              <span className="text-gray-600">Due</span>
              <span className="font-medium text-gray-900">{formatDate(ticket.due_at)}</span>
            </div>
            <div className="py-2 flex justify-between text-sm">
              <span className="text-gray-600">Closed</span>
              <span className="font-medium text-gray-900">{formatDateTime(ticket.closed_at)}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
