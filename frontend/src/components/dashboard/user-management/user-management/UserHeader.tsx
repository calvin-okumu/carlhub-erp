import Button from "@/components/ui/Button";
import { User, UserPlus, Users, Shield } from "lucide-react";

interface UserHeaderProps {
    activeTab: 'invites' | 'activeUsers' | 'employees';
    onTabChange: (tab: 'invites' | 'activeUsers' | 'employees') => void;
}

export const UserHeader = ({ activeTab, onTabChange }: UserHeaderProps) => {
    return (
        <div className="flex items-center justify-end gap-2">
            <Button
                onClick={() => onTabChange('invites')}
                className={`flex items-center gap-2 px-4 py-2 ${activeTab === 'invites' ? 'bg-blue-600 text-white hover:bg-blue-700' : 'text-blue-600 hover:bg-blue-50'} border border-blue-600 rounded-md`}
            >
                <UserPlus size={16} />
                Invites
            </Button>
            <Button
                onClick={() => onTabChange('activeUsers')}
                className={`flex items-center gap-2 px-4 py-2 ${activeTab === 'activeUsers' ? 'bg-blue-600 text-white hover:bg-blue-700' : 'text-blue-600 hover:bg-blue-50'} border border-blue-600 rounded-md`}
            >
                <User size={16} />
                Active Users
            </Button>
            <Button
                onClick={() => onTabChange('employees')}
                className={`flex items-center gap-2 px-4 py-2 ${activeTab === 'employees' ? 'bg-blue-600 text-white hover:bg-blue-700' : 'text-blue-600 hover:bg-blue-50'} border border-blue-600 rounded-md`}
            >
                <Users size={16} />
                Employees
            </Button>
            <Button
                onClick={() => onTabChange('employees')}
                className={`flex items-center gap-2 px-4 py-2 ${activeTab === 'employees' ? 'bg-blue-600 text-white hover:bg-blue-700' : 'text-blue-600 hover:bg-blue-50'} border border-blue-600 rounded-md`}
            >
                <Shield size={16} />
                Groups & Permissions
            </Button>

        </div>
    )
}
