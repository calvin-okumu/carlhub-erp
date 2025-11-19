import { useState } from 'react';
import Button from '@/components/ui/Button';
import StatusBadge from '@/components/ui/StatusBadge';
import { LeaveRequest } from '@/api/types';
import { CheckCircle, Clock, User, FileText, Eye, X } from 'lucide-react';

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
        { name: 'Employee', completed: true, icon: User },
        { name: 'Supervisor', completed: request.status !== 'pending', icon: User },
        { name: 'Department', completed: ['approved', 'rejected'].includes(request.status), icon: User },
        { name: 'HR', completed: request.status === 'approved', icon: FileText },
        { name: 'GM', completed: false, icon: User },
    ];

    const getStageColor = (completed: boolean, isCurrent: boolean) => {
        if (completed) return 'text-green-600 bg-green-100';
        if (isCurrent) return 'text-blue-600 bg-blue-100';
        return 'text-gray-400 bg-gray-100';
    };

    return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{request.employee_name}</h3>
                    <p className="text-sm text-gray-600">{request.leave_type}</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                            {new Date(request.start_date).toLocaleDateString()} - {new Date(request.end_date).toLocaleDateString()}
                        </p>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {request.days_requested} days
                        </span>
                    </div>
                    <StatusBadge status={request.status} />
                </div>
            </div>

            {/* Status Timeline */}
            <div className="mb-4">
                <div className="flex items-center justify-between">
                    {stages.map((stage, index) => {
                        const Icon = stage.icon;
                        const isCurrent = index === 1 && request.status === 'pending'; // Assuming supervisor is current for pending

                        return (
                            <div key={stage.name} className="flex flex-col items-center">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${getStageColor(stage.completed, isCurrent)}`}>
                                    <Icon className="w-5 h-5" />
                                </div>
                                <span className="text-xs text-gray-600 mt-1 text-center">{stage.name}</span>
                                {index < stages.length - 1 && (
                                    <div className={`w-8 h-0.5 mt-2 ${stage.completed ? 'bg-green-400' : 'bg-gray-300'}`} />
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Metadata */}
            <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        Submitted {new Date(request.applied_date).toLocaleDateString()}
                    </span>
                    {request.approval_notes && (
                        <span className="flex items-center gap-1">
                            <FileText className="w-4 h-4" />
                            Has notes
                        </span>
                    )}
                </div>
            </div>

            {/* Reason Preview */}
            {request.reason && (
                <div className="mb-4">
                    <p className={`text-sm text-gray-700 ${showFullReason ? '' : 'line-clamp-2'}`}>
                        {request.reason}
                    </p>
                    {request.reason.length > 100 && (
                        <button
                            onClick={() => setShowFullReason(!showFullReason)}
                            className="text-sm text-blue-600 hover:text-blue-800 mt-1"
                        >
                            {showFullReason ? 'Show less' : 'Show more'}
                        </button>
                    )}
                </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-end gap-3">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onViewDetails(request)}
                    className="flex items-center gap-2"
                >
                    <Eye className="w-4 h-4" />
                    View Details
                </Button>
                <Button
                    variant="gradient"
                    size="sm"
                    onClick={() => onApprove(request.id)}
                    disabled={isApproving}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
                >
                    <CheckCircle className="w-4 h-4" />
                    {isApproving ? 'Approving...' : 'Approve'}
                </Button>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onReject(request.id)}
                    disabled={isRejecting}
                    className="flex items-center gap-2 border-red-300 text-red-700 hover:bg-red-50"
                >
                    <X className="w-4 h-4" />
                    {isRejecting ? 'Rejecting...' : 'Reject'}
                </Button>
            </div>
        </div>
    );
};
