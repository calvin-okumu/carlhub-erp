"use client";

import type { LeaveRequest } from '@/api/types';
import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import StatusBadge from '@/components/ui/StatusBadge';
import {
    AlertCircle,
    Calendar,
    CheckCircle,
    Clock,
    Eye,
    FileText,
    User,
    X,
} from 'lucide-react';
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

    // FIXED FILTER LOGIC
    const filteredRequests = useMemo(() => {
        return leaveRequests.filter(request => {
            const matchesSearch = request.employee_name
                ?.toLowerCase()
                .includes(searchValue.toLowerCase());

            const matchesStatus =
                statusFilter === "all"
                    ? true
                    : statusFilter === "pending"
                        ? request.status.startsWith("pending")
                        : request.status === statusFilter;

            return matchesSearch && matchesStatus;
        });
    }, [leaveRequests, searchValue, statusFilter]);

    const itemsPerPage = 10;
    const totalPages = Math.ceil(filteredRequests.length / itemsPerPage);

    const visibleRequests = useMemo(() => {
        return filteredRequests.slice(
            (page - 1) * itemsPerPage,
            page * itemsPerPage
        );
    }, [filteredRequests, page]);

    const handleApprove = useCallback((slug: string) => {
        if (confirm("Approve this leave request?")) onApprove(slug);
    }, [onApprove]);

    const handleReject = useCallback((slug: string) => {
        if (confirm("Reject this leave request?")) onReject(slug);
    }, [onReject]);

    const toggleDetails = useCallback((r: LeaveRequest) => {
        setExpandedRequestId(prev => (prev === r.id ? null : r.id));
    }, []);

    const formatDate = (date: string) =>
        new Date(date).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
        });

    const getLeaveTypeIcon = (type: string) => {
        const map = {
            annual_leave: Calendar,
            sick_leave: AlertCircle,
            personal_leave: User,
            maternity_leave: Calendar,
            emergency_leave: AlertCircle,
            unpaid_leave: Clock,
        };
        return map[type as keyof typeof map] || FileText;
    };

    if (loading) return <Loader />;

    if (filteredRequests.length === 0) {
        return (
            <div className="bg-white rounded-xl p-12 text-center shadow">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <AlertCircle className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">No leave requests found</h3>
                <p className="text-sm text-gray-500">
                    {searchValue
                        ? `No matching results for "${searchValue}"`
                        : "No leave requests for now."}
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {visibleRequests.map(request => {
                const Icon = getLeaveTypeIcon(request.leave_type);
                const expanded = expandedRequestId === request.id;
                const single = request.start_date === request.end_date;

                return (
                    <div
                        key={request.id}
                        className="bg-white rounded-xl border shadow-sm hover:shadow transition-all duration-200"
                    >
                        <div className="p-6">
                            {/* TOP ROW */}
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-gray-50 rounded-lg">
                                        <User className="w-6 h-6 text-gray-600" />
                                    </div>

                                    <div>
                                        <h3 className="font-semibold text-gray-900 text-lg">
                                            {request.employee_name}
                                        </h3>

                                        <div className="flex items-center gap-2 mt-1">
                                            <Icon className="w-4 h-4 text-gray-500" />
                                            <span className="text-sm text-gray-600 capitalize">
                                                {request.leave_type.replace("_", " ")}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="text-right">
                                    <StatusBadge status={request.status} />

                                    <div className="text-sm text-gray-600 mt-1">
                                        {request.days_requested} {request.days_requested === 1 ? "day" : "days"}
                                    </div>
                                </div>
                            </div>

                            {/* DATE ROW */}
                            <div className="flex items-center gap-6 mb-4 text-sm text-gray-700">
                                <div className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4 text-gray-400" />
                                    <span>{formatDate(request.start_date)}</span>
                                    {!single && (
                                        <>
                                            <span className="text-gray-400">→</span>
                                            <span>{formatDate(request.end_date)}</span>
                                        </>
                                    )}
                                </div>

                                <div className="flex items-center gap-2">
                                    <Clock className="w-4 h-4 text-gray-400" />
                                    <span>Applied {formatDate(request.applied_date)}</span>
                                </div>
                            </div>

                            {/* REASON BOX */}
                            {request.reason && (
                                <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-100">
                                    <div className="flex items-start gap-2">
                                        <FileText className="w-4 h-4 text-gray-400 mt-0.5" />
                                        <p className="text-sm text-gray-700 line-clamp-2">
                                            {request.reason}
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* ACTIONS */}
                            <div className="flex items-center justify-between pt-2">
                                <Button
                                    variant="secondary"
                                    size="sm"
                                    onClick={() => toggleDetails(request)}
                                    className="flex items-center gap-2"
                                >
                                    <Eye className="h-4 w-4" />
                                    {expanded ? "Hide Details" : "View Details"}
                                </Button>

                                {request.status === "pending" && (
                                    <div className="flex items-center gap-2">
                                        <Button
                                            onClick={() => handleApprove(request.slug)}
                                            size="sm"
                                            disabled={approvingId === request.slug}
                                            className="flex items-center gap-2"
                                        >
                                            {approvingId === request.slug ? (
                                                <div className="w-4 h-4 border-2 border-green-600 border-t-transparent rounded-full animate-spin" />
                                            ) : (
                                                <CheckCircle className="h-4 w-4" />
                                            )}
                                            Approve
                                        </Button>

                                        <Button
                                            onClick={() => handleReject(request.slug)}
                                            size="sm"
                                            variant="danger"
                                            disabled={rejectingId === request.slug}
                                            className="flex items-center gap-2"
                                        >
                                            {rejectingId === request.slug ? (
                                                <div className="w-4 h-4 border-2 border-red-600 border-t-transparent rounded-full animate-spin" />
                                            ) : (
                                                <X className="h-4 w-4" />
                                            )}
                                            Reject
                                        </Button>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* EXPANDABLE DETAILS */}
                        {expanded && (
                            <div className="border-t bg-gray-50 p-4 animate-fadeIn">
                                <LeaveRequestDetails
                                    request={request}
                                    isOpen
                                    onToggle={() => setExpandedRequestId(null)}
                                />
                            </div>
                        )}
                    </div>
                );
            })}

            {/* PAGINATION */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between bg-white rounded-xl border shadow-sm p-4">
                    <div className="text-sm text-gray-600">
                        Showing {(page - 1) * itemsPerPage + 1}–
                        {Math.min(page * itemsPerPage, filteredRequests.length)} of{" "}
                        {filteredRequests.length}
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

                        <span className="text-sm text-gray-600">
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
