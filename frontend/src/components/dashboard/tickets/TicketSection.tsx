"use client";

import { useEffect, useState } from "react";
import TicketHeader from "./TicketHeader";
import TicketTable from "./TicketTable";
import TicketModal from "./TicketModal";
import { useTickets } from "@/hooks/useTickets";
import type { CreateTicketData, Ticket, UpdateTicketData } from "@/api/types";

export default function TicketSection() {
  const [currentPage, setCurrentPage] = useState(1);
  const [searchValue, setSearchValue] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"add" | "edit">("add");
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const { tickets, loading, error, pagination, addTicket, editTicket, removeTicket, refetch } = useTickets();

  useEffect(() => {
    refetch({ page: currentPage, limit: 10, search: searchValue });
  }, [currentPage, searchValue, refetch]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchValue]);

  const handleAddTicket = () => {
    setModalMode("add");
    setSelectedTicket(null);
    setModalOpen(true);
  };

  const handleEditTicket = (ticket: Ticket) => {
    setModalMode("edit");
    setSelectedTicket(ticket);
    setModalOpen(true);
  };

  const handleSaveTicket = async (data: CreateTicketData | UpdateTicketData) => {
    try {
      if (modalMode === "add") {
        await addTicket(data as CreateTicketData, { page: currentPage, limit: 10, search: searchValue });
      } else if (selectedTicket) {
        await editTicket(selectedTicket.id, data as UpdateTicketData);
      }
      setModalOpen(false);
    } catch (error) {
      console.error("Error saving ticket:", error);
    }
  };

  return (
    <div className="space-y-6">
      <TicketHeader searchValue={searchValue} onSearchChange={setSearchValue} onAddTicket={handleAddTicket} />
      <TicketTable
        tickets={tickets}
        loading={loading}
        error={error}
        onEditTicket={handleEditTicket}
        onDeleteTicket={removeTicket}
        pagination={pagination}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        searchValue={searchValue}
      />
      <TicketModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        mode={modalMode}
        ticket={selectedTicket || undefined}
        onSave={handleSaveTicket}
      />
    </div>
  );
}
