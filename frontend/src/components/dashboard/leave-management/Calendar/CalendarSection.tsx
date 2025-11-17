"use client";

import type { LeaveRequest } from "@/api/types";
import {
    eachDayOfInterval,
    endOfMonth,
    isSameMonth,
    isValid,
    startOfMonth,
} from "date-fns";
import { useMemo, useState } from "react";
import CalendarHeader from "./CalendarHeader";
import LeaveDay from "./LeaveDay";
import LeaveDetailsModal from "./LeaveDetailsModal";
import { useLeaveRequests } from "./hooks/useLeaveRequests";

const CalendarSection = () => {
    const [currentDate, setCurrentDate] = useState(new Date());
    const [selectedLeaves, setSelectedLeaves] = useState<LeaveRequest[]>([]);
    const [showDetails, setShowDetails] = useState(false);

    const { leaveRequests, isLoading, error } = useLeaveRequests({
        month: currentDate.getMonth() + 1,
        year: currentDate.getFullYear(),
    });

    /** 
     * Helper: safely convert API dates.
     */
    const parseDate = (value: string): Date | null => {
        const d = new Date(value);
        return isValid(d) ? d : null;
    };

    /**
     * Memoize calendar days so we don't regenerate unnecessarily.
     */
    const calendarDays = useMemo(() => {
        const start = startOfMonth(currentDate);
        const end = endOfMonth(currentDate);
        return eachDayOfInterval({ start, end });
    }, [currentDate]);

    /**
     * Helper: find leaves matching a given day.
     */
    const getLeavesForDay = (day: Date): LeaveRequest[] => {
        return leaveRequests.filter((req) => {
            const start = parseDate(req.start_date);
            const end = parseDate(req.end_date);

            if (!start || !end) return false;
            return day >= start && day <= end;
        });
    };

    /**
     * Handle clicking on a day.
     * Show all leaves for that day (better UX than forcing index 0 only).
     */
    const handleDayClick = (day: Date, leavesForDay: LeaveRequest[]) => {
        if (leavesForDay.length === 0) return;

        setSelectedLeaves(leavesForDay);
        setShowDetails(true);
    };

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 text-sm font-medium">
                    Failed to load leave calendar.
                </p>
                <p className="text-red-700 text-xs">{String(error)}</p>
            </div>
        );
    }

    return (
        <div className="calendar-section">
            <CalendarHeader
                currentDate={currentDate}
                onDateChange={setCurrentDate}
                leaveRequests={leaveRequests}
            />

            {isLoading ? (
                <div className="flex items-center justify-center h-96">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
            ) : (
                <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
                    {/* Day headers */}
                    <div className="grid grid-cols-7 bg-gray-50 border-b select-none">
                        {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d) => (
                            <div
                                key={d}
                                className="p-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wide"
                            >
                                {d}
                            </div>
                        ))}
                    </div>

                    {/* Calendar days */}
                    <div className="grid grid-cols-7">
                        {calendarDays.map((day) => {
                            const dayLeaves = getLeavesForDay(day);

                            return (
                                <LeaveDay
                                    key={day.toISOString()}
                                    day={day}
                                    leaveRequests={dayLeaves}
                                    isCurrentMonth={isSameMonth(day, currentDate)}
                                    onClick={handleDayClick}
                                />
                            );
                        })}
                    </div>
                </div>
            )}

            {showDetails && (
                <LeaveDetailsModal
                    leaveRequests={selectedLeaves}
                    onClose={() => setShowDetails(false)}
                />
            )}
        </div>
    );
};

export default CalendarSection;
