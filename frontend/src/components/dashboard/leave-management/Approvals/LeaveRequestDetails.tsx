"use client";

import type { LeaveRequest } from '@/api/types';
import StatusBadge from '@/components/ui/StatusBadge';
import { Calendar, CheckCircle, ChevronDown, ChevronUp, Clock, FileText, User } from 'lucide-react';

interface LeaveRequestDetailsProps {
    request: LeaveRequest;
    isOpen: boolean;
    onToggle: () => void;
}

const ApprovalStage = ({ name, completed, isCurrent }: { name: string; completed: boolean; isCurrent: boolean }) => {
    const getStageColor = () => {
        if (completed) return 'text-green-600 bg-green-100';
        if (isCurrent) return 'text-blue-600 bg-blue-100';
        return 'text-gray-400 bg-gray-100';
    };

    return (
        <div className="flex flex-col items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${getStageColor()}`}>
                {completed ? (
                    <CheckCircle className="w-4 h-4" />
                ) : (
                    <User className="w-4 h-4" />
                )}
            </div>
            <span className="text-xs text-gray-600 mt-1 text-center">{name}</span>
        </div>
    );
};

export default function LeaveRequestDetails({ request, isOpen, onToggle }: LeaveRequestDetailsProps) {
    const stages = [
        { name: 'Employee', completed: true },
        { name: 'Supervisor', completed: request.status !== 'pending' },
        { name: 'Department', completed: ['approved', 'rejected'].includes(request.status) },
        { name: 'HR', completed: request.status === 'approved' },
        { name: 'GM', completed: false },
    ];

    const getCurrentStageIndex = () => {
        if (request.status === 'pending') return 1;
        if (request.status === 'approved') return 3;
        if (request.status === 'rejected') return 2;
        return 0;
    };

    const currentStageIndex = getCurrentStageIndex();

    return (
        <div className="border border-gray-200 rounded-lg bg-white shadow-sm">
            {/* Toggle Header */}
            <button
                onClick={onToggle}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
                <span className="font-medium text-gray-900">Leave Request Details</span>
                {isOpen ? (
                    <ChevronUp className="h-4 w-4 text-gray-500" />
                ) : (
                    <ChevronDown className="h-4 w-4 text-gray-500" />
                )}
            </button>

            {/* Dropdown Content */}
            {isOpen && (
                <div className="border-t border-gray-200 p-4 space-y-4">
                    {/* Employee Information */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-600 flex items-center gap-1">
                                <User className="h-3 w-3" />
                                Employee Name
                            </label>
                            <div className="p-2 bg-gray-50 rounded text-sm text-gray-900">
                                {request.employee_name || '-'}
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-600">Leave Type</label>
                            <div className="p-2 bg-gray-50 rounded text-sm text-gray-900">
                                {request.leave_type || '-'}
                            </div>
                        </div>
                    </div>

                    {/* Date Information */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-600 flex items-center gap-1">
                                <Calendar className="h-3 w-3" />
                                Start Date
                            </label>
                            <div className="p-2 bg-gray-50 rounded text-sm text-gray-900">
                                {request.start_date ? new Date(request.start_date).toLocaleDateString() : '-'}
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-600">End Date</label>
                            <div className="p-2 bg-gray-50 rounded text-sm text-gray-900">
                                {request.end_date ? new Date(request.end_date).toLocaleDateString() : '-'}
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-600">Duration</label>
                            <div className="p-2 bg-gray-50 rounded text-sm text-gray-900">
                                {request.days_requested || 0} days
                            </div>
                        </div>
                    </div>

                    {/* Status and Applied Date */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-600">Status</label>
                            <div className="p-2 bg-gray-50 rounded">
                                <StatusBadge status={request.status} />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-600 flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                Applied Date
                            </label>
                            <div className="p-2 bg-gray-50 rounded text-sm text-gray-900">
                                {request.applied_date ? new Date(request.applied_date).toLocaleDateString() : '-'}
                            </div>
                        </div>
                    </div>

                    {/* Reason/Description */}
                    <div className="space-y-1">
                        <label className="text-xs font-medium text-gray-600 flex items-center gap-1">
                            <FileText className="h-3 w-3" />
                            Reason/Description
                        </label>
                        <div className="p-2 bg-gray-50 rounded text-sm text-gray-900 min-h-[60px]">
                            {request.reason || 'No reason provided'}
                        </div>
                    </div>

                    {/* Approval Flow */}
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-gray-900">Approval Flow</h4>
                        <div className="flex items-center justify-between relative py-2">
                            {/* Progress Line */}
                            <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200 z-0"></div>
                            <div
                                className="absolute top-5 left-0 h-0.5 bg-green-400 z-0"
                                style={{
                                    width: `${(currentStageIndex / (stages.length - 1)) * 100}%`
                                }}
                            ></div>

                            {/* Stages */}
                            {stages.map((stage, index) => (
                                <div key={stage.name} className="relative z-10">
                                    <ApprovalStage
                                        name={stage.name}
                                        completed={stage.completed}
                                        isCurrent={index === currentStageIndex}
                                    />
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Approval Notes (if any) */}
                    {request.approval_notes && (
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-600">Approval Notes</label>
                            <div className="p-2 bg-gray-50 rounded text-sm text-gray-900">
                                {request.approval_notes}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
