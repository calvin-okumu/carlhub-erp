import { CheckCircle, Clock, LucideIcon, XCircle } from 'lucide-react';

type TabKey = 'all' | 'approved' | 'rejected';

interface ApprovalTabsProps {
    activeTab: TabKey;
    onTabChange: (tab: TabKey) => void;
    counts: Record<TabKey, number>;
}

interface Tab {
    key: TabKey;
    label: string;
    count: number;
    icon: LucideIcon;
    color: string;
    bgColor: string;
    borderColor: string;
}

const TAB_CONFIG: Omit<Tab, 'count'>[] = [
    {
        key: 'all',
        label: 'Pending',
        icon: Clock,
        color: 'yellow',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200'
    },
    {
        key: 'approved',
        label: 'Approved',
        icon: CheckCircle,
        color: 'green',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200'
    },
    {
        key: 'rejected',
        label: 'Rejected',
        icon: XCircle,
        color: 'red',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200'
    },
] as const;

export const ApprovalTabs = ({ activeTab, onTabChange, counts }: ApprovalTabsProps) => {
    const tabs: Tab[] = TAB_CONFIG.map(tab => ({
        ...tab,
        count: counts[tab.key],
    }));

    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-1 mb-6">
            <nav className="flex space-x-1" role="tablist" aria-label="Approval categories">
                {tabs.map((tab) => {
                    const isActive = activeTab === tab.key;
                    const hasCount = tab.count > 0;
                    const Icon = tab.icon;

                    return (
                        <button
                            key={tab.key}
                            onClick={() => onTabChange(tab.key)}
                            role="tab"
                            aria-selected={isActive}
                            aria-controls={`${tab.key}-panel`}
                            className={`
                                relative flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium text-sm transition-all duration-200
                                ${isActive
                                    ? `${tab.bgColor} ${tab.borderColor} border text-${tab.color}-700 shadow-sm`
                                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                                }
                            `}
                        >
                            <Icon className={`w-4 h-4 ${isActive ? `text-${tab.color}-600` : 'text-gray-400'}`} />
                            <span className="font-medium">{tab.label}</span>
                            {hasCount && (
                                <span
                                    className={`
                                        inline-flex items-center justify-center py-0.5 px-2 
                                        rounded-full text-xs font-semibold transition-colors
                                        ${isActive
                                            ? `bg-${tab.color}-100 text-${tab.color}-700`
                                            : 'bg-gray-100 text-gray-600'
                                        }
                                    `}
                                    aria-label={`${tab.count} requests`}
                                >
                                    {tab.count}
                                </span>
                            )}
                        </button>
                    );
                })}
            </nav>
        </div>
    );
};
