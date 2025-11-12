import { LeaveOverview } from "@/components/dashboard/leave-management/LeaveOverview";
import { LeaveLayout } from "@/components/dashboard/leave-management/LeaveLayout";

export default function LeaveManagementPage() {
    return (
        <LeaveLayout>
            <div className="mb-8">
                <h1 className="h1-title">Leave Management</h1>
                <p className="mt-2 text-gray-600">Manage your leave requests and view your balances</p>
            </div>
            <LeaveOverview />
        </LeaveLayout>
    );
}
