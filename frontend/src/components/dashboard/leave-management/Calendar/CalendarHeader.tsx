import { useMemo } from 'react';
import { format, subMonths, addMonths } from 'date-fns';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import type { LeaveRequest } from '../../../../api/types';

interface CalendarHeaderProps {
  currentDate: Date;
  onDateChange: (date: Date) => void;
  leaveRequests: LeaveRequest[];
}

const CalendarHeader = ({ currentDate, onDateChange, leaveRequests }: CalendarHeaderProps) => {
  const goToPreviousMonth = () => {
    onDateChange(subMonths(currentDate, 1));
  };

  const goToNextMonth = () => {
    onDateChange(addMonths(currentDate, 1));
  };

  const goToToday = () => {
    onDateChange(new Date());
  };

  const monthSummary = useMemo(() => {
    const currentMonth = currentDate.getMonth();
    const currentYear = currentDate.getFullYear();

    const monthLeave = leaveRequests.filter(request => {
      const startDate = new Date(request.start_date);
      const endDate = new Date(request.end_date);
      return (startDate.getMonth() === currentMonth && startDate.getFullYear() === currentYear) ||
             (endDate.getMonth() === currentMonth && endDate.getFullYear() === currentYear);
    });

    const totalDays = monthLeave.reduce((sum, request) => sum + request.days_requested, 0);

    const byType = monthLeave.reduce((acc, request) => {
      acc[request.leave_type] = (acc[request.leave_type] || 0) + request.days_requested;
      return acc;
    }, {} as Record<string, number>);

    return { totalDays, byType };
  }, [leaveRequests, currentDate]);

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
      {/* Month Navigation */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <button
            onClick={goToPreviousMonth}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
            aria-label="Previous month"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

          <h2 className="text-2xl font-semibold text-gray-900">
            {format(currentDate, 'MMMM yyyy')}
          </h2>

          <button
            onClick={goToNextMonth}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
            aria-label="Next month"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        <button
          onClick={goToToday}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <Calendar className="w-4 h-4" />
          Today
        </button>
      </div>

      {/* Month Summary */}
      <div className="flex flex-wrap gap-6">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-600">Total Leave Days:</span>
          <span className="text-lg font-semibold text-gray-900">{monthSummary.totalDays}</span>
        </div>

        {(Object.entries(monthSummary.byType) as [string, number][]).map(([type, days]) => (
          <div key={type} className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-600">{type}:</span>
            <span className="text-lg font-semibold text-gray-900">{days} days</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CalendarHeader;