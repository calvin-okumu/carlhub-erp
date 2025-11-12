"use client";
import { useState, useEffect, useCallback } from 'react';
import { LeaveSort } from './LeaveSort';
import { RequestHeader } from './RequestHeader';
import LeaveRequestTable from './LeaveRequestTable';
import { getLeaveRequests, approveLeaveRequest, rejectLeaveRequest, cancelLeaveRequest } from '../../../../api/leave';
import type { LeaveRequest, PaginatedResponse } from '../../../../api/types';

export const RequestSection = () => {
    const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalItems, setTotalItems] = useState(0);
    const [itemsPerPage] = useState(10);

    const fetchLeaveRequests = useCallback(async (page = 1) => {
        try {
            setLoading(true);
            setError(null);
            const response: PaginatedResponse<LeaveRequest> = await getLeaveRequests({
                page,
                page_size: itemsPerPage
            });
            setLeaveRequests(response.results);
            setCurrentPage(page);
            setTotalPages(Math.ceil(response.count / itemsPerPage));
            setTotalItems(response.count);
        } catch (err) {
            setError('Failed to fetch leave requests');
            console.error('Error fetching leave requests:', err);
        } finally {
            setLoading(false);
        }
    }, [itemsPerPage]);

    useEffect(() => {
        fetchLeaveRequests();
    }, [fetchLeaveRequests]);

    const handlePageChange = useCallback((page: number) => {
        fetchLeaveRequests(page);
    }, [fetchLeaveRequests]);

    const handleApproveRequest = useCallback(async (id: string) => {
        try {
            await approveLeaveRequest(id);
            fetchLeaveRequests(currentPage); // Refresh the list
        } catch (err) {
            console.error('Error approving leave request:', err);
            alert('Failed to approve leave request');
        }
    }, [currentPage, fetchLeaveRequests]);

    const handleRejectRequest = useCallback(async (id: string) => {
        try {
            await rejectLeaveRequest(id);
            fetchLeaveRequests(currentPage); // Refresh the list
        } catch (err) {
            console.error('Error rejecting leave request:', err);
            alert('Failed to reject leave request');
        }
    }, [currentPage, fetchLeaveRequests]);

    const handleCancelRequest = useCallback(async (id: string) => {
        try {
            await cancelLeaveRequest(id);
            fetchLeaveRequests(currentPage); // Refresh the list
        } catch (err) {
            console.error('Error cancelling leave request:', err);
            alert('Failed to cancel leave request');
        }
    }, [currentPage, fetchLeaveRequests]);

    const handleRequestSuccess = useCallback(() => {
        fetchLeaveRequests(currentPage);
    }, [currentPage, fetchLeaveRequests]);

    return (
        <div>
            <RequestHeader
                onSearchChange={() => { }}
                onRequestSuccess={handleRequestSuccess}
                onCreateRequest={() => { }}
            />
            <LeaveSort
                onSortChange={() => { }}
                currentSort="all"
            />
            <LeaveRequestTable
                leaveRequests={leaveRequests}
                loading={loading}
                error={error}
                currentPage={currentPage}
                totalPages={totalPages}
                totalItems={totalItems}
                itemsPerPage={itemsPerPage}
                onPageChange={handlePageChange}
                onApproveRequest={handleApproveRequest}
                onRejectRequest={handleRejectRequest}
                onCancelRequest={handleCancelRequest}
            />
        </div>
    );
}
