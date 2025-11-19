"use client";

import type { LeaveRequest } from '@/api/types';
import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import StatusBadge from '@/components/ui/StatusBadge';
import Table from '@/components/ui/Table';
import LeaveRequestDetails from './LeaveRequestDetails';
import { AlertCircle, CheckCircle, Eye, X } from 'lucide-react';
import React, { useCallback, useMemo, useState } from 'react';

interface ApprovalsTableProps {
    leaveRequests: LeaveRequest[];
    loading: boolean;
    onApprove: (requestId: string) => void;
    onReject: (requestId: string) => void;
    approvingId?: string | null;
    rejectingId?: string | null;
    searchValue: string;
    statusFilter: string;
}

const ApprovalsTable = React.memo(function ApprovalsTable({
    leaveRequests,
    loading,
    onApprove,
    onReject,
    approvingId,
    rejectingId,
    searchValue,
    statusFilter
}: ApprovalsTableProps) {
    const [page, setPage] = useState(1);
    const [expandedRequestId, setExpandedRequestId] = useState<string | null>(null);

    const filteredRequests = useMemo(() =>
        leaveRequests.filter(request =>
            request.employee_name?.toLowerCase().includes(searchValue.toLowerCase()) &&
            (statusFilter === 'all' || request.status === statusFilter)
        ),
        [leaveRequests, searchValue, statusFilter]
    );

    const itemsPerPage = 10;
    const totalPages = useMemo(() =>
        Math.ceil(filteredRequests.length / itemsPerPage),
        [filteredRequests.length, itemsPerPage]
    );
    const visibleRequests = useMemo(() =>
        filteredRequests.slice((page - 1) * itemsPerPage, page * itemsPerPage),
        [filteredRequests, page, itemsPerPage]
    );

    const handleApprove = useCallback((requestId: string) => {
        if (confirm("Are you sure you want to approve this leave request?")) {
            onApprove(requestId);
        }
    }, [onApprove]);

    const handleReject = useCallback((requestId: string) => {
        if (confirm("Are you sure you want to reject this leave request?")) {
            onReject(requestId);
        }
    }, [onReject]);

    const handleViewDetails = useCallback((request: LeaveRequest) => {
        setExpandedRequestId(expandedRequestId === request.id ? null : request.id);
    }, [expandedRequestId]);

    const headers = ["Employee", "Leave Type", "Dates", "Duration", "Status", "Applied Date", "Actions"];

    const rows: { key: string; data: (string | number | React.ReactNode)[] }[] = [];

    visibleRequests.forEach(request => {
        rows.push({
            key: request.id,
            data: [
                request.employee_name || "-",
                request.leave_type || "-",
                `${request.start_date ? new Date(request.start_date).toLocaleDateString() : "-"} - ${request.end_date ? new Date(request.end_date).toLocaleDateString() : "-"}`,
                `${request.days_requested || 0} days`,
                <StatusBadge key={request.id + '-status'} status={request.status} />,
                request.applied_date ? new Date(request.applied_date).toLocaleDateString() : "-",
                <div key={request.id + '-actions'} className="flex gap-2">
                    <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleViewDetails(request)}
                    >
                        <Eye className="h-4 w-4 mr-2" />
                        {expandedRequestId === request.id ? 'Hide' : 'View'}
                    </Button>
                    <Button
                        onClick={() => handleApprove(request.id)}
                        variant="gradient"
                        size="sm"
                        disabled={approvingId === request.id}
                        className="text-green-600 border-green-300 hover:bg-green-50"
                    >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        {approvingId === request.id ? 'Approving...' : 'Approve'}
                    </Button>
                    <Button
                        onClick={() => handleReject(request.id)}
                        variant="danger"
                        size="sm"
                        disabled={rejectingId === request.id}
                        className="text-red-600 border-red-300 hover:bg-red-50"
                    >
                        <X className="h-4 w-4 mr-2" />
                        {rejectingId === request.id ? 'Rejecting...' : 'Reject'}
                    </Button>
                </div>
            ]
        });

        // Add details dropdown row if expanded
        if (expandedRequestId === request.id) {
            rows.push({
                key: request.id + '-details',
                data: [
                    <td key={request.id + '-details-td'} colSpan={7} className="p-0 border-t">
                        <LeaveRequestDetails
                            request={request}
                            isOpen={expandedRequestId === request.id}
                            onToggle={() => setExpandedRequestId(null)}
                        />
                    </td>
                ]
            });
        }
    });

    if (loading) {
        return <Loader />;
    }

    if (filteredRequests.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 mb-4">No leave requests found</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
            <Table
                headers={headers}
                rows={rows}
                currentPage={page}
                totalPages={totalPages}
                onPageChange={setPage}
                itemsPerPage={itemsPerPage}
                totalItems={filteredRequests.length}
            />
        </div>
    );
});

export default ApprovalsTable;
