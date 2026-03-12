"use client";

import React, { useState } from 'react';
import { LeaveHeader } from '@/components/dashboard/leave-management/Dashboard/LeaveHeader';

export default function LeaveApprovalsPage() {
    const [showApprovalModal, setShowApprovalModal] = useState(false);

    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900">Leave Approvals</h1>
                <p className="text-gray-600 mt-2">Review and approve pending leave requests</p>
            </div>

            <LeaveHeader />

            {/* TODO: Add filtered RequestList component for pending requests */}
            <div className="mt-8">
                <p className="text-gray-600">Pending leave requests will be displayed here...</p>
            </div>

            {/* TODO: Add ApprovalModal here */}
            {showApprovalModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
                        <h2 className="text-xl font-bold mb-4">Approve Leave Request</h2>
                        <p className="text-gray-600 mb-4">Approval modal will be implemented here...</p>
                        <button
                            onClick={() => setShowApprovalModal(false)}
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
