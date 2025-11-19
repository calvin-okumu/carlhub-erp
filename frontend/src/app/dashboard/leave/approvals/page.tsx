import ApprovalsSection from "@/components/dashboard/leave-management/Approvals/ApprovalsSection";
import { LeaveLayout } from "@/components/dashboard/leave-management/LeaveLayout";

export default function LeaveApprovalsPage() {
    return (
        <LeaveLayout>
            <div className="mb-8">
                <div className="mb-4">
                    <h1 className="h1-title">Leave Approvals</h1>
                    <p className="mt-2 text-gray-600">Approve or reject leave requests</p>
                </div>
                <ApprovalsSection />

            </div>
        </LeaveLayout>
    );
}
