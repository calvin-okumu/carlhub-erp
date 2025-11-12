import { LeaveLayout } from "@/components/dashboard/leave-management/LeaveLayout";
import { RequestSection } from "@/components/dashboard/leave-management/Requests/RequestSection";

export default function LeaveRequestsPage() {
    return (
        <LeaveLayout>
            <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
                <h1 className="h1-title">Leave Management</h1>
                <p className="mt-2 text-gray-600">Manage your leave requests and view remaining leave days</p>
            </div>
            <RequestSection />

        </LeaveLayout>
    );
}
