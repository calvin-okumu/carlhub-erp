"use client";

import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { getLeaveRequests } from '@/api/leave';
import type { LeaveRequest, PaginatedResponse } from '@/api/types';
import Button from '@/components/ui/Button';
import Table from '@/components/ui/Table';
import SearchInput from '@/components/shared/SearchInput';
import Loader from '@/components/shared/Loader';
import { Edit, Trash2, Plus } from 'lucide-react';

interface LeaveRequestTableProps {
    onCreateRequest: () => void;
    onEditRequest: (request: LeaveRequest) => void;
    onDeleteRequest: (id: string) => void;
}

const LeaveRequestTable = ({
    onCreateRequest,
    onEditRequest,
    onDeleteRequest
}: LeaveRequestTableProps) => {
    const [requests, setRequests] = useState<LeaveRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchValue, setSearchValue] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalItems, setTotalItems] = useState(0);

    const fetchRequests = useCallback(async (page = 1, search = '') => {
        setLoading(true);
        setError(null);
        try {
            const params: {
                page: number;
                page_size: number;
                search?: string;
            } = {
                page,
                page_size: 10,
            };

            if (search) {
                params.search = search;
            }

            const response: PaginatedResponse<LeaveRequest> = await getLeaveRequests(params);
            setRequests(response.results);
            setTotalPages(Math.ceil(response.count / 10));
            setTotalItems(response.count);
        } catch (err) {
            setError('Failed to fetch leave requests');
            console.error('Failed to fetch leave requests:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const filteredRequests = useMemo(() => {
        if (!searchValue) return requests;

        return requests.filter(request =>
            request.employee_name.toLowerCase().includes(searchValue.toLowerCase()) ||
            request.leave_type.toLowerCase().includes(searchValue.toLowerCase()) ||
            request.status.toLowerCase().includes(searchValue.toLowerCase())
        );
    }, [requests, searchValue]);

    const handleSearchChange = (value: string) => {
        setSearchValue(value);
        setCurrentPage(1); // Reset to first page when searching
    };

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        fetchRequests(page, searchValue);
    };

    const handleEdit = (request: LeaveRequest) => {
        onEditRequest(request);
    };

    const handleDelete = (id: string) => {
        if (confirm("Are you sure you want to delete this leave request?")) {
            onDeleteRequest(id);
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    const getStatusBadge = (status: string) => {
        const statusClasses = {
            pending: 'bg-yellow-100 text-yellow-800',
            approved: 'bg-green-100 text-green-800',
            rejected: 'bg-red-100 text-red-800',
            cancelled: 'bg-gray-100 text-gray-800',
            taken: 'bg-blue-100 text-blue-800'
        };

        return (
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800'}`}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
            </span>
        );
    };

    const headers = [
        "Employee",
        "Leave Type",
        "Start Date",
        "End Date",
        "Days Requested",
        "Status",
        "Applied Date",
        "Actions"
    ];

    const rows = filteredRequests.map(request => ({
        key: request.id,
        data: [
            request.employee_name,
            request.leave_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
            formatDate(request.start_date),
            formatDate(request.end_date),
            request.duration_display,
            getStatusBadge(request.status),
            formatDate(request.applied_date),
            <div key={request.id + '-actions'} className="flex gap-2">
                <Button
                    onClick={() => handleEdit(request)}
                    variant="outline"
                    size="sm"
                >
                    <Edit className="h-4 w-4" />
                </Button>
                <Button
                    onClick={() => handleDelete(request.id)}
                    variant="danger"
                    size="sm"
                >
                    <Trash2 className="h-4 w-4" />
                </Button>
            </div>
        ]
    }));

    // Initial load
    useEffect(() => {
        fetchRequests(1);
    }, [fetchRequests]);

    if (loading && requests.length === 0) {
        return <Loader />;
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="text-red-800">{error}</div>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Search bar and Create button */}
            <div className="flex items-center justify-between gap-4">
                <div className="flex-1 max-w-md">
                    <SearchInput
                        value={searchValue}
                        onChange={handleSearchChange}
                        placeholder="Search leave requests..."
                    />
                </div>
                <Button
                    onClick={onCreateRequest}
                    className="flex items-center gap-2"
                >
                    <Plus className="h-4 w-4" />
                    Request Leave
                </Button>
            </div>

            {/* Table - only show if we have data */}
            {filteredRequests.length > 0 && (
                <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
                    <Table
                        headers={headers}
                        rows={rows}
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={handlePageChange}
                        itemsPerPage={10}
                        totalItems={totalItems}
                    />
                </div>
            )}

            {filteredRequests.length === 0 && !loading && (
                <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                    <div className="text-gray-500 mb-4">
                        {searchValue ? 'No leave requests found matching your search.' : 'No leave requests found.'}
                    </div>
                    {!searchValue && (
                        <Button onClick={onCreateRequest} className="mx-auto">
                            Create Your First Leave Request
                        </Button>
                    )}
                </div>
            )}
        </div>
    );
};

export default LeaveRequestTable;