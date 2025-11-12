"use client";

import { CheckCircle, Edit, Trash2, XCircle } from 'lucide-react';
import { useState } from 'react';
import type { LeaveRequest } from '../../../../api/types';
import Loader from '../../../shared/Loader';
import Button from '../../../ui/Button';
import Table from '../../../ui/Table';
import { useLeaveRequests } from './hooks/useLeaveRequests';
import { useTableSelection } from './hooks/useTableSelection';

type LeaveType = 'all' | 'annual_leave' | 'sick_leave' | 'personal_leave' | 'maternity_leave' | 'emergency_leave' | 'unpaid_leave';

interface LeaveRequestTableProps {
    onCreateRequest: () => void;
    onEditRequest: (request: LeaveRequest) => void;
    onDeleteRequest: (id: string) => void;
    searchTerm?: string;
    sortBy?: LeaveType;
}

const LeaveRequestTable = ({
    onCreateRequest,
    onEditRequest,
    onDeleteRequest,
    searchTerm = '',
    sortBy = 'all'
}: LeaveRequestTableProps) => {
    const [quickActionLoading, setQuickActionLoading] = useState<string | null>(null);

    const { requests, loading, error, currentPage, totalPages, totalItems, refetch, setPage } = useLeaveRequests({
        searchTerm,
        sortBy
    });

    const { selectedIds, isSelected, isAllSelected, isSomeSelected, toggleSelect, selectAll, selectedCount } = useTableSelection(requests);

    const formatDate = (dateString: string) =>
        new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });

    const getStatusBadge = (status: string) => {
        const colors = {
            pending: 'bg-yellow-100 text-yellow-800',
            approved: 'bg-green-100 text-green-800',
            rejected: 'bg-red-100 text-red-800',
            cancelled: 'bg-gray-100 text-gray-800',
            taken: 'bg-blue-100 text-blue-800'
        };
        return (
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
            </span>
        );
    };

    const handleQuickAction = async (requestId: string, action: 'approve' | 'reject') => {
        setQuickActionLoading(requestId);
        try {
            console.log(`Quick ${action}ing request:`, requestId);
            await new Promise(resolve => setTimeout(resolve, 500));
            refetch();
        } catch (error) {
            console.error(`Failed to quick ${action}:`, error);
        } finally {
            setQuickActionLoading(null);
        }
    };

    const handleDelete = (id: string) => {
        if (confirm("Are you sure you want to delete this leave request?")) {
            onDeleteRequest(id);
        }
    };

    const headers = [
        <input
            key="select-all"
            type="checkbox"
            checked={isAllSelected}
            ref={(el) => { if (el) el.indeterminate = isSomeSelected; }}
            onChange={(e) => selectAll(e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />,
        "Employee", "Leave Type", "Start Date", "End Date", "Days Requested", "Status", "Applied Date", "Actions"
    ];

    const rows = requests.map(request => ({
        key: request.id,
        data: [
            <input
                key={`checkbox-${request.id}`}
                type="checkbox"
                checked={isSelected(request.id)}
                onChange={() => toggleSelect(request.id)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />,
            request.employee_name,
            request.leave_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            formatDate(request.start_date),
            formatDate(request.end_date),
            request.duration_display,
            getStatusBadge(request.status),
            formatDate(request.applied_date),
            <div key={request.id + '-actions'} className="flex gap-1">
                {request.status === 'pending' && (
                    <>
                        <Button
                            onClick={() => handleQuickAction(request.id, 'approve')}
                            variant="outline"
                            size="sm"
                            disabled={quickActionLoading === request.id}
                            className="text-green-600 hover:bg-green-50 border-green-300"
                        >
                            <CheckCircle className="h-3 w-3" />
                        </Button>
                        <Button
                            onClick={() => handleQuickAction(request.id, 'reject')}
                            variant="outline"
                            size="sm"
                            disabled={quickActionLoading === request.id}
                            className="text-orange-600 hover:bg-orange-50 border-orange-300"
                        >
                            <XCircle className="h-3 w-3" />
                        </Button>
                    </>
                )}
                <Button onClick={() => onEditRequest(request)} variant="outline" size="sm">
                    <Edit className="h-3 w-3" />
                </Button>
                <Button onClick={() => handleDelete(request.id)} variant="danger" size="sm">
                    <Trash2 className="h-3 w-3" />
                </Button>
            </div>
        ]
    }));

    if (loading && requests.length === 0) return <Loader />;

    if (error) return <div className="bg-red-50 border border-red-200 rounded-md p-4"><p className="text-red-800">{error}</p></div>;

    return (
        <div className="space-y-4">
            {requests.length > 0 ? (
                <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
                    <Table
                        headers={headers}
                        rows={rows}
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={setPage}
                        itemsPerPage={10}
                        totalItems={totalItems}
                    />
                </div>
            ) : !loading && (
                <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                    <p className="text-gray-500 mb-4">
                        {searchTerm ? 'No leave requests found matching your search.' : 'No leave requests found.'}
                    </p>
                    {!searchTerm && <Button onClick={onCreateRequest}>Create Your First Leave Request</Button>}
                </div>
            )}
        </div>
    );
};

export default LeaveRequestTable;
