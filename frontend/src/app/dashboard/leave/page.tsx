import { LeaveOverview } from "@/components/dashboard/leave-management/LeaveOverview";
export default function LeaveManagementPage() {

    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div className="mb-8">
                <h1 className="h1-title">Leave Management</h1>
                <p className="mt-2 text-gray-600">Manage your leave requests and view your balances</p>
            </div>
            <LeaveOverview />
        </div>
    );
}
