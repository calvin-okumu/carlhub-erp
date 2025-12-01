"use client";

import { useState } from 'react';
import { CheckCircle, XCircle, MessageSquare } from 'lucide-react';
import Button from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import Modal from '@/components/ui/Modal';
import type { LeaveRequest } from '@/api/types';
import { approveLeaveRequestLevel, rejectLeaveRequestLevel } from '@/api/leave';

interface ApprovalActionsProps {
    leaveRequest: LeaveRequest;
    onActionComplete?: () => void;
    disabled?: boolean;
}

export default function ApprovalActions({ 
    leaveRequest, 
    onActionComplete, 
    disabled = false 
}: ApprovalActionsProps) {
    const [showApproveModal, setShowApproveModal] = useState(false);
    const [showRejectModal, setShowRejectModal] = useState(false);
    const [notes, setNotes] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleApprove = async () => {
        if (!leaveRequest.can_approve) return;
        
        setIsSubmitting(true);
        try {
            await approveLeaveRequestLevel(leaveRequest.slug, { notes: notes.trim() || undefined });
            setShowApproveModal(false);
            setNotes('');
            onActionComplete?.();
        } catch (error) {
            console.error('Failed to approve leave request:', error);
            // Show user-friendly error message
            const errorMessage = error instanceof Error ? error.message : 'Failed to approve leave request. Please try again.';
            alert(errorMessage);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleReject = async () => {
        if (!leaveRequest.can_approve) return;
        
        // Validate rejection notes
        if (!notes.trim()) {
            alert('Rejection reason is required.');
            return;
        }
        
        setIsSubmitting(true);
        try {
            await rejectLeaveRequestLevel(leaveRequest.slug, { notes: notes.trim() });
            setShowRejectModal(false);
            setNotes('');
            onActionComplete?.();
        } catch (error) {
            console.error('Failed to reject leave request:', error);
            // Show user-friendly error message
            const errorMessage = error instanceof Error ? error.message : 'Failed to reject leave request. Please try again.';
            alert(errorMessage);
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!leaveRequest.can_approve || !leaveRequest.workflow_status.is_pending) {
        return null;
    }

    return (
        <>
            <div className="flex items-center space-x-3">
                <Button
                    onClick={() => setShowApproveModal(true)}
                    disabled={disabled || isSubmitting}
                    variant="primary"
                    size="sm"
                    className="flex items-center"
                >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Approve
                </Button>
                
                <Button
                    onClick={() => setShowRejectModal(true)}
                    disabled={disabled || isSubmitting}
                    variant="danger"
                    size="sm"
                    className="flex items-center"
                >
                    <XCircle className="w-4 h-4 mr-2" />
                    Reject
                </Button>
            </div>

            {/* Approve Modal */}
            <Modal
                isOpen={showApproveModal}
                onClose={() => {
                    setShowApproveModal(false);
                    setNotes('');
                }}
                title="Approve Leave Request"
            >
                <div className="space-y-4">
                    <div className="bg-green-50 p-4 rounded-lg">
                        <h4 className="font-medium text-green-900">Leave Request Details</h4>
                        <div className="mt-2 text-sm text-green-800">
                            <p><strong>Employee:</strong> {leaveRequest.employee_name}</p>
                            <p><strong>Type:</strong> {leaveRequest.leave_type}</p>
                            <p><strong>Duration:</strong> {leaveRequest.duration_display}</p>
                            <p><strong>Dates:</strong> {leaveRequest.start_date} to {leaveRequest.end_date}</p>
                            {leaveRequest.reason && <p><strong>Reason:</strong> {leaveRequest.reason}</p>}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Approval Notes (Optional)
                        </label>
                        <Textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            placeholder="Add any notes for this approval..."
                            rows={3}
                        />
                    </div>

                    <div className="flex justify-end space-x-3">
                        <Button
                            onClick={() => {
                                setShowApproveModal(false);
                                setNotes('');
                            }}
                            variant="secondary"
                            disabled={isSubmitting}
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={handleApprove}
                            variant="primary"
                            disabled={isSubmitting}
                            loading={isSubmitting}
                        >
                            Approve Request
                        </Button>
                    </div>
                </div>
            </Modal>

            {/* Reject Modal */}
            <Modal
                isOpen={showRejectModal}
                onClose={() => {
                    setShowRejectModal(false);
                    setNotes('');
                }}
                title="Reject Leave Request"
            >
                <div className="space-y-4">
                    <div className="bg-red-50 p-4 rounded-lg">
                        <h4 className="font-medium text-red-900">Leave Request Details</h4>
                        <div className="mt-2 text-sm text-red-800">
                            <p><strong>Employee:</strong> {leaveRequest.employee_name}</p>
                            <p><strong>Type:</strong> {leaveRequest.leave_type}</p>
                            <p><strong>Duration:</strong> {leaveRequest.duration_display}</p>
                            <p><strong>Dates:</strong> {leaveRequest.start_date} to {leaveRequest.end_date}</p>
                            {leaveRequest.reason && <p><strong>Reason:</strong> {leaveRequest.reason}</p>}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Rejection Reason <span className="text-red-500">*</span>
                        </label>
                        <Textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            placeholder="Please provide a reason for rejecting this leave request..."
                            rows={4}
                            required
                        />
                        {notes.trim().length === 0 && (
                            <p className="mt-1 text-sm text-red-600">Rejection reason is required.</p>
                        )}
                    </div>

                    <div className="flex justify-end space-x-3">
                        <Button
                            onClick={() => {
                                setShowRejectModal(false);
                                setNotes('');
                            }}
                            variant="secondary"
                            disabled={isSubmitting}
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={handleReject}
                            variant="danger"
                            disabled={isSubmitting || notes.trim().length === 0}
                            loading={isSubmitting}
                        >
                            Reject Request
                        </Button>
                    </div>
                </div>
            </Modal>
        </>
    );
}