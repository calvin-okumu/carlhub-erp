"use client";

import type { LeaveRequest } from '@/api/types';
import StatusBadge from '@/components/ui/StatusBadge';
import { AlertCircle, Calendar, CheckCircle, ChevronDown, ChevronUp, Clock, FileText, Mail, TrendingUp, User } from 'lucide-react';

interface LeaveRequestDetailsProps {
    request: LeaveRequest;
    isOpen: boolean;
    onToggle: () => void;
}

const ApprovalStage = ({
    name,
    completed,
    isCurrent,
    description
}: {
    name: string;
    completed: boolean;
    isCurrent: boolean;
    description?: string;
}) => {
    const getStageColor = () => {
        if (completed) return 'text-green-600 bg-green-100 border-green-200';
        if (isCurrent) return 'text-blue-600 bg-blue-100 border-blue-200';
        return 'text-gray-400 bg-gray-100 border-gray-200';
    };

    return (
        <div className="flex flex-col items-center group">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-200 ${getStageColor()} group-hover:scale-110`}>
                {completed ? (
                    <CheckCircle className="w-5 h-5" />
                ) : (
                    <User className="w-5 h-5" />
                )}
            </div>
            <div className="mt-2 text-center">
                <span className="text-xs font-medium text-gray-900 block">{name}</span>
                {description && (
                    <span className="text-xs text-gray-500 block max-w-16 truncate">{description}</span>
                )}
            </div>
        </div>
    );
};

export default function LeaveRequestDetails({ request, isOpen, onToggle }: LeaveRequestDetailsProps) {
    const stages = [
        { name: 'Employee', completed: true, description: 'Submitted' },
        { name: 'Supervisor', completed: request.status !== 'pending', description: 'Manager Review' },
        { name: 'Department', completed: ['approved', 'rejected'].includes(request.status), description: 'Department Head' },
        { name: 'HR', completed: request.status === 'approved', description: 'HR Verification' },
        { name: 'GM', completed: false, description: 'Final Approval' },
    ];

    const getCurrentStageIndex = () => {
        if (request.status === 'pending') return 1;
        if (request.status === 'approved') return 3;
        if (request.status === 'rejected') return 2;
        return 0;
    };

    const currentStageIndex = getCurrentStageIndex();

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
            sick_leave: AlertCircle,
            personal_leave: User,
            maternity_leave: Calendar,
            emergency_leave: AlertCircle,
            unpaid_leave: Clock,
        };
        return icons[leaveType as keyof typeof icons] || FileText;
    };

    const LeaveTypeIcon = getLeaveTypeIcon(request.leave_type);

    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            {/* Toggle Header */}
            <button
                onClick={onToggle}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors bg-gradient-to-r from-gray-50 to-white"
            >
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                        <FileText className="h-4 w-4 text-blue-600" />
                    </div>
                    <div className="text-left">
                        <span className="font-semibold text-gray-900">Leave Request Details</span>
                        <p className="text-xs text-gray-500 mt-0.5">Complete request information and workflow</p>
                    </div>
                </div>
                {isOpen ? (
                    <ChevronUp className="h-5 w-5 text-gray-500" />
                ) : (
                    <ChevronDown className="h-5 w-5 text-gray-500" />
                )}
            </button>

            {/* Dropdown Content */}
            {isOpen && (
                <div className="border-t border-gray-100 bg-gradient-to-b from-gray-50/50 to-white">
                    <div className="p-6 space-y-6">
                        {/* Employee and Leave Type Card */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                                <div className="flex items-center gap-2 mb-2">
                                    <User className="h-4 w-4 text-gray-500" />
                                    <label className="text-xs font-semibold text-gray-700 uppercase tracking-wide">Employee</label>
                                </div>
                                <div className="text-sm font-medium text-gray-900">
                                    {request.employee_name || 'Unknown Employee'}
                                </div>
                            </div>

                            <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                                <div className="flex items-center gap-2 mb-2">
                                    <LeaveTypeIcon className="h-4 w-4 text-gray-500" />
                                    <label className="text-xs font-semibold text-gray-700 uppercase tracking-wide">Leave Type</label>
                                </div>
                                <div className="text-sm font-medium text-gray-900 capitalize">
                                    {request.leave_type?.replace('_', ' ') || 'Unknown Type'}
                                </div>
                            </div>
                        </div>

                        {/* Date Information Card */}
                        <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                            <div className="flex items-center gap-2 mb-3">
                                <Calendar className="h-4 w-4 text-blue-600" />
                                <label className="text-xs font-semibold text-blue-700 uppercase tracking-wide">Leave Period</label>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <div className="text-xs text-blue-600 font-medium mb-1">Start Date</div>
                                    <div className="text-sm font-semibold text-gray-900">
                                        {request.start_date ? formatDate(request.start_date) : '-'}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs text-blue-600 font-medium mb-1">End Date</div>
                                    <div className="text-sm font-semibold text-gray-900">
                                        {request.end_date ? formatDate(request.end_date) : '-'}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs text-blue-600 font-medium mb-1">Duration</div>
                                    <div className="text-sm font-semibold text-gray-900">
                                        {request.days_requested || 0} {request.days_requested === 1 ? 'day' : 'days'}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Status and Applied Date */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                                <div className="flex items-center gap-2 mb-2">
                                    <TrendingUp className="h-4 w-4 text-gray-500" />
                                    <label className="text-xs font-semibold text-gray-700 uppercase tracking-wide">Status</label>
                                </div>
                                <div className="flex items-center">
                                    <StatusBadge status={request.status} />
                                </div>
                            </div>

                            <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                                <div className="flex items-center gap-2 mb-2">
                                    <Clock className="h-4 w-4 text-gray-500" />
                                    <label className="text-xs font-semibold text-gray-700 uppercase tracking-wide">Applied Date</label>
                                </div>
                                <div className="text-sm font-medium text-gray-900">
                                    {request.applied_date ? formatDate(request.applied_date) : '-'}
                                </div>
                            </div>
                        </div>

                        {/* Reason/Description */}
                        {request.reason && (
                            <div className="bg-amber-50 rounded-lg p-4 border border-amber-100">
                                <div className="flex items-center gap-2 mb-3">
                                    <FileText className="h-4 w-4 text-amber-600" />
                                    <label className="text-xs font-semibold text-amber-700 uppercase tracking-wide">Reason for Leave</label>
                                </div>
                                <div className="text-sm text-gray-800 leading-relaxed bg-white rounded-lg p-3 border border-amber-200">
                                    {request.reason}
                                </div>
                            </div>
                        )}

                        {/* Approval Flow */}
                        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-100">
                            <div className="flex items-center gap-2 mb-4">
                                <CheckCircle className="h-4 w-4 text-green-600" />
                                <label className="text-xs font-semibold text-green-700 uppercase tracking-wide">Approval Workflow</label>
                            </div>
                            <div className="relative">
                                {/* Progress Line */}
                                <div className="absolute top-5 left-0 right-0 h-1 bg-gray-200 rounded-full"></div>
                                <div
                                    className="absolute top-5 left-0 h-1 bg-gradient-to-r from-green-400 to-green-500 rounded-full transition-all duration-500"
                                    style={{
                                        width: `${(stages.filter(s => s.completed).length / stages.length) * 100}%`
                                    }}
                                ></div>

                                {/* Stages */}
                                <div className="relative flex justify-between">
                                    {stages.map((stage, index) => (
                                        <div key={stage.name} className="relative z-10">
                                            <ApprovalStage
                                                name={stage.name}
                                                completed={stage.completed}
                                                isCurrent={index === currentStageIndex}
                                                description={stage.description}
                                            />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Approval Notes */}
                        {request.approval_notes && (
                            <div className="bg-purple-50 rounded-lg p-4 border border-purple-100">
                                <div className="flex items-center gap-2 mb-3">
                                    <Mail className="h-4 w-4 text-purple-600" />
                                    <label className="text-xs font-semibold text-purple-700 uppercase tracking-wide">Approval Notes</label>
                                </div>
                                <div className="text-sm text-gray-800 leading-relaxed bg-white rounded-lg p-3 border border-purple-200">
                                    {request.approval_notes}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
