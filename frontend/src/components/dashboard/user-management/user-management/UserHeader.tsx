
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
            {tabs.map(({ key, label, icon: Icon }) => {
                const isActive = activeTab === key;
                const base =
                    "flex items-center gap-2 px-4 py-2 border border-blue-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors";
                const state = isActive
                    ? "bg-blue-600 text-white hover:bg-blue-700"
                    : "text-blue-600 hover:bg-blue-50";

                return (
                    <Button
                        key={key}
                        onClick={() => onTabChange(key)}
                        className={`${base} ${state}`}
                    >
                        <Icon size={16} />
                        {label}
                    </Button>
                );
            })}
        </div>
    );
};
