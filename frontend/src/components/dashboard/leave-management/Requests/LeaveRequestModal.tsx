"use client";

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import { createLeaveRequest } from '@/api/leave';
import type { CreateLeaveRequestData } from '@/api/types';

interface LeaveRequestModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}

const LEAVE_TYPE_CHOICES = [
    { value: 'annual_leave', label: 'Annual Leave' },
    { value: 'sick_leave', label: 'Sick Leave' },
    { value: 'personal_leave', label: 'Personal Leave' },
    { value: 'maternity_leave', label: 'Maternity/Paternity Leave' },
    { value: 'emergency_leave', label: 'Emergency Leave' },
    { value: 'unpaid_leave', label: 'Unpaid Leave' },
];

export default function LeaveRequestModal({ isOpen, onClose, onSuccess }: LeaveRequestModalProps) {
    const [formData, setFormData] = useState<CreateLeaveRequestData>({
        leave_type: '',
        start_date: '',
        end_date: '',
        reason: '',
    });
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState<Record<string, string>>({});

    const handleInputChange = (field: keyof CreateLeaveRequestData, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        // Clear error when user starts typing
        if (errors[field]) {
            setErrors(prev => ({ ...prev, [field]: '' }));
        }
    };

    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        if (!formData.leave_type) {
            newErrors.leave_type = 'Leave type is required';
        }

        if (!formData.start_date) {
            newErrors.start_date = 'Start date is required';
        }

        if (!formData.end_date) {
            newErrors.end_date = 'End date is required';
        }

        if (formData.start_date && formData.end_date) {
            const startDate = new Date(formData.start_date);
            const endDate = new Date(formData.end_date);

            if (startDate > endDate) {
                newErrors.end_date = 'End date must be after start date';
            }

            // Check if start date is not in the past
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            if (startDate < today) {
                newErrors.start_date = 'Start date cannot be in the past';
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setLoading(true);
        try {
            await createLeaveRequest(formData);
            onSuccess?.();
            onClose();
            // Reset form
            setFormData({
                leave_type: '',
                start_date: '',
                end_date: '',
                reason: '',
            });
        } catch (error) {
            console.error('Failed to create leave request:', error);
            setErrors({ submit: 'Failed to create leave request. Please try again.' });
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        if (!loading) {
            onClose();
            // Reset form when closing
            setFormData({
                leave_type: '',
                start_date: '',
                end_date: '',
                reason: '',
            });
            setErrors({});
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={handleClose} title="New Leave Request" size="md">
            <form onSubmit={handleSubmit} className="space-y-4">
                {/* Leave Type */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Leave Type *
                    </label>
                    <Select
                        value={formData.leave_type}
                        onChange={(e) => handleInputChange('leave_type', e.target.value)}
                        className={errors.leave_type ? 'border-red-500' : ''}
                    >
                        <option value="">Select leave type</option>
                        {LEAVE_TYPE_CHOICES.map(choice => (
                            <option key={choice.value} value={choice.value}>
                                {choice.label}
                            </option>
                        ))}
                    </Select>
                    {errors.leave_type && (
                        <p className="mt-1 text-sm text-red-600">{errors.leave_type}</p>
                    )}
                </div>

                {/* Start Date */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Start Date *
                    </label>
                    <Input
                        type="date"
                        value={formData.start_date}
                        onChange={(e) => handleInputChange('start_date', e.target.value)}
                        className={errors.start_date ? 'border-red-500' : ''}
                        min={new Date().toISOString().split('T')[0]}
                    />
                    {errors.start_date && (
                        <p className="mt-1 text-sm text-red-600">{errors.start_date}</p>
                    )}
                </div>

                {/* End Date */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        End Date *
                    </label>
                    <Input
                        type="date"
                        value={formData.end_date}
                        onChange={(e) => handleInputChange('end_date', e.target.value)}
                        className={errors.end_date ? 'border-red-500' : ''}
                        min={formData.start_date || new Date().toISOString().split('T')[0]}
                    />
                    {errors.end_date && (
                        <p className="mt-1 text-sm text-red-600">{errors.end_date}</p>
                    )}
                </div>

                {/* Reason */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Reason
                    </label>
                    <Textarea
                        value={formData.reason}
                        onChange={(e) => handleInputChange('reason', e.target.value)}
                        placeholder="Please provide a reason for your leave request..."
                        rows={3}
                    />
                </div>

                {/* Submit Error */}
                {errors.submit && (
                    <div className="bg-red-50 border border-red-200 rounded-md p-3">
                        <p className="text-sm text-red-600">{errors.submit}</p>
                    </div>
                )}

                {/* Actions */}
                <div className="flex justify-end space-x-3 pt-4">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={handleClose}
                        disabled={loading}
                    >
                        Cancel
                    </Button>
                    <Button
                        type="submit"
                        disabled={loading}
                        className="min-w-[100px]"
                    >
                        {loading ? 'Submitting...' : 'Submit Request'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
}