"use client";

import StatCard from "@/components/ui/StatCard";
import { Calendar, DollarSign, Heart, AlertCircle } from "lucide-react";
import { useLeaveBalances } from "@/hooks/useLeaveBalances";

export const PolicyHeader = () => {
    const { balances, isLoading, error } = useLeaveBalances();

    if (isLoading) {
        return (
            <div className="space-y-2">
                <h2 className="text-xl font-bold text-gray-900 mt-6 mb-4">Leave Balances</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="animate-pulse">
                            <div className="bg-gray-200 h-24 rounded-lg"></div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="space-y-2">
                <h2 className="text-xl font-bold text-gray-900 mt-6 mb-4">Leave Balances</h2>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-red-600">
                        <AlertCircle size={16} />
                        <span className="text-sm">Failed to load leave balances</span>
                    </div>
                </div>
            </div>
        );
    }

    // Group balances by leave type
    const balanceMap = balances.reduce((acc, balance) => {
        acc[balance.leave_type] = balance;
        return acc;
    }, {} as Record<string, LeaveBalance>);

    const displayBalances = [
        {
            type: 'annual',
            title: 'Annual Leave',
            icon: Calendar,
            balance: balanceMap.annual
        },
        {
            type: 'sick',
            title: 'Sick Leave',
            icon: Heart,
            balance: balanceMap.sick
        },
        {
            type: 'unpaid',
            title: 'Unpaid Leave',
            icon: DollarSign,
            balance: balanceMap.unpaid
        }
    ];

    return (
        <div className="space-y-2">
            <div>
                <h2 className="text-xl font-bold text-gray-900 mt-6 mb-4">Your Leave Balances</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {displayBalances.map(({ type, title, icon, balance }) => (
                    <StatCard
                        key={type}
                        title={title}
                        value={
                            balance
                                ? `${balance.remaining_days}/${balance.total_days} days`
                                : "0/0 days"
                        }
                        icon={icon}
                        className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                    />
                ))}
            </div>

            {balances.length === 0 && (
                <p className="text-sm text-gray-500 text-center mt-4">
                    No leave balances available. Contact HR for assistance.
                </p>
            )}
        </div>
    );
};

