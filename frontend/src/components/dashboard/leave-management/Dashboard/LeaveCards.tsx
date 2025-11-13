"use client";

import { getLeaveRequests } from '@/api/leave';
import type { LeaveRequest } from '@/api/types';
import StatCard from '@/components/ui/StatCard';
import { Calendar, CheckCircle, Clock } from 'lucide-react';
import { useEffect, useState } from 'react';

interface LeaveCardsProps {
    onAddRequest?: () => void;
    searchValue: string;
    onSearchChange: (value: string) => void;
}

export const LeaveCards = ({
    onAddRequest,
    searchValue,
    onSearchChange
}: LeaveCardsProps) => {
    const [allRequests, setAllRequests] = useState<LeaveRequest[]>([]);

    useEffect(() => {
        const fetchAllRequests = async () => {
            try {
                // Get current user ID from localStorage
                const userData = localStorage.getItem('user');
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
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <StatCard
                    title="Pending Approval"
                    value={pendingRequests}
                    icon={Clock}
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <StatCard
                    title="Approved"
                    value={approvedRequests}
                    icon={CheckCircle}
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <StatCard
                    title="This Month"
                    value={thisMonthRequests}
                    icon={Calendar}
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
            </div>
        </div>
    );
};
