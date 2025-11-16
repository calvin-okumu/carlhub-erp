"use client";

import { useState } from 'react';
import { startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth } from 'date-fns';
import CalendarHeader from './CalendarHeader';
import LeaveDay from './LeaveDay';
import LeaveDetailsModal from './LeaveDetailsModal';
import { useLeaveRequests } from './hooks/useLeaveRequests';
import type { LeaveRequest } from '../../../../api/types';

const CalendarSection = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedLeave, setSelectedLeave] = useState<LeaveRequest | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const { leaveRequests, isLoading, error } = useLeaveRequests({
    month: currentDate.getMonth() + 1,
    year: currentDate.getFullYear()
  });

  // Generate calendar days
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarDays = eachDayOfInterval({ start: monthStart, end: monthEnd });

  // Helper: get leave requests for a specific day
  const getLeaveForDay = (day: Date): LeaveRequest[] => {
    return leaveRequests.filter(request => {
      const start = new Date(request.start_date);
      const end = new Date(request.end_date);
      return day >= start && day <= end;
    });
  };

  // Handle day click
  const handleDayClick = (day: Date, dayLeaveRequests: LeaveRequest[]) => {
    if (dayLeaveRequests.length > 0) {
      setSelectedLeave(dayLeaveRequests[0]); // Show first leave, or handle multiple
      setShowDetails(true);
    }
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="text-red-800">
          Error loading calendar: {error}
        </div>
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
          <div className="grid grid-cols-7 bg-gray-50 border-b">
            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => (
              <div key={day} className="p-4 text-center text-sm font-medium text-gray-700">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-7">
            {calendarDays.map(day => {
              const dayLeave = getLeaveForDay(day);
              const isCurrentMonth = isSameMonth(day, currentDate);

              return (
                <LeaveDay
                  key={day.toISOString()}
                  day={day}
                  leaveRequests={dayLeave}
                  isCurrentMonth={isCurrentMonth}
                  onClick={handleDayClick}
                />
              );
            })}
          </div>
        </div>
      )}

      {showDetails && (
        <LeaveDetailsModal
          leaveRequest={selectedLeave}
          onClose={() => setShowDetails(false)}
        />
      )}
    </div>
  );
};

export default CalendarSection;