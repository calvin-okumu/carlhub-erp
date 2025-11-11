"use client";

import { getLeaveRequests } from '@/api/leave';
import type { LeaveRequest, PaginatedResponse } from '@/api/types';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import StatusBadge from '@/components/ui/StatusBadge';
import Table from '@/components/ui/Table';
import { Eye, Edit, Check, X, MoreVertical } from 'lucide-react';
import { useEffect, useState } from 'react';

interface RequestListProps {
    searchValue?: string;
    onViewRequest?: (request: LeaveRequest) => void;
    onEditRequest?: (request: LeaveRequest) => void;
    onApproveRequest?: (request: LeaveRequest) => void;
    onRejectRequest?: (request: LeaveRequest) => void;
    canApprove?: boolean;
}

export default function RequestList({
    searchValue = '',
    onViewRequest,
    onEditRequest,
    onApproveRequest,
    onRejectRequest,
    canApprove = false
}: RequestListProps) {
    const [requests, setRequests] = useState<LeaveRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalItems, setTotalItems] = useState(0);
    const [statusFilter, setStatusFilter] = useState('');
    const [leaveTypeFilter, setLeaveTypeFilter] = useState('');

    const fetchRequests = async (page = 1) => {
        setLoading(true);
        try {
            const params: any = {
                page,
                page_size: 10,
            };

            if (statusFilter) params.status = statusFilter;
            if (leaveTypeFilter) params.leave_type = leaveTypeFilter;
            if (searchValue) {
                // Assuming backend supports search parameter
                params.search = searchValue;
            }

            const response: PaginatedResponse<LeaveRequest> = await getLeaveRequests(params);
            setRequests(response.results);
            setTotalPages(Math.ceil(response.count / 10));
            setTotalItems(response.count);
        } catch (error) {
            console.error('Failed to fetch leave requests:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRequests(currentPage);
    }, [currentPage, statusFilter, leaveTypeFilter, searchValue]);

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
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

    const renderActions = (request: LeaveRequest) => {
        const actions = [];

        if (onViewRequest) {
            actions.push(
                <Button
                    key="view"
                    variant="ghost"
                    size="sm"
                    onClick={() => onViewRequest(request)}
                    className="p-1"
                >
                    <Eye className="h-4 w-4" />
                </Button>
            );
        }

        if (onEditRequest && (request.status === 'pending' || request.status === 'draft')) {
            actions.push(
                <Button
                    key="edit"
                    variant="ghost"
                    size="sm"
                    onClick={() => onEditRequest(request)}
                    className="p-1"
                >
                    <Edit className="h-4 w-4" />
                </Button>
            );
        }

        if (canApprove && request.status === 'pending') {
            if (onApproveRequest) {
                actions.push(
                    <Button
                        key="approve"
                        variant="ghost"
                        size="sm"
                        onClick={() => onApproveRequest(request)}
                        className="p-1 text-green-600 hover:text-green-700"
                    >
                        <Check className="h-4 w-4" />
                    </Button>
                );
            }

            if (onRejectRequest) {
                actions.push(
                    <Button
                        key="reject"
                        variant="ghost"
                        size="sm"
                        onClick={() => onRejectRequest(request)}
                        className="p-1 text-red-600 hover:text-red-700"
                    >
                        <X className="h-4 w-4" />
                    </Button>
                );
            }
        }

        return (
            <div className="flex items-center space-x-1">
                {actions}
            </div>
        );
    };

    const headers = [
        'Employee',
        'Leave Type',
        'Start Date',
        'End Date',
        'Days',
        'Status',
        'Applied Date',
        'Actions'
    ];

    const rows = requests.map((request) => ({
        key: request.id,
        data: [
            request.employee_name,
            request.leave_type,
            formatDate(request.start_date),
            formatDate(request.end_date),
            request.days_requested,
            getStatusBadge(request.status),
            formatDate(request.applied_date),
            renderActions(request)
        ]
    }));

    if (loading) {
        return (
            <div className="flex justify-center items-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Filters */}
            <div className="flex flex-wrap gap-4">
                <Select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="min-w-[150px]"
                >
                    <option value="">All Statuses</option>
                    <option value="pending">Pending</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                    <option value="cancelled">Cancelled</option>
                    <option value="taken">Taken</option>
                </Select>

                <Select
                    value={leaveTypeFilter}
                    onChange={(e) => setLeaveTypeFilter(e.target.value)}
                    className="min-w-[150px]"
                >
                    <option value="">All Types</option>
                    <option value="annual">Annual Leave</option>
                    <option value="sick">Sick Leave</option>
                    <option value="maternity">Maternity Leave</option>
                    <option value="paternity">Paternity Leave</option>
                    <option value="emergency">Emergency Leave</option>
                </Select>
            </div>

            {/* Table */}
            <Table
                headers={headers}
                rows={rows}
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
                totalItems={totalItems}
                itemsPerPage={10}
            />

            {requests.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                    No leave requests found.
                </div>
            )}
        </div>
    );
}