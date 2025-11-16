import { LeaveLayout } from "@/components/dashboard/leave-management/LeaveLayout";
import { PolicySection } from "@/components/dashboard/leave-management/Policies/PolicySection";

export default function LeavePoliciesPage() {
    return (
        <LeaveLayout>
            <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
                <h1 className="h1-title">Leave Policies</h1>
                <p className="mt-2 text-gray-600">
                    View  company leave policies.
                </p>
                <PolicySection />
            </div>
        </LeaveLayout>
    );
}
