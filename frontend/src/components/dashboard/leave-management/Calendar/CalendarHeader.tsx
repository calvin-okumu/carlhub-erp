import type { LeaveRequest } from "@/api/types";
import { addMonths, format, isValid, subMonths } from "date-fns";
import { Calendar, ChevronLeft, ChevronRight, Users, TrendingUp, Clock, Filter } from "lucide-react";
import { useCallback, useMemo } from "react";

interface CalendarHeaderProps {
    currentDate: Date;
    onDateChange: (date: Date) => void;
    leaveRequests: LeaveRequest[];
}

const getMonthSummary = (requests: LeaveRequest[], date: Date) => {
    if (!isValid(date)) return { totalDays: 0, byType: {}, totalRequests: 0, byStatus: {} };

    const month = date.getMonth();
    const year = date.getFullYear();

    const relevant = requests.filter((r) => {
        const start = new Date(r.start_date);
        const end = new Date(r.end_date);

        return (
            isValid(start) &&
            isValid(end) &&
            ((start.getMonth() === month && start.getFullYear() === year) ||
                (end.getMonth() === month && end.getFullYear() === year))
        );
    });

    const totalDays = relevant.reduce((sum, r) => sum + r.days_requested, 0);
    const totalRequests = relevant.length;

    const byType = relevant.reduce((acc, r) => {
        acc[r.leave_type] = (acc[r.leave_type] || 0) + r.days_requested;
        return acc;
    }, {} as Record<string, number>);

    const byStatus = relevant.reduce((acc, r) => {
        acc[r.status] = (acc[r.status] || 0) + 1;
        return acc;
    }, {} as Record<string, number>);

    return { totalDays, byType, totalRequests, byStatus };
};

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

const CalendarHeader = ({
    currentDate,
    onDateChange,
    leaveRequests,
}: CalendarHeaderProps) => {
    const changeMonth = useCallback(
        (direction: "prev" | "next") => {
            const fn = direction === "prev" ? subMonths : addMonths;
            onDateChange(fn(currentDate, 1));
        },
        [currentDate, onDateChange]
    );

    const goToToday = () => onDateChange(new Date());

    const monthSummary = useMemo(
        () => getMonthSummary(leaveRequests, currentDate),
        [leaveRequests, currentDate]
    );

    const hasSummary = monthSummary.totalDays > 0;

    return (
        <div className="bg-gradient-to-r from-white to-blue-50/30 rounded-xl border border-blue-100 shadow-sm p-6 mb-6">
            {/* Header Controls */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => changeMonth("prev")}
                        className="p-2.5 hover:bg-white/80 active:bg-white/90 rounded-lg transition-all duration-200 border border-blue-100 hover:border-blue-200"
                        aria-label="Previous month"
                    >
                        <ChevronLeft className="w-5 h-5 text-blue-600" />
                    </button>

                    <div className="text-center">
                        <h2 className="text-2xl font-bold text-gray-900 select-none">
                            {format(currentDate, "MMMM yyyy")}
                        </h2>
                        <p className="text-sm text-gray-500 mt-0.5">Leave Calendar Overview</p>
                    </div>

                    <button
                        onClick={() => changeMonth("next")}
                        className="p-2.5 hover:bg-white/80 active:bg-white/90 rounded-lg transition-all duration-200 border border-blue-100 hover:border-blue-200"
                        aria-label="Next month"
                    >
                        <ChevronRight className="w-5 h-5 text-blue-600" />
                    </button>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={goToToday}
                        className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 active:bg-blue-800 transition-all duration-200 shadow-sm hover:shadow-md"
                    >
                        <Calendar className="w-4 h-4" />
                        Today
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2.5 bg-white border border-blue-200 text-blue-700 rounded-lg hover:bg-blue-50 transition-all duration-200">
                        <Filter className="w-4 h-4" />
                        Filters
                    </button>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Total Summary Card */}
                <div className="bg-white rounded-lg border border-blue-100 p-4 shadow-sm">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-100 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-gray-900">
                                {monthSummary.totalDays}
                            </div>
                            <div className="text-sm text-gray-600">Total Leave Days</div>
                        </div>
                    </div>
                </div>

                {/* Requests Summary Card */}
                <div className="bg-white rounded-lg border border-green-100 p-4 shadow-sm">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-green-100 rounded-lg">
                            <Users className="w-5 h-5 text-green-600" />
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-gray-900">
                                {monthSummary.totalRequests}
                            </div>
                            <div className="text-sm text-gray-600">Leave Requests</div>
                        </div>
                    </div>
                </div>

                {/* Status Summary Card */}
                <div className="bg-white rounded-lg border border-purple-100 p-4 shadow-sm">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-purple-100 rounded-lg">
                            <Clock className="w-5 h-5 text-purple-600" />
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-gray-900">
                                {monthSummary.byStatus.approved || 0}
                            </div>
                            <div className="text-sm text-gray-600">Approved Requests</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Leave Type Breakdown */}
            {hasSummary && (
                <div className="mt-6 p-4 bg-white/50 rounded-lg border border-blue-50">
                    <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-blue-600" />
                        Leave Type Breakdown
                    </h3>
                    <div className="flex flex-wrap gap-3">
                        {Object.entries(monthSummary.byType).map(([type, days]) => (
                            <div
                                key={type}
                                className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${getLeaveTypeColor(type)}`}
                            >
                                <span className="text-lg">{getLeaveTypeIcon(type)}</span>
                                <div>
                                    <div className="text-sm font-medium capitalize">
                                        {type.replace('_', ' ')}
                                    </div>
                                    <div className="text-xs opacity-75">
                                        {days} {days === 1 ? 'day' : 'days'}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Empty State */}
            {!hasSummary && (
                <div className="mt-6 p-6 bg-gray-50 rounded-lg border border-gray-200 text-center">
                    <Calendar className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-600 font-medium">No leave records for this month</p>
                    <p className="text-sm text-gray-500 mt-1">
                        Leave requests will appear here once they&apos;re approved
                    </p>
                </div>
            )}
        </div>
    );
};

export default CalendarHeader;
