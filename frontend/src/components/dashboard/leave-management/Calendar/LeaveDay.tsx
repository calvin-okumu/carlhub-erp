import type { LeaveRequest } from '@/api/types';
import { format, isToday, isWeekend } from 'date-fns';
import { Users } from 'lucide-react';

interface LeaveDayProps {
    day: Date;
    leaveRequests: LeaveRequest[];
    isCurrentMonth: boolean;
    onClick: (day: Date, leaveRequests: LeaveRequest[]) => void;
}

const LeaveDay = ({ day, leaveRequests, isCurrentMonth, onClick }: LeaveDayProps) => {
    const hasLeave = leaveRequests.length > 0;
    const isCurrentDay = isToday(day);
    const isWeekendDay = isWeekend(day);

    // Get leave type configuration
    const getLeaveTypeConfig = (leaveType: string) => {
        const configs = {
            annual_leave: {
                bg: 'bg-blue-500',
                light: 'bg-blue-100',
                text: 'text-blue-700',
                border: 'border-blue-200',
                icon: '🏖️'
            },
            sick_leave: {
                bg: 'bg-red-500',
                light: 'bg-red-100',
                text: 'text-red-700',
                border: 'border-red-200',
                icon: '🏥'
            },
            personal_leave: {
                bg: 'bg-purple-500',
                light: 'bg-purple-100',
                text: 'text-purple-700',
                border: 'border-purple-200',
                icon: '👤'
            },
            maternity_leave: {
                bg: 'bg-pink-500',
                light: 'bg-pink-100',
                text: 'text-pink-700',
                border: 'border-pink-200',
                icon: '🤰'
            },
            paternity_leave: {
                bg: 'bg-indigo-500',
                light: 'bg-indigo-100',
                text: 'text-indigo-700',
                border: 'border-indigo-200',
                icon: '👨‍👧‍👦'
            },
            emergency_leave: {
                bg: 'bg-orange-500',
                light: 'bg-orange-100',
                text: 'text-orange-700',
                border: 'border-orange-200',
                icon: '🚨'
            },
            unpaid_leave: {
                bg: 'bg-gray-500',
                light: 'bg-gray-100',
                text: 'text-gray-700',
                border: 'border-gray-200',
                icon: '💳'
            },
        };
        return configs[leaveType as keyof typeof configs] || configs.annual_leave;
    };

    const handleClick = () => {
        if (hasLeave) {
            onClick(day, leaveRequests);
        }
    };

    const getUniqueLeaveTypes = () => {
        const types = new Set();
        leaveRequests.forEach(req => types.add(req.leave_type));
        return Array.from(types);
    };

    const uniqueTypes = getUniqueLeaveTypes();

    return (
        <div
            className={`
                relative h-28 p-2 border cursor-pointer transition-all duration-200
                ${!isCurrentMonth 
                    ? 'bg-gray-50 text-gray-400 border-gray-100' 
                    : isWeekendDay
                        ? 'bg-blue-50/30 text-gray-700 border-blue-100 hover:bg-blue-100/50'
                        : 'bg-white text-gray-900 border-gray-200 hover:bg-gray-50 hover:border-gray-300 hover:shadow-sm'
                }
                ${isCurrentDay 
                    ? 'ring-2 ring-blue-400 ring-offset-1 bg-blue-50/50' 
                    : ''
                }
                ${hasLeave ? 'hover:z-10' : ''}
            `}
            onClick={handleClick}
        >
            {/* Day number with indicator */}
            <div className="flex items-start justify-between mb-2">
                <div className={`text-sm font-semibold ${isCurrentDay ? 'text-blue-600' : ''}`}>
                    {format(day, 'd')}
                </div>
                {hasLeave && (
                    <div className="flex items-center gap-1">
                        {uniqueTypes.length > 0 && (
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                        )}
                    </div>
                )}
            </div>

            {/* Leave indicators */}
            {hasLeave && (
                <div className="space-y-1">
                    {leaveRequests.slice(0, 2).map((request) => {
                        const config = getLeaveTypeConfig(request.leave_type);
                        return (
                            <div
                                key={request.id}
                                className={`
                                    text-xs px-1.5 py-0.5 rounded-md text-center truncate font-medium
                                    transition-all duration-200 hover:scale-105
                                    ${config.bg} text-white shadow-sm
                                `}
                                title={`${request.leave_type.replace('_', ' ')} - ${request.days_requested} days`}
                            >
                                <span className="mr-1">{config.icon}</span>
                                {request.leave_type.split('_')[0].charAt(0).toUpperCase() + request.leave_type.split('_')[0].slice(1, 3)}
                            </div>
                        );
                    })}
                    {leaveRequests.length > 2 && (
                        <div className="text-xs text-center">
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full font-medium">
                                <Users className="w-3 h-3" />
                                +{leaveRequests.length - 2}
                            </span>
                        </div>
                    )}
                </div>
            )}

            {/* Weekend indicator */}
            {isWeekendDay && !hasLeave && (
                <div className="absolute bottom-1 right-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-400 opacity-50"></div>
                </div>
            )}

            {/* Current day indicator */}
            {isCurrentDay && (
                <div className="absolute top-1 right-1">
                    <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                </div>
            )}
        </div>
    );
};

export default LeaveDay;
