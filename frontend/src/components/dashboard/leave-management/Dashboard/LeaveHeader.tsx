import { Calendar, User, Users } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
    { key: "requests", label: "Requests", icon: User },
    { key: "calendar", label: "Calendar", icon: Calendar },
    { key: "policies", label: "Policies", icon: Users },
] as const;

export const LeaveHeader = () => {
    const pathname = usePathname();
    const activeTab = pathname.split('/').pop() as typeof tabs[number]['key'];

    return (
        <div className="flex items-center justify-end gap-2">
            {tabs.map(({ key, label, icon: Icon }) => (
                <Link
                    key={key}
                    href={`/dashboard/leave/${key}`}
                    className={`flex bg-white shadow-md items-center gap-2 px-3 py-2 rounded-md border ${activeTab === key
                        ? 'bg-blue-100 border-blue-600 text-blue-700'
                        : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                >
                    <Icon size={16} />
                    {label}
                </Link>
            ))}
        </div>
    );
};
