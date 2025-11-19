"use client";

import { useState, useEffect, useCallback } from 'react';
import { ApprovalsHeader } from './ApprovalsHeader';
import { ApprovalTabs } from './ApprovalTabs';
import ApprovalsTable from './ApprovalsTable';
import { getLeaveRequests, approveLeaveRequest, rejectLeaveRequest } from '@/api/leave';
import type { LeaveRequest, PaginatedResponse } from '@/api/types';

type ApprovalTab = 'all' | 'approved' | 'rejected';

export default function ApprovalsSection() {
    const [searchValue, setSearchValue] = useState('');
    const [activeTab, setActiveTab] = useState<ApprovalTab>('all');
    const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [approvingId, setApprovingId] = useState<string | null>(null);
    const [rejectingId, setRejectingId] = useState<string | null>(null);

    const tabCounts = {
        all: leaveRequests.filter(r => r.status === 'pending').length,
        approved: leaveRequests.filter(r => r.status === 'approved').length,
        rejected: leaveRequests.filter(r => r.status === 'rejected').length,
    };

    const fetchLeaveRequests = useCallback(async () => {
        try {
            setLoading(true);
            const params: Record<string, string> = {};

            if (activeTab !== 'all') {
                params.status = activeTab;
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

    const handleApprove = async (requestId: string) => {
        try {
            setApprovingId(requestId);
            await approveLeaveRequest(requestId);
            await fetchLeaveRequests();
        } catch (error) {
            console.error('Failed to approve request:', error);
        } finally {
            setApprovingId(null);
        }
    };

    const handleReject = async (requestId: string) => {
        try {
            setRejectingId(requestId);
            await rejectLeaveRequest(requestId);
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
                counts={tabCounts}
            />

            <ApprovalsTable
                leaveRequests={leaveRequests}
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
