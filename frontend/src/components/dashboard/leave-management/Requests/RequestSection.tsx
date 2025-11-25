"use client";
import { useState, useEffect, useCallback } from 'react';
import { LeaveSort } from './LeaveSort';
import { RequestHeader } from './RequestHeader';
import LeaveRequestTable from './LeaveRequestTable';
import { getLeaveRequests, getLeaveRequest, cancelLeaveRequest, deleteLeaveRequest } from '../../../../api/leave';
import { STORAGE_KEYS } from '../../../../constants/storage';
import type { LeaveRequest, PaginatedResponse } from '../../../../api/types';
import type { LeaveType, SortOption } from './LeaveSort';

export const RequestSection = () => {
    const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalItems, setTotalItems] = useState(0);
    const [itemsPerPage] = useState(10);
    const [editingRequest, setEditingRequest] = useState<LeaveRequest | null>(null);
    const [currentSort, setCurrentSort] = useState<LeaveType>('all');
    const [currentSortOption, setCurrentSortOption] = useState<SortOption>('applied_date_desc');

    const fetchLeaveRequests = useCallback(async (page = 1) => {
        try {
            setLoading(true);
            setError(null);

            // Get current user ID from localStorage
            const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
            let employeeId: number | undefined;

            if (userData) {
                const user = JSON.parse(userData);
                employeeId = user.id;
            }

            const params: {
                page: number;
                page_size: number;
                leave_type?: string;
                employee?: number;
                ordering: string;
            } = {
                page,
                page_size: itemsPerPage,
                ordering: '-applied_date',
                employee: employeeId,
            };

            // Add filtering
            if (currentSort !== 'all') {
                params.leave_type = currentSort;
            }

            // Add sorting
            switch (currentSortOption) {
                case 'applied_date_desc':
                    params.ordering = '-applied_date';
                    break;
                case 'applied_date_asc':
                    params.ordering = 'applied_date';
                    break;
                case 'start_date_desc':
                    params.ordering = '-start_date';
                    break;
                case 'start_date_asc':
                    params.ordering = 'start_date';
                    break;
                case 'status':
                    params.ordering = 'status';
                    break;
                default:
                    params.ordering = '-applied_date';
            }

            const response: PaginatedResponse<LeaveRequest> = await getLeaveRequests(params);
            setLeaveRequests(response.results || []);
            setCurrentPage(page);
            setTotalPages(Math.ceil(response.count / itemsPerPage));
            setTotalItems(response.count);
        } catch (err) {
            setError('Failed to fetch leave requests');
            console.error('Error fetching leave requests:', err);
        } finally {
            setLoading(false);
        }
    }, [itemsPerPage, currentSort, currentSortOption]);

    useEffect(() => {
        fetchLeaveRequests();
    }, [fetchLeaveRequests]);

    const handlePageChange = useCallback((page: number) => {
        fetchLeaveRequests(page);
    }, [fetchLeaveRequests]);

    const handleEditRequest = useCallback(async (id: string) => {
        try {
            const request = await getLeaveRequest(id);
            setEditingRequest(request);
        } catch (err) {
            console.error('Error fetching leave request for editing:', err);
            alert('Failed to load leave request for editing');
        }
    }, []);

    const handleDeleteRequest = useCallback(async (id: string) => {
        try {
            await deleteLeaveRequest(id);
            fetchLeaveRequests(currentPage); // Refresh the list
        } catch (err) {
            console.error('Error deleting leave request:', err);
            alert('Failed to delete leave request');
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

    const handleSortChange = useCallback((sortBy: LeaveType) => {
        setCurrentSort(sortBy);
    }, []);

    const handleSortOptionChange = useCallback((sortOption: SortOption) => {
        setCurrentSortOption(sortOption);
    }, []);

    return (
        <div>
            <RequestHeader
                onSearchChange={() => { }}
                onRequestSuccess={handleRequestSuccess}
                onCreateRequest={() => { }}
                editingRequest={editingRequest}
                onEditClose={() => setEditingRequest(null)}
            />
            <LeaveSort
                onSortChange={handleSortChange}
                onSortOptionChange={handleSortOptionChange}
                currentSort={currentSort}
                currentSortOption={currentSortOption}
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
                onEditRequest={handleEditRequest}
                onCancelRequest={handleCancelRequest}
                onDeleteRequest={handleDeleteRequest}
            />
        </div>
    );
}
