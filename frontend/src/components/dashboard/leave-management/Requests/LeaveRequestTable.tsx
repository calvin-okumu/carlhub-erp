"use client";

import { Clock, Edit, Trash2 } from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';
import type { LeaveRequest } from '../../../../api/types';
import Loader from '../../../shared/Loader';
import Button from '../../../ui/Button';
import Table from '../../../ui/Table';

interface LeaveRequestTableProps {
    leaveRequests: LeaveRequest[];
    loading: boolean;
    error: string | null;
    currentPage: number;
    totalPages: number;
    totalItems: number;
    itemsPerPage: number;
    onPageChange: (page: number) => void;
    onEditRequest: (id: string) => void;
    onCancelRequest: (id: string) => void;
    onDeleteRequest: (id: string) => void;
}

export default function LeaveRequestTable({
    leaveRequests,
    loading,
    error,
    currentPage,
    totalPages,
    totalItems,
    itemsPerPage,
    onPageChange,
    onEditRequest,
    onCancelRequest,
    onDeleteRequest
}: LeaveRequestTableProps) {
    const [searchValue, setSearchValue] = useState('');

    // Client-side search filtering
    const filteredRequests = useMemo(() =>
        leaveRequests.filter(request =>
            request.leave_type.toLowerCase().includes(searchValue.toLowerCase()) ||
            request.employee_name.toLowerCase().includes(searchValue.toLowerCase()) ||
            request.reason.toLowerCase().includes(searchValue.toLowerCase())
        ),
        [leaveRequests, searchValue]
    );

    const handleEdit = useCallback((id: string) => {
        onEditRequest(id);
    }, [onEditRequest]);

    const handleDelete = useCallback((id: string) => {
        if (confirm("Are you sure you want to delete this leave request? This action cannot be undone.")) {
            onDeleteRequest(id);
        }
    }, [onDeleteRequest]);

    const handleCancel = useCallback((id: string) => {
        if (confirm("Are you sure you want to cancel this leave request?")) {
            onCancelRequest(id);
        }
    }, [onCancelRequest]);

    const getStatusBadge = (status: string) => {
        const statusConfig = {
            pending: { bg: "bg-yellow-100", text: "text-yellow-800", label: "Pending" },
            approved: { bg: "bg-green-100", text: "text-green-800", label: "Approved" },
            rejected: { bg: "bg-red-100", text: "text-red-800", label: "Rejected" },
            cancelled: { bg: "bg-gray-100", text: "text-gray-800", label: "Cancelled" },
            taken: { bg: "bg-blue-100", text: "text-blue-800", label: "Taken" }
        };

        const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;

        return (
            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${config.bg} ${config.text}`}>
                {config.label}
            </span>
        );
    };

    const formatLeaveType = (leaveType: string) => {
        return leaveType.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    };

    const headers = ["Leave Type", "Start Date", "End Date", "Reason", "Status", "Actions"];

    const rows = filteredRequests.map(request => ({
        key: request.id,
        data: [
            formatLeaveType(request.leave_type),
            new Date(request.start_date).toLocaleDateString(),
            new Date(request.end_date).toLocaleDateString(),
            <span key={request.id + '-reason'} className="truncate max-w-xs block" title={request.reason}>
                {request.reason || '-'}
            </span>,
            getStatusBadge(request.status),
            <div key={request.id + '-actions'} className="flex gap-2">
                {/* Edit button - available for pending and approved requests */}
                {(request.status === 'pending' || request.status === 'approved') && (
                    <Button
                        onClick={() => handleEdit(request.id)}
                        variant="outline"
                        size="sm"
                    >
                        <Edit className="h-4 w-4" />
                    </Button>
                )}

                {/* Cancel button - available for pending and approved requests */}
                {(request.status === 'pending' || request.status === 'approved') && (
                    <Button
                        onClick={() => handleCancel(request.id)}
                        variant="outline"
                        size="sm"
                    >
                        <Clock className="h-4 w-4" />
                    </Button>
                )}

                {/* Delete button - only available for rejected requests */}
                {request.status === 'rejected' && (
                    <Button
                        onClick={() => handleDelete(request.id)}
                        variant="danger"
                        size="sm"
                    >
                        <Trash2 className="h-4 w-4" />
                    </Button>
                )}
            </div>
        ]
    }));

    if (loading) {
        return <Loader />;
    }

    if (error) {
        return <div className="text-red-500">{error}</div>;
    }

    return (
        <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
            </div>
            {filteredRequests.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                    {searchValue ? `No leave requests found matching "${searchValue}"` : 'No leave requests found'}
                </div>
            ) : (
                <Table
                    headers={headers}
                    rows={rows}
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={onPageChange}
                    itemsPerPage={itemsPerPage}
                    totalItems={totalItems}
                />
            )}
        </div>
    );
}
