"use client";

import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Clock, Inbox } from "lucide-react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import StatCard from "@/components/ui/StatCard";
import type { Ticket } from "@/api/types";
import { getTickets } from "@/api/tickets";

interface TicketHeaderProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  onAddTicket: () => void;
}

export default function TicketHeader({ searchValue, onSearchChange, onAddTicket }: TicketHeaderProps) {
  const [allTickets, setAllTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAllTickets = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      try {
        const data = await getTickets(token, { limit: 1000 });
        if (data && typeof data === "object" && "results" in data) {
          setAllTickets(data.results);
        } else {
          setAllTickets(data as Ticket[]);
        }
      } catch (error) {
        console.error("Failed to fetch tickets for metrics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllTickets();
  }, []);

  const tickets = allTickets;
  const totalTickets = tickets.length;
  const openTickets = tickets.filter((ticket) => ticket.status === "open").length;
  const inProgressTickets = tickets.filter((ticket) => ticket.status === "in_progress").length;
  const closedTickets = tickets.filter((ticket) => ticket.status === "closed").length;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Tickets"
          value={loading ? "..." : totalTickets}
          icon={Inbox}
          className="shadow-lg hover:shadow-xl transition-shadow duration-300"
        />
        <StatCard
          title="Open"
          value={loading ? "..." : openTickets}
          icon={AlertCircle}
          className="shadow-lg hover:shadow-xl transition-shadow duration-300"
        />
        <StatCard
          title="In Progress"
          value={loading ? "..." : inProgressTickets}
          icon={Clock}
          className="shadow-lg hover:shadow-xl transition-shadow duration-300"
        />
        <StatCard
          title="Closed"
          value={loading ? "..." : closedTickets}
          icon={CheckCircle2}
          className="shadow-lg hover:shadow-xl transition-shadow duration-300"
        />
      </div>
      <div className="flex items-center justify-between">
        <Input
          type="text"
          placeholder="Search tickets..."
          value={searchValue}
          onChange={(event) => onSearchChange(event.target.value)}
          className="max-w-xs"
        />
        <Button onClick={onAddTicket}>+ Add Ticket</Button>
      </div>
    </div>
  );
}
