import type { LeaveRequest } from '@/api/types';
import { format, isToday } from 'date-fns';

interface LeaveDayProps {
    day: Date;
    leaveRequests: LeaveRequest[];
    isCurrentMonth: boolean;
    onClick: (day: Date, leaveRequests: LeaveRequest[]) => void;
}

const LeaveDay = ({ day, leaveRequests, isCurrentMonth, onClick }: LeaveDayProps) => {
    const hasLeave = leaveRequests.length > 0;
    const isCurrentDay = isToday(day);

    // Get leave type colors
    const getLeaveTypeColor = (leaveType: string) => {
        const colors: Record<string, string> = {
            'Annual Leave': 'bg-green-500',
            'Sick Leave': 'bg-red-500',
            'Maternity Leave': 'bg-purple-500',
            'Paternity Leave': 'bg-blue-500',
            'Personal Leave': 'bg-yellow-500',
            'Study Leave': 'bg-indigo-500',
        };
        return colors[leaveType] || 'bg-gray-500';
    };

    const handleClick = () => {
        if (hasLeave) {
            onClick(day, leaveRequests);
        }
    };

    return (
        <div
            className={`
        relative h-24 p-2 border border-gray-200 cursor-pointer transition-colors
        ${!isCurrentMonth ? 'bg-gray-50 text-gray-400' : 'bg-white hover:bg-gray-50'}
        ${isCurrentDay ? 'ring-2 ring-blue-500' : ''}
      `}
            onClick={handleClick}
        >
            {/* Day number */}
            <div className={`text-sm font-medium mb-1 ${isCurrentDay ? 'text-blue-600' : ''}`}>
                {format(day, 'd')}
            </div>

            {/* Leave indicators */}
            {hasLeave && (
                <div className="space-y-1">
                    {leaveRequests.slice(0, 2).map((request) => (
                        <div
                            key={request.id}
                            className={`
                text-xs px-1 py-0.5 rounded text-white text-center truncate
                ${getLeaveTypeColor(request.leave_type)}
              `}
                            title={`${request.leave_type} - ${request.days_requested} days`}
                        >
                            {request.leave_type.split(' ')[0]}
                        </div>
                    ))}
                    {leaveRequests.length > 2 && (
                        <div className="text-xs text-gray-500 text-center">
                            +{leaveRequests.length - 2} more
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default LeaveDay;
