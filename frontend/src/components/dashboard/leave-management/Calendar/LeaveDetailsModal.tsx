import { format } from 'date-fns';
import { X, Calendar, Clock, User, FileText } from 'lucide-react';
import type { LeaveRequest } from '../../../../api/types';

interface LeaveDetailsModalProps {
  leaveRequest: LeaveRequest | null;
  onClose: () => void;
}

const LeaveDetailsModal = ({ leaveRequest, onClose }: LeaveDetailsModalProps) => {
  if (!leaveRequest) return null;

  const getStatusColor = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800',
      taken: 'bg-blue-100 text-blue-800',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Leave Details</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Date */}
          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-gray-400" />
            <div>
              <div className="font-medium text-gray-900">
                {format(new Date(leaveRequest.start_date), 'dd MMM yyyy')}
              </div>
              <div className="text-sm text-gray-600">
                {leaveRequest.start_date !== leaveRequest.end_date
                  ? `to ${format(new Date(leaveRequest.end_date), 'dd MMM yyyy')}`
                  : 'Single day'
                }
              </div>
            </div>
          </div>

          {/* Leave Type */}
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-gray-400" />
            <div>
              <div className="font-medium text-gray-900">{leaveRequest.leave_type}</div>
              <div className="text-sm text-gray-600">Leave Type</div>
            </div>
          </div>

          {/* Duration */}
          <div className="flex items-center gap-3">
            <Clock className="w-5 h-5 text-gray-400" />
            <div>
              <div className="font-medium text-gray-900">
                {leaveRequest.days_requested} {leaveRequest.days_requested === 1 ? 'day' : 'days'}
              </div>
              <div className="text-sm text-gray-600">Duration</div>
            </div>
          </div>

          {/* Employee */}
          <div className="flex items-center gap-3">
            <User className="w-5 h-5 text-gray-400" />
            <div>
              <div className="font-medium text-gray-900">{leaveRequest.employee_name}</div>
              <div className="text-sm text-gray-600">Employee</div>
            </div>
          </div>

          {/* Status */}
          <div className="flex items-center gap-3">
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(leaveRequest.status)}`}>
              {leaveRequest.status.charAt(0).toUpperCase() + leaveRequest.status.slice(1)}
            </div>
          </div>

          {/* Reason */}
          {leaveRequest.reason && (
            <div className="pt-4 border-t">
              <div className="text-sm font-medium text-gray-900 mb-2">Reason</div>
              <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-md">
                {leaveRequest.reason}
              </div>
            </div>
          )}

          {/* Approval Info */}
          {leaveRequest.approved_by_name && (
            <div className="pt-4 border-t">
              <div className="text-sm text-gray-600">
                Approved by {leaveRequest.approved_by_name} on{' '}
                {format(new Date(leaveRequest.approved_date!), 'dd MMM yyyy')}
              </div>
              {leaveRequest.approval_notes && (
                <div className="text-sm text-gray-600 mt-2 bg-gray-50 p-3 rounded-md">
                  {leaveRequest.approval_notes}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LeaveDetailsModal;