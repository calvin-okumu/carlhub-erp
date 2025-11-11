"use client";
import type { LeaveRequest } from "@/api/types";
import { useState } from 'react';
import { LeaveCards } from "./Dashboard/LeaveCards";
import { LeaveHeader } from "./Dashboard/LeaveHeader";
import LeaveRequestTable from "./Requests/LeaveRequestTable";
import LeaveRequestModal from "./Requests/LeaveRequestModal";


export const LeaveOverview = () => {
    const [activeTab, setActiveTab] = useState<"requests" | "calendar" | "approvals" | "policies">("requests");
    const [isModalOpen, setIsModalOpen] = useState(false);

    const handleTabChange = (tab: "requests" | "calendar" | "approvals" | "policies") => {
        setActiveTab(tab);
    };

    const handleCreateRequest = () => {
        setIsModalOpen(true);
    };

    const handleModalClose = () => {
        setIsModalOpen(false);
    };

    const handleModalSuccess = () => {
        // Refresh the table data after successful creation
        // This will be handled by the table component's internal state management
        console.log("Leave request created successfully");
    };

    const handleEditRequest = (request: LeaveRequest) => {
        // TODO: Open edit leave request modal/form
        console.log("Edit leave request:", request);
    };

    const handleDeleteRequest = (id: string) => {
        // TODO: Handle delete with confirmation
        console.log("Delete leave request:", id);
    };

    return (
        <div className="space-y-4">
            <LeaveHeader activeTab={activeTab} onTabChange={handleTabChange} />
            <LeaveCards
                onAddRequest={handleCreateRequest}
                searchValue=""
                onSearchChange={() => {}}
            />
            <LeaveRequestTable
                onCreateRequest={handleCreateRequest}
                onEditRequest={handleEditRequest}
                onDeleteRequest={handleDeleteRequest}
            />

            <LeaveRequestModal
                isOpen={isModalOpen}
                onClose={handleModalClose}
                onSuccess={handleModalSuccess}
            />
        </div>
    );
};
