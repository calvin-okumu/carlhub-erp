"use client";

import { Clock, Edit, Trash2, Calendar, User, AlertCircle, CheckCircle, XCircle, Timer } from 'lucide-react';
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
            pending: { 
                bg: "bg-yellow-50", 
                border: "border-yellow-200", 
                text: "text-yellow-800", 
                icon: Timer,
                label: "Pending" 
            },
            approved: { 
                bg: "bg-green-50", 
                border: "border-green-200", 
                text: "text-green-800", 
                icon: CheckCircle,
                label: "Approved" 
            },
            rejected: { 
                bg: "bg-red-50", 
                border: "border-red-200", 
                text: "text-red-800", 
                icon: XCircle,
                label: "Rejected" 
            },
            cancelled: { 
                bg: "bg-gray-50", 
                border: "border-gray-200", 
                text: "text-gray-800", 
                icon: XCircle,
                label: "Cancelled" 
            },
            taken: { 
                bg: "bg-blue-50", 
                border: "border-blue-200", 
                text: "text-blue-800", 
                icon: CheckCircle,
                label: "Taken" 
            }
        };

        const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
        const StatusIcon = config.icon;

        return (
            <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${config.border} ${config.bg}`}>
                <StatusIcon className={`w-3.5 h-3.5 ${config.text}`} />
                <span className={`text-xs font-medium ${config.text}`}>
                    {config.label}
                </span>
            </div>
        );
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
        return icons[leaveType as keyof typeof icons] || Calendar;
    };

    const formatLeaveType = (leaveType: string) => {
        return leaveType.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
        });
    };

    const headers = ["Leave Type", "Duration", "Dates", "Reason", "Status", "Actions"];

    const rows = filteredRequests.map(request => {
        const LeaveTypeIcon = getLeaveTypeIcon(request.leave_type);
        const isSingleDay = request.start_date === request.end_date;
        
        return {
            key: request.id,
            data: [
                // Leave Type with icon
                <div key={request.id + '-type'} className="flex items-center gap-2">
                    <div className="p-1.5 bg-gray-100 rounded-lg">
                        <LeaveTypeIcon className="w-4 h-4 text-gray-600" />
                    </div>
                    <div>
                        <div className="font-medium text-gray-900">
                            {formatLeaveType(request.leave_type)}
                        </div>
                        <div className="text-xs text-gray-500">
                            {request.days_requested} {request.days_requested === 1 ? 'day' : 'days'}
                        </div>
                    </div>
                </div>,
                
                // Duration
                <div key={request.id + '-duration'} className="text-center">
                    <div className="font-medium text-gray-900">
                        {request.days_requested}
                    </div>
                    <div className="text-xs text-gray-500">
                        {request.days_requested === 1 ? 'day' : 'days'}
                    </div>
                </div>,
                
                // Dates
                <div key={request.id + '-dates'} className="text-sm">
                    <div className="font-medium text-gray-900">
                        {formatDate(request.start_date)}
                    </div>
                    {!isSingleDay && (
                        <div className="text-xs text-gray-500">
                            to {formatDate(request.end_date)}
                        </div>
                    )}
                    {isSingleDay && (
                        <div className="text-xs text-gray-500">Single day</div>
                    )}
                </div>,
                
                // Reason
                <div key={request.id + '-reason'} className="max-w-xs">
                    <div className="text-sm text-gray-900 truncate" title={request.reason}>
                        {request.reason || <span className="text-gray-400 italic">No reason provided</span>}
                    </div>
                </div>,
                
                // Status
                <div key={request.id + '-status'} className="flex justify-center">
                    {getStatusBadge(request.status)}
                </div>,
                
                // Actions
                <div key={request.id + '-actions'} className="flex gap-1.5 justify-center">
                    {/* Edit button - available for pending and approved requests */}
                    {(request.status === 'pending' || request.status === 'approved') && (
                        <Button
                            onClick={() => handleEdit(request.id)}
                            variant="outline"
                            size="sm"
                            className="p-2 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600 transition-colors duration-200"
                            title="Edit request"
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
                            className="p-2 hover:bg-yellow-50 hover:border-yellow-300 hover:text-yellow-600 transition-colors duration-200"
                            title="Cancel request"
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
                            className="p-2 hover:bg-red-50 hover:border-red-300 transition-colors duration-200"
                            title="Delete request"
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    )}
                </div>
            ]
        };
    });

    if (loading) {
        return <Loader />;
    }

    if (error) {
        return <div className="text-red-500">{error}</div>;
    }

    return (
        <div className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden border border-gray-100">
            {/* Search Bar */}
            <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-white">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-semibold text-gray-900">Leave Requests</h2>
                        <p className="text-sm text-gray-500 mt-1">
                            {filteredRequests.length} {filteredRequests.length === 1 ? 'request' : 'requests'} found
                        </p>
                    </div>
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Search requests..."
                            value={searchValue}
                            onChange={(e) => setSearchValue(e.target.value)}
                            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
                        />
                        <User className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                    </div>
                </div>
            </div>
            
            {filteredRequests.length === 0 ? (
                <div className="p-12 text-center">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Calendar className="w-8 h-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                        {searchValue ? 'No matching requests' : 'No leave requests'}
                    </h3>
                    <p className="text-sm text-gray-500">
                        {searchValue 
                            ? `No leave requests found matching "${searchValue}"`
                            : 'Get started by creating your first leave request'
                        }
                    </p>
                </div>
            ) : (
                <div className="overflow-x-auto">
                    <Table
                        headers={headers}
                        rows={rows}
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={onPageChange}
                        itemsPerPage={itemsPerPage}
                        totalItems={totalItems}
                    />
                </div>
            )}
        </div>
    );
}
