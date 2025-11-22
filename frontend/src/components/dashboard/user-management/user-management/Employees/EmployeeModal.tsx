"use client";
import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { createMember, updateUser, getCurrentUser } from '@/api/users';
import { getAccessToken } from '@/utils/auth';
import type { UserProfile } from '@/api/types';

interface EmployeeModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'add' | 'edit';
    employee?: UserProfile; // For edit mode
    onSave?: (employee: UserProfile) => void; // Callback after successful save
}

export default function EmployeeModal({ isOpen, onClose, mode, employee, onSave }: EmployeeModalProps) {
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        company_name: '',
    });

    const [loading, setLoading] = useState(false);
    const [currentUserOrg, setCurrentUserOrg] = useState('');

    // Fetch current user's organization
    useEffect(() => {
        const fetchCurrentUserOrg = async () => {
            try {
                const token = getAccessToken();
                if (token) {
                    const currentUser = await getCurrentUser(token);
                    setCurrentUserOrg(currentUser.organization || '');
                }
            } catch (error) {
                console.error('Failed to fetch current user organization:', error);
            }
        };

        if (isOpen) {
            fetchCurrentUserOrg();
        }
    }, [isOpen]);

    // Initialize form data when modal opens or employee changes
    React.useEffect(() => {
        if (mode === 'edit' && employee) {
            setFormData({
                first_name: employee.first_name || '',
                last_name: employee.last_name || '',
                email: employee.email || '',
                password: '', // Password not shown in edit mode
                company_name: currentUserOrg,
            });
        } else if (mode === 'add') {
            // Reset form for add mode
            setFormData({
                first_name: '',
                last_name: '',
                email: '',
                password: '',
                company_name: currentUserOrg,
            });
        }
    }, [mode, employee, isOpen, currentUserOrg]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            setLoading(true);

            // Validate required fields
            if (!formData.first_name || !formData.last_name || !formData.email || !formData.password) {
                alert('Please fill in all required fields');
                return;
            }

            const token = getAccessToken();
            if (!token) {
                alert('No access token found. Please log in again.');
                return;
            }

            let result;
            if (mode === 'add') {
                result = await createMember(token, {
                    email: formData.email,
                    password: formData.password,
                    first_name: formData.first_name,
                    last_name: formData.last_name,
                });
            } else if (mode === 'edit' && employee?.id) {
                // For edit mode, we still use updateUser but with simplified data
                result = await updateUser(token, employee.id, {
                    first_name: formData.first_name,
                    last_name: formData.last_name,
                    email: formData.email,
                });
            }

            // Call the onSave callback if provided
            if (onSave && result) {
                // Convert User to UserProfile format with default values
                const userProfile: UserProfile = {
                    id: result.id,
                    user: result.id,
                    first_name: result.first_name,
                    last_name: result.last_name,
                    email: result.email,
                    job_title: '',
                    phone: '',
                    linkedin_profile: '',
                    employee_id: '',
                    employee_number: '',
                    tax_number: '',
                    hire_date: '',
                    street_address: '',
                    city: '',
                    state_province: '',
                    postal_code: '',
                    country: '',
                    emergency_contact: '',
                    emergency_phone: '',
                    medical_aid_provider: '',
                    medical_aid_plan: '',
                    medical_aid_number: '',
                    medical_conditions: '',
                    allergies: '',
                    medications: '',
                    bank_name: '',
                    account_number: '',
                    branch_code: '',
                    account_type: '',
                    routing_number: '',
                    swift_code: '',
                    created_at: '',
                    updated_at: '',
                    is_active: true,
                    date_joined: result.date_joined,
                    organization: result.organization,
                };
                onSave(userProfile);
            }

            alert(`Employee ${mode === 'add' ? 'created' : 'updated'} successfully!`);
            onClose();

        } catch (error) {
            console.error('Error submitting employee data:', error);

            // Try to parse backend validation errors
            let errorMessage = `Failed to ${mode === 'add' ? 'create' : 'update'} employee. Please try again.`;

            if (error instanceof Error) {
                // Check if it's a backend validation error
                try {
                    const errorData = JSON.parse(error.message);
                    if (errorData && typeof errorData === 'object') {
                        const fieldErrors = Object.entries(errorData)
                            .filter(([key, value]) => Array.isArray(value))
                            .map(([key, _value]) => `${key}: ${(_value as string[]).join(', ')}`)
                            .join('\n');

                        if (fieldErrors) {
                            errorMessage = `Validation errors:\n${fieldErrors}`;
                        } else if (errorData.detail) {
                            errorMessage = errorData.detail;
                        } else if (errorData.error) {
                            errorMessage = errorData.error;
                        }
                    }
                } catch {
                    // If parsing fails, use the original error message
                    errorMessage = error.message || errorMessage;
                }
            }

            alert(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={mode === 'add' ? 'Add Employee' : 'Edit Employee'}>
            <div className="p-6 max-h-[80vh] overflow-y-auto">
                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Basic Information Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">Employee Information</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    First Name *
                                </label>
                                <Input
                                    placeholder="Enter first name"
                                    value={formData.first_name}
                                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Last Name *
                                </label>
                                <Input
                                    placeholder="Enter last name"
                                    value={formData.last_name}
                                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Email *
                                </label>
                                <Input
                                    placeholder="Enter email address"
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    required
                                />
                            </div>
                            {mode === 'add' && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Password *
                                    </label>
                                    <Input
                                        placeholder="Enter password"
                                        type="password"
                                        value={formData.password}
                                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                        required
                                    />
                                </div>
                            )}
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Company
                                </label>
                                <Input
                                    placeholder="Company name"
                                    value={formData.company_name}
                                    readOnly
                                    className="bg-gray-100"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end space-x-2 pt-6 border-t">
                        <Button type="button" onClick={onClose} variant='secondary'>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={loading} className="bg-blue-600 text-white">
                            {loading ? 'Processing...' : (mode === 'add' ? 'Add Employee' : 'Update Employee')}
                        </Button>
                    </div>
                </form>
            </div>
        </Modal>
    );
}
