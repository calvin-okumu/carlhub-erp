import type { LeaveRequest } from "@/api/types";
import { addMonths, format, isValid, subMonths } from "date-fns";
import { Calendar, ChevronLeft, ChevronRight } from "lucide-react";
import { useCallback, useMemo } from "react";

interface CalendarHeaderProps {
    currentDate: Date;
    onDateChange: (date: Date) => void;
    leaveRequests: LeaveRequest[];
}

const getMonthSummary = (requests: LeaveRequest[], date: Date) => {
    if (!isValid(date)) return { totalDays: 0, byType: {} };

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

    const byType = relevant.reduce((acc, r) => {
        acc[r.leave_type] = (acc[r.leave_type] || 0) + r.days_requested;
        return acc;
    }, {} as Record<string, number>);

    return { totalDays, byType };
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
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
            {/* Header Controls */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => changeMonth("prev")}
                        className="p-2 hover:bg-gray-100 active:bg-gray-200 rounded-md transition"
                        aria-label="Previous month"
                    >
                        <ChevronLeft className="w-5 h-5" />
                    </button>

                    <h2 className="text-2xl font-semibold text-gray-900 select-none">
                        {format(currentDate, "MMMM yyyy")}
                    </h2>

                    <button
                        onClick={() => changeMonth("next")}
                        className="p-2 hover:bg-gray-100 active:bg-gray-200 rounded-md transition"
                        aria-label="Next month"
                    >
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>

                <button
                    onClick={goToToday}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 active:bg-blue-800 transition"
                >
                    <Calendar className="w-4 h-4" />
                    Today
                </button>
            </div>

            {/* Summary */}
            <div className="border-t pt-4">
                {!hasSummary ? (
                    <p className="text-gray-500 text-sm italic">
                        No leave records for this month.
                    </p>
                ) : (
                    <div className="flex flex-wrap gap-6">
                        <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-600">Total Leave Days:</span>
                            <span className="text-lg font-semibold">{monthSummary.totalDays}</span>
                        </div>

                        {Object.entries(monthSummary.byType).map(([type, days]) => (
                            <div key={type} className="flex items-center gap-2">
                                <span className="text-sm text-gray-600">{type}:</span>
                                <span className="text-lg font-semibold">{days} days</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default CalendarHeader;
