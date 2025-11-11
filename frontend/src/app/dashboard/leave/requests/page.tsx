"use client";

import React, { useState } from 'react';
import LeaveHeader from '@/components/dashboard/leave-management/Requests/LeaveHeader';
import RequestList from '@/components/dashboard/leave-management/Requests/RequestList';
import type { LeaveRequest } from '@/api/types';

export default function LeaveRequestsPage() {
    const [searchValue, setSearchValue] = useState('');
    const [showRequestForm, setShowRequestForm] = useState(false);
    const [selectedRequest, setSelectedRequest] = useState<LeaveRequest | null>(null);
    const [showRequestDetail, setShowRequestDetail] = useState(false);

    const handleAddRequest = () => {
        setShowRequestForm(true);
    };

    const handleViewRequest = (request: LeaveRequest) => {
        setSelectedRequest(request);
        setShowRequestDetail(true);
    };

    const handleEditRequest = (request: LeaveRequest) => {
        setSelectedRequest(request);
        setShowRequestForm(true);
    };

    const handleApproveRequest = (request: LeaveRequest) => {
        // TODO: Implement approval logic
        console.log('Approve request:', request.id);
    };

    const handleRejectRequest = (request: LeaveRequest) => {
        // TODO: Implement rejection logic
        console.log('Reject request:', request.id);
    };

    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <LeaveHeader
                onAddRequest={handleAddRequest}
                searchValue={searchValue}
                onSearchChange={setSearchValue}
            />

            <div className="mt-8">
                <RequestList
                    searchValue={searchValue}
                    onViewRequest={handleViewRequest}
                    onEditRequest={handleEditRequest}
                    onApproveRequest={handleApproveRequest}
                    onRejectRequest={handleRejectRequest}
                    canApprove={true} // TODO: Check user permissions
                />
            </div>

            {/* TODO: Add RequestForm modal here */}
            {showRequestForm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
                        <h2 className="text-xl font-bold mb-4">
                            {selectedRequest ? 'Edit Leave Request' : 'New Leave Request'}
                        </h2>
                        <p className="text-gray-600 mb-4">Request form will be implemented here...</p>
                        <button
                            onClick={() => {
                                setShowRequestForm(false);
                                setSelectedRequest(null);
                            }}
                            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}

            {/* TODO: Add RequestDetail modal here */}
            {showRequestDetail && selectedRequest && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-lg max-w-2xl w-full mx-4">
                        <h2 className="text-xl font-bold mb-4">Leave Request Details</h2>
                        <p className="text-gray-600 mb-4">Request detail view will be implemented here...</p>
                        <button
                            onClick={() => {
                                setShowRequestDetail(false);
                                setSelectedRequest(null);
                            }}
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