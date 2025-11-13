"use client";

import React, { useState } from 'react';
import { LeaveCards } from '@/components/dashboard/leave-management/Dashboard/LeaveCards';

export default function LeaveBalancePage() {
    const [searchValue, setSearchValue] = useState('');
    const [showBalanceForm, setShowBalanceForm] = useState(false);
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

    const handleAddRequest = () => {
        setShowBalanceForm(true);
    };

    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900">Leave Balances</h1>
                <p className="text-gray-600 mt-2">Manage employee leave balances and allocations</p>
            </div>

            <LeaveCards
                onAddRequest={handleAddRequest}
                searchValue={searchValue}
                onSearchChange={setSearchValue}
            />

            {/* TODO: Add BalanceList component here */}
            <div className="mt-8">
                <p className="text-gray-600">Leave balances list will be displayed here...</p>
            </div>

            {/* TODO: Add BalanceForm modal here */}
            {showBalanceForm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
                        <h2 className="text-xl font-bold mb-4">Add Leave Balance</h2>
                        <p className="text-gray-600 mb-4">Balance form will be implemented here...</p>
                        <button
                            onClick={() => setShowBalanceForm(false)}
                            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}