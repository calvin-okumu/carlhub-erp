"use client";

import type { LeaveRequest } from '@/api/types';
import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import StatusBadge from '@/components/ui/StatusBadge';
import { AlertCircle, Calendar, CheckCircle, Clock, Eye, FileText, User, X } from 'lucide-react';
import React, { useCallback, useMemo, useState } from 'react';
import LeaveRequestDetails from './LeaveRequestDetails';

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

    const handleApprove = useCallback((requestSlug: string) => {
        if (confirm("Are you sure you want to approve this leave request?")) {
            onApprove(requestSlug);
        }
    }, [onApprove]);

    const handleReject = useCallback((requestSlug: string) => {
        if (confirm("Are you sure you want to reject this leave request?")) {
            onReject(requestSlug);
        }
    }, [onReject]);

    const handleViewDetails = useCallback((request: LeaveRequest) => {
        setExpandedRequestId(expandedRequestId === request.id ? null : request.id);
    }, [expandedRequestId]);

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    const getLeaveTypeIcon = (leaveType: string) => {
        const icons = {
            annual_leave: Calendar,
            sick_leave: AlertCircle,
            personal_leave: User,
            maternity_leave: Calendar,
            emergency_leave: AlertCircle,
            unpaid_leave: Clock,
        };
        return icons[leaveType as keyof typeof icons] || FileText;
    };

    const getStatusColor = (status: string) => {
        const colors = {
            pending: 'text-yellow-600 bg-yellow-50 border-yellow-200',
            approved: 'text-green-600 bg-green-50 border-green-200',
            rejected: 'text-red-600 bg-red-50 border-red-200',
            cancelled: 'text-gray-600 bg-gray-50 border-gray-200',
            taken: 'text-blue-600 bg-blue-50 border-blue-200',
        };
        return colors[status as keyof typeof colors] || colors.pending;
    };

    if (loading) {
        return <Loader />;
    }

    if (filteredRequests.length === 0) {
        return (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-12 text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <AlertCircle className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No leave requests found</h3>
                <p className="text-sm text-gray-500">
                    {searchValue
                        ? `No requests matching "${searchValue}"`
                        : 'No leave requests to review at this time'
                    }
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {visibleRequests.map((request) => {
                const LeaveTypeIcon = getLeaveTypeIcon(request.leave_type);
                const isExpanded = expandedRequestId === request.id;
                const statusColorClass = getStatusColor(request.status);
                const isSingleDay = request.start_date === request.end_date;

                return (
                    <div key={request.id} className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden">
                        {/* Main Card Content */}
                        <div className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                {/* Employee and Leave Type */}
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-gray-50 rounded-lg">
                                        <User className="w-6 h-6 text-gray-600" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900 text-lg">
                                            {request.employee_name || 'Unknown Employee'}
                                        </h3>
                                        <div className="flex items-center gap-2 mt-1">
                                            <LeaveTypeIcon className="w-4 h-4 text-gray-500" />
                                            <span className="text-sm text-gray-600 capitalize">
                                                {request.leave_type?.replace('_', ' ') || 'Unknown Type'}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Status and Duration */}
                                <div className="text-right">
                                    <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${statusColorClass} mb-2`}>
                                        <StatusBadge status={request.status} />
                                    </div>
                                    <div className="text-sm text-gray-600">
                                        {request.days_requested || 0} {request.days_requested === 1 ? 'day' : 'days'}
                                    </div>
                                </div>
                            </div>

                            {/* Dates Row */}
                            <div className="flex items-center gap-6 mb-4 text-sm">
                                <div className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4 text-gray-400" />
                                    <span className="text-gray-900 font-medium">
                                        {formatDate(request.start_date)}
                                    </span>
                                    {!isSingleDay && (
                                        <>
                                            <span className="text-gray-400">→</span>
                                            <span className="text-gray-900 font-medium">
                                                {formatDate(request.end_date)}
                                            </span>
                                        </>
                                    )}
                                </div>
                                <div className="flex items-center gap-2">
                                    <Clock className="w-4 h-4 text-gray-400" />
                                    <span className="text-gray-600">
                                        Applied {formatDate(request.applied_date)}
                                    </span>
                                </div>
                            </div>

                            {/* Reason Preview */}
                            {request.reason && (
                                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-start gap-2">
                                        <FileText className="w-4 h-4 text-gray-400 mt-0.5" />
                                        <p className="text-sm text-gray-700 line-clamp-2">
                                            {request.reason}
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* Action Buttons */}
                            <div className="flex items-center justify-between">
                                <Button
                                    variant="secondary"
                                    size="sm"
                                    onClick={() => handleViewDetails(request)}
                                    className="flex items-center gap-2 hover:bg-blue-50 hover:border-blue-300"
                                >
                                    <Eye className="h-4 w-4" />
                                    {isExpanded ? 'Hide Details' : 'View Details'}
                                </Button>

                                <div className="flex items-center gap-2">
                                    {request.status === 'pending' && (
                                        <>
                                            <Button
                                                onClick={() => handleApprove(request.slug)}
                                                variant="gradient"
                                                size="sm"
                                                disabled={approvingId === request.slug}
                                                className="flex items-center gap-2 border-green-300 text-green-700 hover:bg-green-50"
                                            >
                                                {approvingId === request.slug ? (
                                                    <>
                                                        <div className="w-4 h-4 border-2 border-green-600 border-t-transparent rounded-full animate-spin"></div>
                                                        Approving...
                                                    </>
                                                ) : (
                                                    <>
                                                        <CheckCircle className="h-4 w-4" />
                                                        Approve
                                                    </>
                                                )}
                                            </Button>
                                            <Button
                                                onClick={() => handleReject(request.slug)}
                                                variant="danger"
                                                size="sm"
                                                disabled={rejectingId === request.slug}
                                                className="flex items-center gap-2 border-red-300 text-red-700 hover:bg-red-50"
                                            >
                                                {rejectingId === request.slug ? (
                                                    <>
                                                        <div className="w-4 h-4 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
                                                        Rejecting...
                                                    </>
                                                ) : (
                                                    <>
                                                        <X className="h-4 w-4" />
                                                        Reject
                                                    </>
                                                )}
                                            </Button>
                                        </>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Expandable Details */}
                        {isExpanded && (
                            <div className="border-t border-gray-100 bg-gray-50/50">
                                <LeaveRequestDetails
                                    request={request}
                                    isOpen={isExpanded}
                                    onToggle={() => setExpandedRequestId(null)}
                                />
                            </div>
                        )}
                    </div>
                );
            })}

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between bg-white rounded-xl border border-gray-200 shadow-sm p-4">
                    <div className="text-sm text-gray-600">
                        Showing {((page - 1) * itemsPerPage) + 1} to {Math.min(page * itemsPerPage, filteredRequests.length)} of {filteredRequests.length} requests
                    </div>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage(page - 1)}
                            disabled={page === 1}
                        >
                            Previous
                        </Button>
                        <span className="px-3 py-1 text-sm text-gray-600">
                            Page {page} of {totalPages}
                        </span>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage(page + 1)}
                            disabled={page === totalPages}
                        >
                            Next
                        </Button>
                    </div>
                </div>
            )}
        </div>
    );
});

export default ApprovalsTable;
