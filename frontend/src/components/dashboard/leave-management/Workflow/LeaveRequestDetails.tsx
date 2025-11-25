"use client";

import { useState } from 'react';
import { Eye, Clock, CheckCircle, XCircle, User, Calendar, MessageSquare } from 'lucide-react';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import WorkflowStatus from './WorkflowStatus';
import ApprovalActions from './ApprovalActions';
import type { LeaveRequest } from '@/api/types';
import { formatStatus } from '@/utils/leave';

interface LeaveRequestDetailsProps {
    leaveRequest: LeaveRequest;
    onRefresh?: () => void;
    showApprovalActions?: boolean;
}

export default function LeaveRequestDetails({ 
    leaveRequest, 
    onRefresh, 
    showApprovalActions = false 
}: LeaveRequestDetailsProps) {
    const [showWorkflowModal, setShowWorkflowModal] = useState(false);

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            month: 'long', 
            day: 'numeric', 
            year: 'numeric' 
        });
    };

    const getLeaveTypeIcon = (leaveType: string) => {
        const icons = {
            annual_leave: Calendar,
            sick_leave: Clock,
            personal_leave: User,
            maternity_leave: Calendar,
            emergency_leave: Clock,
            unpaid_leave: Calendar,
        };
        return icons[leaveType as keyof typeof icons] || Calendar;
    };

    const LeaveTypeIcon = getLeaveTypeIcon(leaveRequest.leave_type);

    return (
        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-50 rounded-lg">
                        <LeaveTypeIcon className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                            {formatStatus(leaveRequest.leave_type)}
                        </h3>
                        <p className="text-sm text-gray-500">
                            Applied on {formatDate(leaveRequest.applied_date)}
                        </p>
                    </div>
                </div>
                
                <div className="flex items-center space-x-2">
                    {/* View Workflow Button */}
                    <Button
                        onClick={() => setShowWorkflowModal(true)}
                        variant="outline"
                        size="sm"
                        className="flex items-center"
                    >
                        <Eye className="w-4 h-4 mr-2" />
                        View Workflow
                    </Button>
                    
                    {/* Approval Actions */}
                    {showApprovalActions && (
                        <ApprovalActions
                            leaveRequest={leaveRequest}
                            onActionComplete={onRefresh}
                        />
                    )}
                </div>
            </div>

            {/* Request Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Left Column */}
                <div className="space-y-4">
                    <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Employee</h4>
                        <div className="flex items-center space-x-2">
                            <User className="w-4 h-4 text-gray-400" />
                            <span className="font-medium text-gray-900">{leaveRequest.employee_name}</span>
                        </div>
                    </div>

                    <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Duration</h4>
                        <div className="flex items-center space-x-2">
                            <Calendar className="w-4 h-4 text-gray-400" />
                            <span className="font-medium text-gray-900">{leaveRequest.duration_display}</span>
                        </div>
                    </div>

                    <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Leave Type</h4>
                        <div className="font-medium text-gray-900">
                            {formatStatus(leaveRequest.leave_type)}
                        </div>
                    </div>
                </div>

                {/* Right Column */}
                <div className="space-y-4">
                    <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Start Date</h4>
                        <div className="font-medium text-gray-900">
                            {formatDate(leaveRequest.start_date)}
                        </div>
                    </div>

                    <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">End Date</h4>
                        <div className="font-medium text-gray-900">
                            {formatDate(leaveRequest.end_date)}
                        </div>
                    </div>

                    <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Status</h4>
                        <div className="flex items-center space-x-2">
                            {leaveRequest.workflow_status.is_approved && (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                            )}
                            {leaveRequest.workflow_status.is_pending && (
                                <Clock className="w-4 h-4 text-yellow-500" />
                            )}
                            {leaveRequest.workflow_status.is_rejected && (
                                <XCircle className="w-4 h-4 text-red-500" />
                            )}
                            <span className="font-medium text-gray-900">
                                {leaveRequest.workflow_status.current_status}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Reason */}
            {leaveRequest.reason && (
                <div>
                    <h4 className="text-sm font-medium text-gray-500 mb-2 flex items-center">
                        <MessageSquare className="w-4 h-4 mr-2" />
                        Reason
                    </h4>
                    <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-gray-700">{leaveRequest.reason}</p>
                    </div>
                </div>
            )}

            {/* Current Approver Info */}
            {leaveRequest.current_approver && (
                <div>
                    <h4 className="text-sm font-medium text-gray-500 mb-2">Current Approver</h4>
                    <div className="flex items-center space-x-2 bg-blue-50 p-3 rounded-lg">
                        <User className="w-4 h-4 text-blue-600" />
                        <span className="font-medium text-blue-900">{leaveRequest.current_approver}</span>
                    </div>
                </div>
            )}

            {/* Approval Notes */}
            {leaveRequest.approval_notes && (
                <div>
                    <h4 className="text-sm font-medium text-gray-500 mb-2">Approval Notes</h4>
                    <div className="bg-green-50 p-4 rounded-lg">
                        <p className="text-green-700">{leaveRequest.approval_notes}</p>
                    </div>
                </div>
            )}

            {/* Workflow Modal */}
            <Modal
                isOpen={showWorkflowModal}
                onClose={() => setShowWorkflowModal(false)}
                title="Approval Workflow Status"
                size="lg"
            >
                <WorkflowStatus workflowStatus={leaveRequest.workflow_status} />
            </Modal>
        </div>
    );
}