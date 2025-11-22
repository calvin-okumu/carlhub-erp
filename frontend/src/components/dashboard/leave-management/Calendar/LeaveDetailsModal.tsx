import type { LeaveRequest } from '@/api/types';
import { format, differenceInDays } from 'date-fns';
import { Calendar, Clock, FileText, User, X, CheckCircle, XCircle, Timer, TrendingUp, Mail } from 'lucide-react';

interface LeaveDetailsModalProps {
    leaveRequests: LeaveRequest[];
    onClose: () => void;
}

const LeaveDetailsModal = ({ leaveRequests, onClose }: LeaveDetailsModalProps) => {
    if (!leaveRequests || leaveRequests.length === 0) return null;

    // Get the date from the first request (they should all be for the same day)
    const displayDate = new Date(leaveRequests[0].start_date);
    const formattedDate = format(displayDate, 'EEEE, MMMM d, yyyy');



    const getLeaveTypeColor = (leaveType: string) => {
        const colors = {
            annual_leave: 'bg-blue-100 text-blue-700 border-blue-200',
            sick_leave: 'bg-red-100 text-red-700 border-red-200',
            personal_leave: 'bg-purple-100 text-purple-700 border-purple-200',
            maternity_leave: 'bg-pink-100 text-pink-700 border-pink-200',
            paternity_leave: 'bg-indigo-100 text-indigo-700 border-indigo-200',
            emergency_leave: 'bg-orange-100 text-orange-700 border-orange-200',
            unpaid_leave: 'bg-gray-100 text-gray-700 border-gray-200',
        };
        return colors[leaveType as keyof typeof colors] || 'bg-gray-100 text-gray-700 border-gray-200';
    };

    const getStatusConfig = (status: string) => {
        const configs = {
            pending: {
                bg: 'bg-yellow-50',
                border: 'border-yellow-200',
                text: 'text-yellow-800',
                icon: Timer,
                label: 'Pending Approval'
            },
            approved: {
                bg: 'bg-green-50',
                border: 'border-green-200',
                text: 'text-green-800',
                icon: CheckCircle,
                label: 'Approved'
            },
            rejected: {
                bg: 'bg-red-50',
                border: 'border-red-200',
                text: 'text-red-800',
                icon: XCircle,
                label: 'Rejected'
            },
            cancelled: {
                bg: 'bg-gray-50',
                border: 'border-gray-200',
                text: 'text-gray-800',
                icon: XCircle,
                label: 'Cancelled'
            },
            taken: {
                bg: 'bg-blue-50',
                border: 'border-blue-200',
                text: 'text-blue-800',
                icon: CheckCircle,
                label: 'Leave Taken'
            },
        };
        return configs[status as keyof typeof configs] || configs.pending;
    };

    // Get the first request for header display
    const firstRequest = leaveRequests[0];
    const statusConfig = getStatusConfig(firstRequest.status);



    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-blue-100 rounded-xl">
                            <Calendar className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-gray-900">Leave Details</h3>
                            <p className="text-sm text-gray-600">{formattedDate}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2.5 hover:bg-white/80 rounded-xl transition-colors"
                    >
                        <X className="w-6 h-6 text-gray-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {leaveRequests.map((request, index) => {
                            const StatusIcon = getStatusConfig(request.status).icon;
                            
                            // Define getLeaveTypeIcon inline to avoid conflicts
                            const getLeaveTypeIcon = (leaveType: string) => {
                                const icons = {
                                    annual_leave: '🏖️',
                                    sick_leave: '🏥',
                                    personal_leave: '👤',
                                    maternity_leave: '🤰',
                                    paternity_leave: '👨‍👧‍👦',
                                    emergency_leave: '🚨',
                                    unpaid_leave: '💳',
                                };
                                return icons[leaveType as keyof typeof icons] || '📅';
                            };
                            
                            const leaveTypeIcon = getLeaveTypeIcon(request.leave_type);
                            const leaveTypeColor = getLeaveTypeColor(request.leave_type);
                            const isSingleDay = request.start_date === request.end_date;

                            return (
                                <div key={request.id} className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-all duration-200">
                                    {/* Request Header */}
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="flex items-center gap-3">
                                            <div className={`p-2.5 rounded-lg ${leaveTypeColor}`}>
                                                <span className="text-lg">{leaveTypeIcon}</span>
                                            </div>
                                            <div>
                                                <h4 className="font-semibold text-gray-900 capitalize">
                                                    {request.leave_type.replace('_', ' ')}
                                                </h4>
                                                <p className="text-sm text-gray-600">Request #{index + 1}</p>
                                            </div>
                                        </div>
                                        <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${statusConfig.bg} ${statusConfig.border} ${statusConfig.text}`}>
                                            <StatusIcon className="w-4 h-4" />
                                            <span className="text-xs font-medium">
                                                {statusConfig.label}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Employee Info */}
                                    <div className="flex items-center gap-3 mb-4 p-3 bg-gray-50 rounded-lg">
                                        <User className="w-4 h-4 text-gray-500" />
                                        <div>
                                            <div className="font-medium text-gray-900">
                                                {request.employee_name || 'Unknown Employee'}
                                            </div>
                                            <div className="text-xs text-gray-500">Employee</div>
                                        </div>
                                    </div>

                                    {/* Date Information */}
                                    <div className="space-y-3 mb-4">
                                        <div className="flex items-center gap-3">
                                            <Calendar className="w-4 h-4 text-gray-500" />
                                            <div>
                                                <div className="font-medium text-gray-900">
                                                    {format(new Date(request.start_date), 'MMM d, yyyy')}
                                                    {!isSingleDay && ` - ${format(new Date(request.end_date), 'MMM d, yyyy')}`}
                                                </div>
                                                <div className="text-xs text-gray-500">
                                                    {isSingleDay ? 'Single day' : `${differenceInDays(new Date(request.end_date), new Date(request.start_date)) + 1} days`}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <Clock className="w-4 h-4 text-gray-500" />
                                            <div>
                                                <div className="font-medium text-gray-900">
                                                    {request.days_requested} {request.days_requested === 1 ? 'day' : 'days'}
                                                </div>
                                                <div className="text-xs text-gray-500">Duration</div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Reason */}
                                    {request.reason && (
                                        <div className="mb-4">
                                            <div className="flex items-center gap-2 mb-2">
                                                <FileText className="w-4 h-4 text-gray-500" />
                                                <span className="text-sm font-medium text-gray-700">Reason</span>
                                            </div>
                                            <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                                                <p className="text-sm text-gray-700 leading-relaxed">
                                                    {request.reason}
                                                </p>
                                            </div>
                                        </div>
                                    )}

                                    {/* Approval Info */}
                                    {request.approved_by_name && (
                                        <div className="p-3 bg-green-50 rounded-lg border border-green-100">
                                            <div className="flex items-center gap-2 mb-2">
                                                <CheckCircle className="w-4 h-4 text-green-600" />
                                                <span className="text-sm font-medium text-green-700">Approval Information</span>
                                            </div>
                                            <div className="text-sm text-gray-700">
                                                <div className="mb-1">
                                                    <span className="font-medium">Approved by:</span> {request.approved_by_name}
                                                </div>
                                                <div className="mb-1">
                                                    <span className="font-medium">Date:</span> {format(new Date(request.approved_date!), 'MMM d, yyyy')}
                                                </div>
                                                {request.approval_notes && (
                                                    <div className="mt-2 pt-2 border-t border-green-200">
                                                        <div className="flex items-center gap-2 mb-1">
                                                            <Mail className="w-3 h-3 text-green-600" />
                                                            <span className="text-xs font-medium text-green-700">Notes</span>
                                                        </div>
                                                        <p className="text-xs text-gray-600 bg-white rounded p-2">
                                                            {request.approval_notes}
                                                        </p>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>

                    {/* Summary */}
                    <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
                        <div className="flex items-center gap-3">
                            <TrendingUp className="w-5 h-5 text-blue-600" />
                            <div>
                                <h4 className="font-semibold text-blue-900">Summary</h4>
                                <p className="text-sm text-blue-700">
                                    {leaveRequests.length} leave request{leaveRequests.length === 1 ? '' : 's'} for {formattedDate}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LeaveDetailsModal;
