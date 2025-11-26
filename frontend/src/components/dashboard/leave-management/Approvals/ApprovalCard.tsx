import { LeaveRequest } from '@/api/types';
import Button from '@/components/ui/Button';
import StatusBadge from '@/components/ui/StatusBadge';
import { AlertCircle, Calendar, CheckCircle, Clock, Eye, FileText, TrendingUp, User, X } from 'lucide-react';
import { useState } from 'react';

interface LeaveRequestCardProps {
    request: LeaveRequest;
    onViewDetails: (request: LeaveRequest) => void;
    onApprove: (requestId: string) => void;
    onReject: (requestId: string) => void;
    isApproving?: boolean;
    isRejecting?: boolean;
}

export const LeaveRequestCard = ({
    request,
    onViewDetails,
    onApprove,
    onReject,
    isApproving = false,
    isRejecting = false
}: LeaveRequestCardProps) => {
    const [showFullReason, setShowFullReason] = useState(false);

    // Approval stages
    const stages = [
        { name: 'Employee', completed: true, icon: User, description: 'Request submitted' },
        { name: 'Supervisor', completed: request.status !== 'pending', icon: User, description: 'Manager review' },
        { name: 'Department', completed: ['approved', 'rejected'].includes(request.status), icon: User, description: 'Department approval' },
        { name: 'HR', completed: request.status === 'approved', icon: FileText, description: 'HR verification' },
        { name: 'GM', completed: false, icon: User, description: 'Final approval' },
    ];

    const getStageColor = (completed: boolean, isCurrent: boolean) => {
        if (completed) return 'text-green-600 bg-green-100 border-green-200';
        if (isCurrent) return 'text-blue-600 bg-blue-100 border-blue-200';
        return 'text-gray-400 bg-gray-100 border-gray-200';
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

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    const LeaveTypeIcon = getLeaveTypeIcon(request.leave_type);
    const isSingleDay = request.start_date === request.end_date;

    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden">
            {/* Header with gradient background */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 border-b border-gray-100">
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-white rounded-lg shadow-sm">
                            <User className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-gray-900">
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
                    <div className="text-right">
                        <StatusBadge status={request.status} />
                        <div className="mt-2">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                                {request.days_requested || 0} {request.days_requested === 1 ? 'day' : 'days'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
                {/* Date Information */}
                <div className="flex items-center gap-6 text-sm">
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

                {/* Approval Timeline */}
                <div className="space-y-3">
                    <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4" />
                        Approval Progress
                    </h4>
                    <div className="relative">
                        {/* Progress Line */}
                        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200"></div>
                        <div
                            className="absolute top-5 left-0 h-0.5 bg-green-400 transition-all duration-500"
                            style={{
                                width: `${(stages.filter(s => s.completed).length / stages.length) * 100}%`
                            }}
                        ></div>

                        {/* Stages */}
                        <div className="relative flex justify-between">
                            {stages.map((stage, index) => {
                                const Icon = stage.icon;
                                const isCurrent = index === stages.findIndex(s => !s.completed);
                                const stageColor = getStageColor(stage.completed, isCurrent);

                                return (
                                    <div key={stage.name} className="flex flex-col items-center group">
                                        <div className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-200 ${stageColor} group-hover:scale-110`}>
                                            <Icon className="w-5 h-5" />
                                        </div>
                                        <div className="mt-2 text-center">
                                            <span className="text-xs font-medium text-gray-900 block">
                                                {stage.name}
                                            </span>
                                            <span className="text-xs text-gray-500 block max-w-20 truncate">
                                                {stage.description}
                                            </span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* Reason Section */}
                {request.reason && (
                    <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm font-medium text-gray-900">
                            <FileText className="w-4 h-4" />
                            Reason for Leave
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                            <p className={`text-sm text-gray-700 leading-relaxed ${showFullReason ? '' : 'line-clamp-3'}`}>
                                {request.reason}
                            </p>
                            {request.reason.length > 150 && (
                                <button
                                    onClick={() => setShowFullReason(!showFullReason)}
                                    className="text-sm text-blue-600 hover:text-blue-800 mt-2 font-medium"
                                >
                                    {showFullReason ? 'Show less' : 'Show more'}
                                </button>
                            )}
                        </div>
                    </div>
                )}

                {/* Additional Information */}
                {request.approval_notes && (
                    <div className="flex items-center gap-2 text-sm text-amber-600 bg-amber-50 p-3 rounded-lg">
                        <FileText className="w-4 h-4" />
                        <span className="font-medium">Approval notes available</span>
                    </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onViewDetails(request)}
                        className="flex items-center gap-2 hover:bg-blue-50"
                    >
                        <Eye className="w-4 h-4" />
                        View Full Details
                    </Button>

                    {request.status === 'pending' && (
                        <div className="flex items-center gap-3">
                            <Button
                                onClick={() => onApprove(request.id)}
                                variant="outline"
                                size="sm"
                                disabled={isApproving}
                                className="flex items-center gap-2 border-green-300 text-green-700 hover:bg-green-50"
                            >
                                {isApproving ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-green-600 border-t-transparent rounded-full animate-spin"></div>
                                        Approving...
                                    </>
                                ) : (
                                    <>
                                        <CheckCircle className="w-4 h-4" />
                                        Approve
                                    </>
                                )}
                            </Button>
                            <Button
                                onClick={() => onReject(request.id)}
                                variant="outline"
                                size="sm"
                                disabled={isRejecting}
                                className="flex items-center gap-2 border-red-300 text-red-700 hover:bg-red-50"
                            >
                                {isRejecting ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
                                        Rejecting...
                                    </>
                                ) : (
                                    <>
                                        <X className="w-4 h-4" />
                                        Reject
                                    </>
                                )}
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
