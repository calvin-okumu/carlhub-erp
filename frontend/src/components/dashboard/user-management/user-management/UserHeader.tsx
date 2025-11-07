import Button from "@/components/ui/Button";
import { Shield, User, UserPlus, Users } from "lucide-react";

interface UserHeaderProps {
    activeTab: "invites" | "activeUsers" | "employees" | "groups";
    onTabChange: (
        tab: "invites" | "activeUsers" | "employees" | "groups"
    ) => void;
}

const tabs = [
    { key: "invites", label: "Invites", icon: UserPlus },
    { key: "activeUsers", label: "Active Users", icon: User },
    { key: "employees", label: "Employees", icon: Users },
    { key: "groups", label: "Groups & Permissions", icon: Shield },
] as const;

export const UserHeader = ({ activeTab, onTabChange }: UserHeaderProps) => {
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
