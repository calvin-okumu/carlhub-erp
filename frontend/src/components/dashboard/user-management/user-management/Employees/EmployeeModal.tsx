"use client";
import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface EmployeeModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'add' | 'edit';
}

export default function EmployeeModal({ isOpen, onClose, mode }: EmployeeModalProps) {
    const [formData, setFormData] = useState({
        name: '',
        jobTitle: '',
        email: '',
        phone: '',
        employmentDate: '',
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
                <h2 className="text-lg font-medium mb-4">{mode === 'add' ? 'Add Employee' : 'Edit Employee'}</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <Input
                            placeholder="Name"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            required
                        />
                    </div>
                    <div className="mb-4">
                        <Input
                            placeholder="Job Title"
                            value={formData.jobTitle}
                            onChange={(e) => setFormData({ ...formData, jobTitle: e.target.value })}
                            required
                        />
                    </div>
                    <div className="mb-4">
                        <Input
                            placeholder="Email"
                            type="email"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            required
                        />
                    </div>
                    <div className="mb-4">
                        <Input
                            placeholder="Phone"
                            value={formData.phone}
                            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                            required
                        />
                    </div>
                    <div className="mb-4">
                        <Input
                            placeholder="Employment Date"
                            type="date"
                            value={formData.employmentDate}
                            onChange={(e) => setFormData({ ...formData, employmentDate: e.target.value })}
                            required
                        />
                    </div>
                    <div className="flex justify-end space-x-2">
                        <Button type="button" onClick={onClose} className="bg-gray-500 text-white">
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