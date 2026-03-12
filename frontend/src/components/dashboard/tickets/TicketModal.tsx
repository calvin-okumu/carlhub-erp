"use client";

import type { Client, CreateTicketData, Ticket, UpdateTicketData } from "@/api/types";
import { getClients, getUserTenants } from "@/api/crm";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import Select from "@/components/ui/Select";
import Textarea from "@/components/ui/Textarea";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";

interface TicketModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: "add" | "edit";
  ticket?: Ticket;
  onSave: (data: CreateTicketData | UpdateTicketData) => void;
}

type FormData = {
  title: string;
  client: string;
  description: string;
  status: string;
  priority: string;
  category: string;
  source: string;
  requester_name: string;
  requester_email: string;
  assignee: string;
  due_at: string;
};

const statusOptions = ["open", "in_progress", "blocked", "resolved", "closed"];
const priorityOptions = ["low", "medium", "high", "urgent"];

export default function TicketModal({ isOpen, onClose, mode, ticket, onSave }: TicketModalProps) {
  const [clients, setClients] = useState<Client[]>([]);
  const [loadingClients, setLoadingClients] = useState(false);
  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      title: "",
      client: "",
      description: "",
      status: "open",
      priority: "medium",
      category: "",
      source: "",
      requester_name: "",
      requester_email: "",
      assignee: "",
      due_at: "",
    },
  });

  useEffect(() => {
    if (!isOpen) return;

    const fetchClients = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      setLoadingClients(true);
      try {
        const tenants = await getUserTenants(token);
        const ownerTenant = Array.isArray(tenants) ? tenants.find((t) => t.is_owner) || tenants[0] : tenants;
        if (!ownerTenant) {
          setClients([]);
          return;
        }
        const data = await getClients(token, { tenant: ownerTenant.tenant, limit: 1000, ordering: "name" });
        const list = data && typeof data === "object" && "results" in data ? data.results : (data as Client[]);
        setClients(list);
      } catch (error) {
        console.error("Failed to fetch clients for tickets:", error);
        setClients([]);
      } finally {
        setLoadingClients(false);
      }
    };

    fetchClients();
  }, [isOpen]);

  useEffect(() => {
    if (mode === "edit" && ticket) {
      setValue("title", ticket.title);
      setValue("client", ticket.client);
      setValue("description", ticket.description || "");
      setValue("status", ticket.status || "open");
      setValue("priority", ticket.priority || "medium");
      setValue("category", ticket.category || "");
      setValue("source", ticket.source || "");
      setValue("requester_name", ticket.requester_name || "");
      setValue("requester_email", ticket.requester_email || "");
      setValue("assignee", ticket.assignee ? String(ticket.assignee) : "");
      setValue("due_at", ticket.due_at ? ticket.due_at.slice(0, 10) : "");
    } else {
      setValue("title", "");
      setValue("client", "");
      setValue("description", "");
      setValue("status", "open");
      setValue("priority", "medium");
      setValue("category", "");
      setValue("source", "");
      setValue("requester_name", "");
      setValue("requester_email", "");
      setValue("assignee", "");
      setValue("due_at", "");
    }
  }, [mode, ticket, isOpen, setValue]);

  const onSubmit = (data: FormData) => {
    if (!data.title || (!data.client && mode === "add")) return;

    const dueAtValue = data.due_at ? new Date(data.due_at).toISOString() : null;

    const base = {
      title: data.title,
      description: data.description || undefined,
      status: data.status || undefined,
      priority: data.priority || undefined,
      category: data.category || undefined,
      source: data.source || undefined,
      requester_name: data.requester_name || undefined,
      requester_email: data.requester_email || undefined,
      assignee: data.assignee ? Number(data.assignee) : null,
      due_at: dueAtValue,
    };

    if (mode === "add") {
      const submitData: CreateTicketData = {
        ...base,
        client: data.client,
      };
      onSave(submitData);
      return;
    }

    const submitData: UpdateTicketData = {
      ...base,
    };
    onSave(submitData);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={mode === "add" ? "Add Ticket" : "Edit Ticket"} size="lg">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700">
              Title *
            </label>
            <Input id="title" type="text" {...register("title", { required: "Title is required" })} />
            {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title.message}</p>}
          </div>
          <div>
            <label htmlFor="client" className="block text-sm font-medium text-gray-700">
              Client *
            </label>
            <Select id="client" {...register("client", { required: mode === "add" ? "Client is required" : false })} disabled={mode === "edit" || loadingClients}>
              <option value="">{loadingClients ? "Loading clients..." : "Select a client"}</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </Select>
            {errors.client && <p className="text-red-500 text-sm mt-1">{errors.client.message}</p>}
          </div>
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700">
              Status
            </label>
            <Select id="status" {...register("status")}>
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {status.replace("_", " ")}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
              Priority
            </label>
            <Select id="priority" {...register("priority")}>
              {priorityOptions.map((priority) => (
                <option key={priority} value={priority}>
                  {priority}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700">
              Category
            </label>
            <Input id="category" type="text" {...register("category")} />
          </div>
          <div>
            <label htmlFor="source" className="block text-sm font-medium text-gray-700">
              Source
            </label>
            <Input id="source" type="text" {...register("source")} />
          </div>
          <div>
            <label htmlFor="requester_name" className="block text-sm font-medium text-gray-700">
              Requester Name
            </label>
            <Input id="requester_name" type="text" {...register("requester_name")} />
          </div>
          <div>
            <label htmlFor="requester_email" className="block text-sm font-medium text-gray-700">
              Requester Email
            </label>
            <Input id="requester_email" type="email" {...register("requester_email")} />
          </div>
          <div>
            <label htmlFor="assignee" className="block text-sm font-medium text-gray-700">
              Assignee ID
            </label>
            <Input id="assignee" type="number" {...register("assignee")} />
          </div>
          <div>
            <label htmlFor="due_at" className="block text-sm font-medium text-gray-700">
              Due Date
            </label>
            <Input id="due_at" type="date" {...register("due_at")} />
          </div>
        </div>
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <Textarea id="description" rows={4} {...register("description")} />
        </div>
        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" onClick={onClose} variant="secondary">
            Cancel
          </Button>
          <Button type="submit">{mode === "add" ? "Add Ticket" : "Update Ticket"}</Button>
        </div>
      </form>
    </Modal>
  );
}
