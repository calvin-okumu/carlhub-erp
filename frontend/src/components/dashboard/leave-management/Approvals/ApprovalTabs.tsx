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
}

const TAB_CONFIG: Omit<Tab, 'count'>[] = [
    { key: 'all', label: 'All Pending' },
    { key: 'approved', label: 'Approved' },
    { key: 'rejected', label: 'Rejected' },
] as const;

export const ApprovalTabs = ({ activeTab, onTabChange, counts }: ApprovalTabsProps) => {
    const tabs: Tab[] = TAB_CONFIG.map(tab => ({
        ...tab,
        count: counts[tab.key],
    }));

    return (
        <div className="border-b border-gray-200 mb-6">
            <nav className="flex space-x-8" role="tablist" aria-label="Approval categories">
                {tabs.map((tab) => {
                    const isActive = activeTab === tab.key;
                    const hasCount = tab.count > 0;

                    return (
                        <button
                            key={tab.key}
                            onClick={() => onTabChange(tab.key)}
                            role="tab"
                            aria-selected={isActive}
                            aria-controls={`${tab.key}-panel`}
                            className={`
                relative py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${isActive
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }
              `}
                        >
                            <span>{tab.label}</span>
                            {hasCount && (
                                <span
                                    className={`
                    ml-2 inline-flex items-center justify-center py-0.5 px-2 
                    rounded-full text-xs font-semibold transition-colors
                    ${isActive
                                            ? 'bg-blue-100 text-blue-600'
                                            : 'bg-gray-100 text-gray-600'
                                        }
                  `}
                                    aria-label={`${tab.count} pending`}
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
