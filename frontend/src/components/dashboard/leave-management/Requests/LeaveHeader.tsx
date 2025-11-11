"use client";

import { getLeaveRequests } from '@/api/leave';
import type { LeaveRequest } from '@/api/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import StatCard from '@/components/ui/StatCard';
import { Calendar, Clock, CheckCircle } from 'lucide-react';
import { useEffect, useState } from 'react';

interface LeaveHeaderProps {
    onAddRequest: () => void;
    searchValue: string;
    onSearchChange: (value: string) => void;
}

export default function LeaveHeader({ onAddRequest, searchValue, onSearchChange }: LeaveHeaderProps) {
    const [allRequests, setAllRequests] = useState<LeaveRequest[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAllRequests = async () => {
            try {
                const data = await getLeaveRequests({ limit: 1000 });
                if (data && typeof data === 'object' && 'results' in data) {
                    setAllRequests(data.results);
                } else {
                    setAllRequests(data as LeaveRequest[]);
                }
            } catch (error) {
                console.error('Failed to fetch leave requests for metrics:', error);
            } finally {
                setLoading(false);
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
        onAddRequest();
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
            <div className="flex justify-between items-center">
                <Input
                    type="text"
                    placeholder="Search leave requests..."
                    value={searchValue}
                    onChange={(e) => onSearchChange(e.target.value)}
                    className="max-w-xs"
                />
                <Button onClick={handleAddRequest}>
                    + New Leave Request
                </Button>
            </div>
        </div>
    );
};