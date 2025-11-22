"use client";

import { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import { createLeaveRequest, updateLeaveRequest } from '@/api/leave';
import type { CreateLeaveRequestData, LeaveRequest } from '@/api/types';
import { Calendar, Heart, User, Baby, AlertTriangle, CreditCard } from 'lucide-react';

interface LeaveRequestModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
    editingRequest?: LeaveRequest | null;
}

const LEAVE_TYPE_CHOICES = [
    { 
        value: 'annual_leave', 
        label: 'Annual Leave', 
        icon: Calendar,
        description: 'Planned vacation time',
        color: 'blue'
    },
    { 
        value: 'sick_leave', 
        label: 'Sick Leave', 
        icon: Heart,
        description: 'Health-related absence',
        color: 'red'
    },
    { 
        value: 'personal_leave', 
        label: 'Personal Leave', 
        icon: User,
        description: 'Personal matters',
        color: 'purple'
    },
    { 
        value: 'maternity_leave', 
        label: 'Maternity/Paternity Leave', 
        icon: Baby,
        description: 'Family care time',
        color: 'pink'
    },
    { 
        value: 'emergency_leave', 
        label: 'Emergency Leave', 
        icon: AlertTriangle,
        description: 'Urgent situations',
        color: 'orange'
    },
    { 
        value: 'unpaid_leave', 
        label: 'Unpaid Leave', 
        icon: CreditCard,
        description: 'Leave without pay',
        color: 'gray'
    },
];

export default function LeaveRequestModal({ isOpen, onClose, onSuccess, editingRequest }: LeaveRequestModalProps) {
    const isEditing = !!editingRequest;
    const [formData, setFormData] = useState<CreateLeaveRequestData>({
        leave_type: '',
        start_date: '',
        end_date: '',
        reason: '',
    });

    // Update form data when editing request changes
    useEffect(() => {
        if (editingRequest) {
            setFormData({
                leave_type: editingRequest.leave_type,
                start_date: editingRequest.start_date,
                end_date: editingRequest.end_date,
                reason: editingRequest.reason,
            });
        } else {
            setFormData({
                leave_type: '',
                start_date: '',
                end_date: '',
                reason: '',
            });
        }
    }, [editingRequest]);
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
            if (isEditing && editingRequest) {
                await updateLeaveRequest(editingRequest.id, formData);
            } else {
                await createLeaveRequest(formData);
            }
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
        <Modal isOpen={isOpen} onClose={handleClose} title={isEditing ? "Edit Leave Request" : "New Leave Request"} size="md">
            <form onSubmit={handleSubmit} className="space-y-4">
                {/* Leave Type */}
                <div>
                    <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-blue-500" />
                        Leave Type *
                    </label>
                    <Select
                        value={formData.leave_type}
                        onChange={(value) => handleInputChange('leave_type', value)}
                        options={LEAVE_TYPE_CHOICES}
                        placeholder="Select leave type"
                        showIcons={true}
                        className={errors.leave_type ? 'border-red-500 ring-red-500' : ''}
                    />
                    {errors.leave_type && (
                        <div className="mt-2 flex items-center gap-2 text-sm text-red-600 bg-red-50 p-2 rounded-md">
                            <AlertTriangle className="w-4 h-4" />
                            {errors.leave_type}
                        </div>
                    )}
                </div>

                {/* Start Date */}
                <div>
                    <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-green-500" />
                        Start Date *
                    </label>
                    <Input
                        type="date"
                        value={formData.start_date}
                        onChange={(e) => handleInputChange('start_date', e.target.value)}
                        className={`p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${
                            errors.start_date ? 'border-red-500 ring-red-500' : 'hover:border-gray-400'
                        }`}
                        min={new Date().toISOString().split('T')[0]}
                    />
                    {errors.start_date && (
                        <div className="mt-2 flex items-center gap-2 text-sm text-red-600 bg-red-50 p-2 rounded-md">
                            <AlertTriangle className="w-4 h-4" />
                            {errors.start_date}
                        </div>
                    )}
                </div>

                {/* End Date */}
                <div>
                    <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-red-500" />
                        End Date *
                    </label>
                    <Input
                        type="date"
                        value={formData.end_date}
                        onChange={(e) => handleInputChange('end_date', e.target.value)}
                        className={`p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${
                            errors.end_date ? 'border-red-500 ring-red-500' : 'hover:border-gray-400'
                        }`}
                        min={formData.start_date || new Date().toISOString().split('T')[0]}
                    />
                    {errors.end_date && (
                        <div className="mt-2 flex items-center gap-2 text-sm text-red-600 bg-red-50 p-2 rounded-md">
                            <AlertTriangle className="w-4 h-4" />
                            {errors.end_date}
                        </div>
                    )}
                </div>

                {/* Reason */}
                <div>
                    <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                        <User className="w-4 h-4 text-purple-500" />
                        Reason
                    </label>
                    <Textarea
                        value={formData.reason}
                        onChange={(e) => handleInputChange('reason', e.target.value)}
                        placeholder="Please provide a reason for your leave request..."
                        rows={3}
                        className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 resize-none"
                    />
                </div>

                {/* Submit Error */}
                {errors.submit && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-sm font-medium text-red-800">Submission Error</p>
                            <p className="text-sm text-red-600 mt-1">{errors.submit}</p>
                        </div>
                    </div>
                )}

                {/* Actions */}
                <div className="flex justify-end gap-3 pt-6 border-t border-gray-200">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={handleClose}
                        disabled={loading}
                        className="px-6 py-2.5 font-medium hover:bg-gray-50 transition-colors duration-200"
                    >
                        Cancel
                    </Button>
                    <Button
                        type="submit"
                        disabled={loading}
                        className={`px-6 py-2.5 font-medium transition-all duration-200 ${
                            loading 
                                ? 'bg-gray-400 cursor-not-allowed' 
                                : 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg transform hover:-translate-y-0.5'
                        }`}
                    >
                        {loading ? (
                            <span className="flex items-center gap-2">
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                {isEditing ? 'Updating...' : 'Submitting...'}
                            </span>
                        ) : (
                            isEditing ? 'Update Request' : 'Submit Request'
                        )}
                    </Button>
                </div>
            </form>
        </Modal>
    );
}