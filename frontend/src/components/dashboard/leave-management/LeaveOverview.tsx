"use client";
import { LeaveCards } from "./Dashboard/LeaveCards";
import { LeaveHeader } from "./Dashboard/LeaveHeader";
import { LeaveSummaryTable } from "./Dashboard/LeaveSummaryTable";

export const LeaveOverview = () => {
    const handleCreateRequest = () => {
        // Navigate to requests page for creating
        window.location.href = '/dashboard/leave/requests';
    };

    return (
        <div className="space-y-4">
            <LeaveHeader />
            <LeaveCards
                onAddRequest={handleCreateRequest}
                searchValue=""
                onSearchChange={() => {}}
            />
            <LeaveSummaryTable />
        </div>
    );
};
