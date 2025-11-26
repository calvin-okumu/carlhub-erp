"use client";

import { approveLeaveRequest, getLeaveRequests, rejectLeaveRequest } from '@/api/leave';
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
        const params: Record<string, string> = {};

        // Handle status filtering for new workflow statuses
        if (activeTab !== 'all') {
            if (activeTab === 'approved' || activeTab === 'rejected') {
                params.status = activeTab;
            } else {
                // For 'all' tab, don't filter by status to get all pending requests
                // The backend will return requests based on user permissions
            }
        }

        if (searchValue.trim()) {
            params.search = searchValue.trim();
        }

        const response: PaginatedResponse<LeaveRequest> = await getLeaveRequests(params);
        setLeaveRequests(response.results);
    } catch (error) {
        console.error('Failed to fetch leave requests:', error);
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
        await approveLeaveRequest(requestSlug);
        await fetchLeaveRequests();
    } catch (error) {
        console.error('Failed to approve request:', error);
    } finally {
        setApprovingId(null);
    }
};

const handleReject = async (requestSlug: string) => {
    try {
        setRejectingId(requestSlug);
        await rejectLeaveRequest(requestSlug);
        await fetchLeaveRequests();
    } catch (error) {
        console.error('Failed to reject request:', error);
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
