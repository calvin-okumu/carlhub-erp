import { UserSection } from "@/components/dashboard/user-management/user-management/UserSection";

export default function UserManagementPage() {
    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <h1 className="h1-title">User Management</h1>
            <UserSection />
        </div>
    );
}
