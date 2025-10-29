"use client";
import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';

interface EmployeeModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'add' | 'edit';
}

export default function EmployeeModal({ isOpen, onClose, mode }: EmployeeModalProps) {
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        jobTitle: '',
        dateOfBirth: '',
        employmentStartDate: '',
        employmentEndDate: '',
        emergencyContact: '',
        emergencyPhone: '',
        status: 'active',
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Handle form submission, e.g., API call
        console.log('Submitting:', formData);
        onClose();
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={mode === 'add' ? 'Add Employee' : 'Edit Employee'}>
            <div className="p-6">
                <form onSubmit={handleSubmit}>
                    <div className="grid grid-cols-2 gap-4 mb-6">
                        {/* Row 1 */}
                        <div>
                            <Input
                                placeholder="First Name"
                                value={formData.firstName}
                                onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <Input
                                placeholder="Last Name"
                                value={formData.lastName}
                                onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                                required
                            />
                        </div>

                        {/* Row 2 */}
                        <div>
                            <Input
                                placeholder="Email"
                                type="email"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <Input
                                placeholder="Phone"
                                value={formData.phone}
                                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                required
                            />
                        </div>

                        {/* Row 3 */}
                        <div>
                            <Input
                                placeholder="Job Title"
                                value={formData.jobTitle}
                                onChange={(e) => setFormData({ ...formData, jobTitle: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Date of Birth
                            </label>
                            <Input
                                placeholder="Select employee's date of birth"
                                type="date"
                                value={formData.dateOfBirth}
                                onChange={(e) => setFormData({ ...formData, dateOfBirth: e.target.value })}
                                required
                            />
                        </div>

                        {/* Row 4 */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Employment Start Date
                            </label>
                            <Input
                                placeholder="Select when employment begins"
                                type="date"
                                value={formData.employmentStartDate}
                                onChange={(e) => setFormData({ ...formData, employmentStartDate: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Employment End Date (Optional)
                            </label>
                            <Input
                                placeholder="Select when employment ends (leave empty if ongoing)"
                                type="date"
                                value={formData.employmentEndDate}
                                onChange={(e) => setFormData({ ...formData, employmentEndDate: e.target.value })}
                            />
                        </div>

                        {/* Row 5 */}
                        <div>
                            <Input
                                placeholder="Emergency Contact"
                                value={formData.emergencyContact}
                                onChange={(e) => setFormData({ ...formData, emergencyContact: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <Input
                                placeholder="Emergency Phone"
                                value={formData.emergencyPhone}
                                onChange={(e) => setFormData({ ...formData, emergencyPhone: e.target.value })}
                                required
                            />
                        </div>

                        {/* Row 6 - Status dropdown spans full width */}
                        <div className="col-span-2">
                            <Select
                                value={formData.status}
                                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                                required
                            >
                                <option value="active">Active</option>
                                <option value="inactive">Inactive</option>
                            </Select>
                        </div>
                    </div>

                    <div className="flex justify-end space-x-2">
                        <Button type="button" onClick={onClose} variant='secondary'>
                            Cancel
                        </Button>
                        <Button type="submit" className="bg-blue-600 text-white">
                            {mode === 'add' ? 'Add' : 'Update'}
                        </Button>
                    </div>
                </form>
            </div>
        </Modal>
    );
}
