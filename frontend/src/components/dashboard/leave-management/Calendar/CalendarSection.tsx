"use client";

import type { LeaveRequest } from "@/api/types";
import {
    endOfMonth,
    isSameMonth,
    isValid,
    startOfMonth,
    startOfWeek,
    endOfWeek,
    eachDayOfInterval as eachDayOfIntervalFn,
    format,
} from "date-fns";
import { useMemo, useState } from "react";
import CalendarHeader from "./CalendarHeader";
import LeaveDay from "./LeaveDay";
import LeaveDetailsModal from "./LeaveDetailsModal";
import { CalendarLegend } from "./CalendarLegend";
import { useLeaveRequests } from "./hooks/useLeaveRequests";
import { Calendar, Download } from "lucide-react";
import type { CalendarFilters } from "./CalendarLegend";

const CalendarSection = () => {
    const [currentDate, setCurrentDate] = useState(new Date());
    const [selectedLeaves, setSelectedLeaves] = useState<LeaveRequest[]>([]);
    const [showDetails, setShowDetails] = useState(false);
    const [calendarFilters, setCalendarFilters] = useState<CalendarFilters>({
        leaveTypes: [],
        statuses: [],
        dateRange: { start: '', end: '' }
    });

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
     * Include days from previous/next month to fill the grid properly.
     */
    const calendarDays = useMemo(() => {
        const monthStart = startOfMonth(currentDate);
        const monthEnd = endOfMonth(currentDate);
        const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 }); // Monday
        const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 }); // Monday
        
        return eachDayOfIntervalFn({ start: calendarStart, end: calendarEnd });
    }, [currentDate]);

    /**
     * Helper: find leaves matching a given day.
     */
    const getLeavesForDay = (day: Date): LeaveRequest[] => {
        return leaveRequests.filter((req) => {
            const start = parseDate(req.start_date);
            const end = parseDate(req.end_date);

            if (!start || !end) return false;
            
            // Apply filters
            if (calendarFilters.leaveTypes.length > 0 && !calendarFilters.leaveTypes.includes(req.leave_type)) {
                return false;
            }
            if (calendarFilters.statuses.length > 0 && !calendarFilters.statuses.includes(req.status)) {
                return false;
            }
            
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
            <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Calendar className="w-6 h-6 text-red-600" />
                </div>
                <h3 className="text-red-800 font-semibold mb-2">Failed to load leave calendar</h3>
                <p className="text-red-700 text-sm">{String(error)}</p>
            </div>
        );
    }

    return (
        <div className="calendar-section space-y-6">
            <CalendarHeader
                currentDate={currentDate}
                onDateChange={setCurrentDate}
                leaveRequests={leaveRequests}
            />

            {isLoading ? (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-12">
                    <div className="flex flex-col items-center justify-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
                        <p className="mt-4 text-gray-600 font-medium">Loading calendar...</p>
                    </div>
                </div>
            ) : (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                    {/* Calendar Controls */}
                    <div className="flex items-center justify-between p-4 border-b border-gray-100 bg-gray-50/50">
                        <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4 text-gray-600" />
                            <span className="text-sm font-medium text-gray-900">
                                {format(currentDate, "MMMM yyyy")}
                            </span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CalendarLegend onFilterChange={setCalendarFilters} />
                            <button className="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                                <Download className="w-3 h-3" />
                                Export
                            </button>
                        </div>
                    </div>

                    {/* Day headers */}
                    <div className="grid grid-cols-7 bg-gradient-to-b from-gray-50 to-white border-b border-gray-100 select-none">
                        {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d, index) => (
                            <div
                                key={d}
                                className={`
                                    p-3 text-center text-xs font-bold uppercase tracking-wide
                                    ${index >= 5 ? 'text-blue-600 bg-blue-50/50' : 'text-gray-700'}
                                `}
                            >
                                {d}
                            </div>
                        ))}
                    </div>

                    {/* Calendar days */}
                    <div className="grid grid-cols-7 divide-x divide-gray-100">
                        {calendarDays.map((day, index) => {
                            const dayLeaves = getLeavesForDay(day);
                            const dayIndex = index % 7;

                            return (
                                <div
                                    key={day.toISOString()}
                                    className={`
                                        ${dayIndex >= 5 ? 'bg-blue-50/20' : ''}
                                    `}
                                >
                                    <LeaveDay
                                        day={day}
                                        leaveRequests={dayLeaves}
                                        isCurrentMonth={isSameMonth(day, currentDate)}
                                        onClick={handleDayClick}
                                    />
                                </div>
                            );
                        })}
                    </div>

                    {/* Calendar Footer */}
                    <div className="p-4 border-t border-gray-100 bg-gray-50/30">
                        <div className="flex items-center justify-between text-xs text-gray-600">
                            <div className="flex items-center gap-4">
                                <div className="flex items-center gap-1">
                                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                                    <span>Today</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                                    <span>Leave</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <div className="w-3 h-3 rounded-full bg-blue-400 opacity-50"></div>
                                    <span>Weekend</span>
                                </div>
                            </div>
                            <div className="text-gray-500">
                                {leaveRequests.length} requests this month
                            </div>
                        </div>
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
