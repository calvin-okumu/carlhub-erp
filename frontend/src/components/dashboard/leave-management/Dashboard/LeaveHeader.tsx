import Button from "@/components/ui/Button";
import { Calendar, Clock, User, Users } from "lucide-react";

interface LeaveHeaderProps {
    activeTab: "requests" | "calendar" | "approvals" | "policies";
    onTabChange: (
        tab: "requests" | "calendar" | "approvals" | "policies"
    ) => void;
}

const tabs = [
    { key: "requests", label: "Requests", icon: User },
    { key: "calendar", label: "Calendar", icon: Calendar },
    { key: "approvals", label: "Approvals", icon: Clock },
    { key: "policies", label: "Policies", icon: Users },
] as const;

export const LeaveHeader = ({ activeTab, onTabChange }: LeaveHeaderProps) => {
    return (
        <div className="flex items-center justify-end gap-2">
            {tabs.map(({ key, label, icon: Icon }) => (
                <Button
                    key={key}
                    variant="outline"
                    onClick={() => onTabChange(key)}
                    className={`flex items-center gap-2 ${activeTab === key
                        ? 'bg-blue-100 border-blue-600 text-blue-700'
                        : ''
                        }`}
                >
                    <Icon size={16} />
                    {label}
                </Button>
            ))}
        </div>
    );
};
