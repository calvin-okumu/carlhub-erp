
import CalendarSection from '../../../../components/dashboard/leave-management/Calendar/CalendarSection';

export default function LeaveCalendarPage() {
    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div className="mb-8">
                <h1 className="h1-title">Leave Calendar</h1>
                <p className="mt-2 text-gray-600">View your leave schedule and track approved leave days</p>
            </div>

            <CalendarSection />
        </div>
    );
}
