"use client";

import { approveLeaveRequestLevel, getLeaveRequests, rejectLeaveRequestLevel, getPendingApprovalsSummary } from '@/api/leave';
import type { LeaveRequest, PaginatedResponse } from '@/api/types';
import { useCallback, useEffect, useState } from 'react';
import { ApprovalsHeader } from './ApprovalsHeader';
import ApprovalsTable from './ApprovalsTable';
import { ApprovalTabs } from './ApprovalTabs';

type ApprovalTab = 'all' | 'approved' | 'rejected';

export default function ApprovalsSection() {
    const [searchValue, setSearchValue] = useState('');
    const [activeTab, setActiveTab] = useState<ApprovalTab>('all');
    const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [approvingId, setApprovingId] = useState<string | null>(null);
    const [rejectingId, setRejectingId] = useState<string | null>(null);

    const tabCounts = {
        all: (leaveRequests || []).filter(r => r.status.startsWith('pending_')).length,
        approved: (leaveRequests || []).filter(r => r.status === 'approved').length,
        rejected: (leaveRequests || []).filter(r => r.status === 'rejected').length,
    };

const fetchLeaveRequests = useCallback(async () => {
    try {
        setLoading(true);
        
        // Get all requests - backend will filter by permissions
        const response = await getLeaveRequests({});
        
        // Handle both paginated and direct array responses
        let allRequests: LeaveRequest[] = [];
        if (Array.isArray(response)) {
            allRequests = response;
        } else if (response && response.results) {
            allRequests = response.results;
        }
        
        // Filter by active tab
        let filteredResults = allRequests;
        if (activeTab === 'approved') {
            filteredResults = allRequests.filter(r => r.status === 'approved');
        } else if (activeTab === 'rejected') {
            filteredResults = allRequests.filter(r => r.status === 'rejected');
        } else {
            // 'all' tab - show pending requests
            filteredResults = allRequests.filter(r => r.status.startsWith('pending_'));
        }
        
        // Apply search filter
        if (searchValue.trim()) {
            filteredResults = filteredResults.filter(request =>
                request.employee_name?.toLowerCase().includes(searchValue.toLowerCase())
            );
        }
        
        setLeaveRequests(filteredResults);
    } catch (error) {
        console.error('Failed to fetch leave requests:', error);
        setLeaveRequests([]);
    } finally {
        setLoading(false);
    }
}, [activeTab, searchValue]);

useEffect(() => {
    fetchLeaveRequests();
}, [fetchLeaveRequests]);

const handleApprove = async (requestSlug: string) => {
    try {
        setApprovingId(requestSlug);
        await approveLeaveRequestLevel(requestSlug, { notes: undefined });
        await fetchLeaveRequests();
    } catch (error) {
        console.error('Failed to approve request:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to approve leave request. Please try again.';
        alert(errorMessage);
    } finally {
        setApprovingId(null);
    }
};

const handleReject = async (requestSlug: string) => {
    const reason = prompt('Please provide a reason for rejection:');
    if (!reason?.trim()) {
        alert('Rejection reason is required.');
        return;
    }

    try {
        setRejectingId(requestSlug);
        await rejectLeaveRequestLevel(requestSlug, { notes: reason.trim() });
        await fetchLeaveRequests();
    } catch (error) {
        console.error('Failed to reject request:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to reject leave request. Please try again.';
        alert(errorMessage);
    } finally {
        setRejectingId(null);
    }
};



const handleFiltersClick = () => {
    console.log('Open filters');
};

const handleBulkActionsClick = () => {
    console.log('Open bulk actions');
};

return (
    <div>
        

        <ApprovalsHeader
            searchValue={searchValue}
            onSearchChange={setSearchValue}
            onFiltersClick={handleFiltersClick}
            onBulkActionsClick={handleBulkActionsClick}
        />

<ApprovalTabs
                activeTab={activeTab}
                onTabChange={setActiveTab}
                counts={!loading ? tabCounts : { all: 0, approved: 0, rejected: 0 }}
            />

<ApprovalsTable
                leaveRequests={leaveRequests || []}
                loading={loading}
                onApprove={handleApprove}
                onReject={handleReject}
                approvingId={approvingId}
                rejectingId={rejectingId}
                searchValue={searchValue}
                statusFilter={activeTab}
            />
    </div>
);
}
