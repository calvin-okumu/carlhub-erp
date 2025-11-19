"use client";
import type { LeaveRequest } from '@/api/types';
import { useState } from 'react';
import { ApprovalsHeader } from './ApprovalsHeader';
import { ApprovalTabs } from './ApprovalTabs';

type ApprovalTab = 'all' | 'approved' | 'rejected';

export default function ApprovalsSection() {
    const [searchValue, setSearchValue] = useState('');
    const [activeTab, setActiveTab] = useState<ApprovalTab>('all');
    const [leaveRequests] = useState<LeaveRequest[]>([]);

    const tabCounts = {
        all: leaveRequests.filter(r => r.status === 'pending').length,
        approved: leaveRequests.filter(r => r.status === 'approved').length,
        rejected: leaveRequests.filter(r => r.status === 'rejected').length,
    };



    const handleFiltersClick = () => {
        console.log('Open filters');
    };

    const handleBulkActionsClick = () => {
        console.log('Open bulk actions');
    };

    return (
        <div>
            <ApprovalsHeader
                searchValue={searchValue}
                onSearchChange={setSearchValue}
                onFiltersClick={handleFiltersClick}
                onBulkActionsClick={handleBulkActionsClick}
            />

            <ApprovalTabs
                activeTab={activeTab}
                onTabChange={setActiveTab}
                counts={tabCounts}
            />
        </div>
    );
}
