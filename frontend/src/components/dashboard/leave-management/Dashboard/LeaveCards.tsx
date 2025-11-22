"use client";

import { getLeaveRequests } from '@/api/leave';
import type { LeaveRequest } from '@/api/types';
import StatCard from '@/components/ui/StatCard';
import { STORAGE_KEYS } from '@/constants/storage';
import { Calendar, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';

interface LeaveCardsProps {
    onAddRequest?: () => void;
}

export const LeaveCards = ({
    onAddRequest
}: LeaveCardsProps) => {
    const [allRequests, setAllRequests] = useState<LeaveRequest[]>([]);

    useEffect(() => {
        const fetchAllRequests = async () => {
            try {
                // Get current user ID from localStorage
                const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
                let employeeId: number | undefined;

                if (userData) {
                    const user = JSON.parse(userData);
                    employeeId = user.id;
                }

                const data = await getLeaveRequests({
                    page_size: 1000,
                    employee: employeeId
                });

                if (data && typeof data === 'object' && 'results' in data) {
                    setAllRequests(data.results);
                } else {
                    setAllRequests(data as LeaveRequest[]);
                }
            } catch (error) {
                console.error('Failed to fetch leave requests for metrics:', error);
            }
        };

        fetchAllRequests();
    }, []);

    const requests = allRequests;

    const totalRequests = requests.length;
    const pendingRequests = requests.filter(r => r.status === 'pending').length;
    const approvedRequests = requests.filter(r => r.status === 'approved').length;
    const thisMonthRequests = requests.filter(r => {
        const created = new Date(r.applied_date);
        const now = new Date();
        return created.getMonth() === now.getMonth() && created.getFullYear() === now.getFullYear();
    }).length;

    // Calculate trends (comparing with previous month)
    const lastMonthRequests = requests.filter(r => {
        const created = new Date(r.applied_date);
        const now = new Date();
        const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        return created.getMonth() === lastMonth.getMonth() && created.getFullYear() === lastMonth.getFullYear();
    }).length;

    const getTrend = (current: number, previous: number) => {
        if (previous === 0) return current > 0 ? 100 : 0;
        return Math.round(((current - previous) / previous) * 100);
    };

    const handleAddRequest = () => {
        onAddRequest?.();
    };

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Requests"
                    value={totalRequests}
                    icon={Calendar}
                    color="blue"
                    subtitle="All time requests"
                    trend={{
                        value: getTrend(thisMonthRequests, lastMonthRequests),
                        period: "last month"
                    }}
                />
                <StatCard
                    title="Pending Approval"
                    value={pendingRequests}
                    icon={Clock}
                    color="yellow"
                    subtitle="Awaiting decision"
                    trend={{
                        value: pendingRequests > 0 ? 10 : -5,
                        period: "last week"
                    }}
                />
                <StatCard
                    title="Approved"
                    value={approvedRequests}
                    icon={CheckCircle}
                    color="green"
                    subtitle="Successfully approved"
                    trend={{
                        value: approvedRequests > 0 ? 15 : 0,
                        period: "last month"
                    }}
                />
                <StatCard
                    title="This Month"
                    value={thisMonthRequests}
                    icon={TrendingUp}
                    color="purple"
                    subtitle="Current month"
                    trend={{
                        value: getTrend(thisMonthRequests, lastMonthRequests),
                        period: "last month"
                    }}
                />
            </div>
        </div>
    );
};
