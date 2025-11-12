"use client";
import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import { createUser, updateUser } from '@/api/users';
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
        // Basic Information
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        job_title: '',

        // Employment Details
        employee_id: '',
        employee_number: '',
        hire_date: '',

        // Address Information
        street_address: '',
        city: '',
        state_province: '',
        postal_code: '',
        country: '',

        // Emergency Contact
        emergency_contact: '',
        emergency_phone: '',

        // Medical Information
        medical_aid_provider: '',
        medical_aid_plan: '',
        medical_aid_number: '',
        medical_conditions: '',
        allergies: '',
        medications: '',

        // Banking Information
        bank_name: '',
        account_number: '',
        branch_code: '',
        account_type: '',
        routing_number: '',
        swift_code: '',

        // Status
        is_active: true,
    });

    const [loading, setLoading] = useState(false);

    // Initialize form data when modal opens or employee changes
    React.useEffect(() => {
        if (mode === 'edit' && employee) {
            setFormData({
                first_name: employee.first_name || '',
                last_name: employee.last_name || '',
                email: employee.email || '',
                phone: employee.phone || '',
                job_title: employee.job_title || '',

                employee_id: employee.employee_id || '',
                employee_number: employee.employee_number || '',
                hire_date: employee.hire_date || '',

                street_address: employee.street_address || '',
                city: employee.city || '',
                state_province: employee.state_province || '',
                postal_code: employee.postal_code || '',
                country: employee.country || '',

                emergency_contact: employee.emergency_contact || '',
                emergency_phone: employee.emergency_phone || '',

                medical_aid_provider: employee.medical_aid_provider || '',
                medical_aid_plan: employee.medical_aid_plan || '',
                medical_aid_number: employee.medical_aid_number || '',
                medical_conditions: employee.medical_conditions || '',
                allergies: employee.allergies || '',
                medications: employee.medications || '',

                bank_name: employee.bank_name || '',
                account_number: employee.account_number || '',
                branch_code: employee.branch_code || '',
                account_type: employee.account_type || '',
                routing_number: employee.routing_number || '',
                swift_code: employee.swift_code || '',

                is_active: employee.is_active ?? true,
            });
        } else if (mode === 'add') {
            // Reset form for add mode
            setFormData({
                first_name: '',
                last_name: '',
                email: '',
                phone: '',
                job_title: '',
                employee_id: '',
                employee_number: '',
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
                is_active: true,
            });
        }
    }, [mode, employee, isOpen]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            setLoading(true);

            // Validate required fields
            if (!formData.first_name || !formData.last_name || !formData.email || !formData.phone || !formData.job_title) {
                alert('Please fill in all required fields');
                return;
            }

            const token = localStorage.getItem('access_token');
            if (!token) {
                alert('No access token found. Please log in again.');
                return;
            }

            let result;
            if (mode === 'add') {
                result = await createUser(token, formData);
            } else if (mode === 'edit' && employee?.id) {
                result = await updateUser(token, employee.id, formData);
            }

            // Call the onSave callback if provided
            if (onSave && result) {
                onSave(result as UserProfile);
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
                            .map(([key, value]) => `${key}: ${(value as string[]).join(', ')}`)
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
                <form onSubmit={handleSubmit} className="space-y-8">
                    {/* Basic Information Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">Basic Information</h3>
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
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Phone *
                                </label>
                                <Input
                                    placeholder="Enter phone number"
                                    value={formData.phone}
                                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Job Title *
                                </label>
                                <Input
                                    placeholder="Enter job title"
                                    value={formData.job_title}
                                    onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
                                    required
                                />
                            </div>
                        </div>
                    </div>

                    {/* Employment Details Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">Employment Details</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Employee ID
                                </label>
                                <Input
                                    placeholder="Enter employee ID"
                                    value={formData.employee_id}
                                    onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Employee Number
                                </label>
                                <Input
                                    placeholder="Enter employee number"
                                    value={formData.employee_number}
                                    onChange={(e) => setFormData({ ...formData, employee_number: e.target.value })}
                                />
                            </div>
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Hire Date
                                </label>
                                <Input
                                    placeholder="Select hire date"
                                    type="date"
                                    value={formData.hire_date}
                                    onChange={(e) => setFormData({ ...formData, hire_date: e.target.value })}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Address Information Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">Address Information</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Street Address
                                </label>
                                <Input
                                    placeholder="Enter street address"
                                    value={formData.street_address}
                                    onChange={(e) => setFormData({ ...formData, street_address: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    City
                                </label>
                                <Input
                                    placeholder="Enter city"
                                    value={formData.city}
                                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    State/Province
                                </label>
                                <Input
                                    placeholder="Enter state or province"
                                    value={formData.state_province}
                                    onChange={(e) => setFormData({ ...formData, state_province: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Postal Code
                                </label>
                                <Input
                                    placeholder="Enter postal code"
                                    value={formData.postal_code}
                                    onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Country
                                </label>
                                <Input
                                    placeholder="Enter country"
                                    value={formData.country}
                                    onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Emergency Contact Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">Emergency Contact</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Emergency Contact Name
                                </label>
                                <Input
                                    placeholder="Enter emergency contact name"
                                    value={formData.emergency_contact}
                                    onChange={(e) => setFormData({ ...formData, emergency_contact: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Emergency Contact Phone
                                </label>
                                <Input
                                    placeholder="Enter emergency contact phone"
                                    value={formData.emergency_phone}
                                    onChange={(e) => setFormData({ ...formData, emergency_phone: e.target.value })}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Medical Information Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">Medical Information</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Medical Aid Provider
                                </label>
                                <Input
                                    placeholder="Enter medical aid provider"
                                    value={formData.medical_aid_provider}
                                    onChange={(e) => setFormData({ ...formData, medical_aid_provider: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Medical Aid Plan
                                </label>
                                <Input
                                    placeholder="Enter medical aid plan"
                                    value={formData.medical_aid_plan}
                                    onChange={(e) => setFormData({ ...formData, medical_aid_plan: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Medical Aid Number
                                </label>
                                <Input
                                    placeholder="Enter medical aid number"
                                    value={formData.medical_aid_number}
                                    onChange={(e) => setFormData({ ...formData, medical_aid_number: e.target.value })}
                                />
                            </div>
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Medical Conditions
                                </label>
                                <Textarea
                                    placeholder="Enter any medical conditions"
                                    value={formData.medical_conditions}
                                    onChange={(e) => setFormData({ ...formData, medical_conditions: e.target.value })}
                                    rows={3}
                                />
                            </div>
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Allergies
                                </label>
                                <Textarea
                                    placeholder="Enter any allergies"
                                    value={formData.allergies}
                                    onChange={(e) => setFormData({ ...formData, allergies: e.target.value })}
                                    rows={3}
                                />
                            </div>
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Medications
                                </label>
                                <Textarea
                                    placeholder="Enter current medications"
                                    value={formData.medications}
                                    onChange={(e) => setFormData({ ...formData, medications: e.target.value })}
                                    rows={3}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Banking Information Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">Banking Information</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Bank Name
                                </label>
                                <Input
                                    placeholder="Enter bank name"
                                    value={formData.bank_name}
                                    onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Account Number
                                </label>
                                <Input
                                    placeholder="Enter account number"
                                    value={formData.account_number}
                                    onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Branch Code
                                </label>
                                <Input
                                    placeholder="Enter branch code"
                                    value={formData.branch_code}
                                    onChange={(e) => setFormData({ ...formData, branch_code: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Account Type
                                </label>
                                <Select
                                    value={formData.account_type}
                                    onChange={(e) => setFormData({ ...formData, account_type: e.target.value })}
                                >
                                    <option value="">Select account type</option>
                                    <option value="checking">Checking</option>
                                    <option value="savings">Savings</option>
                                    <option value="business">Business</option>
                                </Select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Routing Number
                                </label>
                                <Input
                                    placeholder="Enter routing number"
                                    value={formData.routing_number}
                                    onChange={(e) => setFormData({ ...formData, routing_number: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    SWIFT Code
                                </label>
                                <Input
                                    placeholder="Enter SWIFT code"
                                    value={formData.swift_code}
                                    onChange={(e) => setFormData({ ...formData, swift_code: e.target.value })}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Status Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">Status</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Employment Status *
                                </label>
                                <Select
                                    value={formData.is_active ? 'active' : 'inactive'}
                                    onChange={(e) => setFormData({ ...formData, is_active: e.target.value === 'active' })}
                                    required
                                >
                                    <option value="active">Active</option>
                                    <option value="inactive">Inactive</option>
                                </Select>
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end space-x-2 pt-6 border-t">
                        <Button type="button" onClick={onClose} variant='secondary'>
                            Cancel
                        </Button>
                        <Button type="submit" className="bg-blue-600 text-white">
                            {mode === 'add' ? 'Add Employee' : 'Update Employee'}
                        </Button>
                    </div>
                </form>
            </div>
        </Modal>
    );
}
