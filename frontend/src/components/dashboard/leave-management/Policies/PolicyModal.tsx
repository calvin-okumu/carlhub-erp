"use client";

import { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Button from '@/components/ui/Button';
import { LeavePolicy } from '@/api/types';

interface PolicyModalProps {
    isOpen: boolean;
    onClose: () => void;
    policy?: LeavePolicy | null;
    onSave: (data: PolicyFormData) => Promise<void>;
    isLoading?: boolean;
}

export interface PolicyFormData {
    leave_type: string;
    annual_entitlement: number;
    max_consecutive_days: number;
    notice_period_days: number;
    carry_over_allowed: boolean;
    max_carry_over?: number;
    auto_approve_max_days?: number;
    is_active: boolean;
}

export default function PolicyModal({
    isOpen,
    onClose,
    policy,
    onSave,
    isLoading = false
}: PolicyModalProps) {
    const [formData, setFormData] = useState<PolicyFormData>({
        leave_type: '',
        annual_entitlement: 0,
        max_consecutive_days: 0,
        notice_period_days: 0,
        carry_over_allowed: false,
        max_carry_over: undefined,
        auto_approve_max_days: undefined,
        is_active: true,
    });

    const [errors, setErrors] = useState<Record<string, string>>({});

    // Reset form when modal opens/closes or policy changes
    useEffect(() => {
        if (isOpen) {
            if (policy) {
                // Editing existing policy
                setFormData({
                    leave_type: policy.leave_type,
                    annual_entitlement: policy.annual_entitlement,
                    max_consecutive_days: policy.max_consecutive_days,
                    notice_period_days: policy.notice_period_days,
                    carry_over_allowed: policy.carry_over_allowed,
                    max_carry_over: policy.max_carry_over,
                    auto_approve_max_days: policy.auto_approve_max_days,
                    is_active: policy.is_active,
                });
            } else {
                // Creating new policy
                setFormData({
                    leave_type: '',
                    annual_entitlement: 0,
                    max_consecutive_days: 0,
                    notice_period_days: 0,
                    carry_over_allowed: false,
                    max_carry_over: undefined,
                    auto_approve_max_days: undefined,
                    is_active: true,
                });
            }
            setErrors({});
        }
    }, [isOpen, policy]);

    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        if (!formData.leave_type) {
            newErrors.leave_type = 'Leave type is required';
        }

        if (formData.annual_entitlement <= 0) {
            newErrors.annual_entitlement = 'Annual entitlement must be greater than 0';
        }

        if (formData.max_consecutive_days <= 0) {
            newErrors.max_consecutive_days = 'Max consecutive days must be greater than 0';
        }

        if (formData.notice_period_days < 0) {
            newErrors.notice_period_days = 'Notice period cannot be negative';
        }

        if (formData.carry_over_allowed && (!formData.max_carry_over || formData.max_carry_over <= 0)) {
            newErrors.max_carry_over = 'Max carry over must be greater than 0 when carry over is allowed';
        }

        if (formData.auto_approve_max_days !== undefined && formData.auto_approve_max_days <= 0) {
            newErrors.auto_approve_max_days = 'Auto approve days must be greater than 0';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        try {
            await onSave(formData);
            onClose();
        } catch (error) {
            console.error('Failed to save policy:', error);
        }
    };

    const handleInputChange = (field: keyof PolicyFormData, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));

        // Clear error for this field when user starts typing
        if (errors[field]) {
            setErrors(prev => ({ ...prev, [field]: '' }));
        }
    };

    const leaveTypeOptions = [
        { value: 'annual', label: 'Annual Leave' },
        { value: 'sick', label: 'Sick Leave' },
        { value: 'casual', label: 'Casual Leave' },
        { value: 'maternity', label: 'Maternity Leave' },
        { value: 'paternity', label: 'Paternity Leave' },
        { value: 'unpaid', label: 'Unpaid Leave' },
    ];

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title={policy ? 'Edit Leave Policy' : 'Create Leave Policy'}
            size="lg"
        >
            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Leave Type */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Leave Type *
                    </label>
                    <Select
                        value={formData.leave_type}
                        onChange={(e) => handleInputChange('leave_type', e.target.value)}
                        className={errors.leave_type ? 'border-red-500' : ''}
                    >
                        <option value="">Select leave type</option>
                        {leaveTypeOptions.map(option => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </Select>
                    {errors.leave_type && (
                        <p className="text-red-500 text-sm mt-1">{errors.leave_type}</p>
                    )}
                </div>

                {/* Annual Entitlement */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Annual Entitlement (days) *
                    </label>
                    <Input
                        type="number"
                        value={formData.annual_entitlement || ''}
                        onChange={(e) => handleInputChange('annual_entitlement', parseInt(e.target.value) || 0)}
                        min="1"
                        className={errors.annual_entitlement ? 'border-red-500' : ''}
                    />
                    {errors.annual_entitlement && (
                        <p className="text-red-500 text-sm mt-1">{errors.annual_entitlement}</p>
                    )}
                </div>

                {/* Max Consecutive Days */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Max Consecutive Days *
                    </label>
                    <Input
                        type="number"
                        value={formData.max_consecutive_days || ''}
                        onChange={(e) => handleInputChange('max_consecutive_days', parseInt(e.target.value) || 0)}
                        min="1"
                        className={errors.max_consecutive_days ? 'border-red-500' : ''}
                    />
                    {errors.max_consecutive_days && (
                        <p className="text-red-500 text-sm mt-1">{errors.max_consecutive_days}</p>
                    )}
                </div>

                {/* Notice Period */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Notice Period (days) *
                    </label>
                    <Input
                        type="number"
                        value={formData.notice_period_days || ''}
                        onChange={(e) => handleInputChange('notice_period_days', parseInt(e.target.value) || 0)}
                        min="0"
                        className={errors.notice_period_days ? 'border-red-500' : ''}
                    />
                    {errors.notice_period_days && (
                        <p className="text-red-500 text-sm mt-1">{errors.notice_period_days}</p>
                    )}
                </div>

                {/* Carry Over Settings */}
                <div className="space-y-4">
                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            id="carry_over_allowed"
                            checked={formData.carry_over_allowed}
                            onChange={(e) => handleInputChange('carry_over_allowed', e.target.checked)}
                            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <label htmlFor="carry_over_allowed" className="ml-2 text-sm font-medium text-gray-700">
                            Allow Carry Over
                        </label>
                    </div>

                    {formData.carry_over_allowed && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Max Carry Over (days)
                            </label>
                            <Input
                                type="number"
                                value={formData.max_carry_over || ''}
                                onChange={(e) => handleInputChange('max_carry_over', e.target.value ? parseInt(e.target.value) : undefined)}
                                min="1"
                                className={errors.max_carry_over ? 'border-red-500' : ''}
                            />
                            {errors.max_carry_over && (
                                <p className="text-red-500 text-sm mt-1">{errors.max_carry_over}</p>
                            )}
                        </div>
                    )}
                </div>

                {/* Auto Approve */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Auto Approve ≤ (days)
                    </label>
                    <Input
                        type="number"
                        value={formData.auto_approve_max_days || ''}
                        onChange={(e) => handleInputChange('auto_approve_max_days', e.target.value ? parseInt(e.target.value) : undefined)}
                        min="1"
                        placeholder="Leave empty to disable auto-approval"
                        className={errors.auto_approve_max_days ? 'border-red-500' : ''}
                    />
                    {errors.auto_approve_max_days && (
                        <p className="text-red-500 text-sm mt-1">{errors.auto_approve_max_days}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                        Requests up to this many days will be automatically approved
                    </p>
                </div>

                {/* Active Status */}
                <div className="flex items-center">
                    <input
                        type="checkbox"
                        id="is_active"
                        checked={formData.is_active}
                        onChange={(e) => handleInputChange('is_active', e.target.checked)}
                        className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="is_active" className="ml-2 text-sm font-medium text-gray-700">
                        Policy is Active
                    </label>
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-4 border-t">
                    <Button
                        type="submit"
                        variant="gradient"
                        disabled={isLoading}
                        className="flex-1"
                    >
                        {isLoading ? 'Saving...' : (policy ? 'Update Policy' : 'Create Policy')}
                    </Button>
                    <Button
                        type="button"
                        variant="outline"
                        onClick={onClose}
                        disabled={isLoading}
                    >
                        Cancel
                    </Button>
                </div>
            </form>
        </Modal>
    );
};