"use client";

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import type { Milestone, UserTenant } from '@/api/types';

interface MilestoneModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'add' | 'edit';
    milestone?: Milestone;
    projectId: number;
    tenant: number;
    assignees: UserTenant[];
    projectStart?: string;
    projectEnd?: string;
    onSave: (data: {
        name: string;
        description?: string;
        status: string;
        planned_start?: string;
        actual_start?: string;
        due_date?: string;
        assignee?: number;
        project: number;
        tenant: number;
    }) => void;
}

export default function MilestoneModal({ isOpen, onClose, mode, milestone, projectId, tenant, assignees, projectStart, projectEnd, onSave }: MilestoneModalProps) {
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        status: 'pending',
        planned_start: '',

        due_date: '',
        assignee: '',
    });
    const [errors, setErrors] = useState<{[key: string]: string}>({});

    useEffect(() => {
        if (mode === 'edit' && milestone) {
            setFormData({
                name: milestone.name,
                description: milestone.description || '',
                status: milestone.status,
                planned_start: milestone.planned_start || '',

                due_date: milestone.due_date || '',
                assignee: milestone.assignee?.toString() || '',
            });
        } else {
            setFormData({
                name: '',
                description: '',
                status: 'planning',
                planned_start: '',
       
                due_date: '',
                assignee: '',
            });
        }
        setErrors({});
    }, [mode, milestone, isOpen]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (name === 'planned_start') {
            if (value && projectStart && value < projectStart) {
                setErrors(prev => ({ ...prev, planned_start: 'Milestone planned start date cannot be before the project start date.' }));
            } else {
                setErrors(prev => {
                    const { planned_start, ...rest } = prev;
                    return rest;
                });
            }
        }
        if (name === 'due_date') {
            if (value && projectEnd && value > projectEnd) {
                setErrors(prev => ({ ...prev, due_date: 'Milestone due date cannot be after the project end date.' }));
            } else {
                setErrors(prev => {
                    const { due_date, ...rest } = prev;
                    return rest;
                });
            }
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.name) return;

        if (Object.keys(errors).length > 0) return;

        const data = {
            name: formData.name,
            description: formData.description || undefined,
            status: formData.status,
            progress: 0,
            planned_start: formData.planned_start || undefined,

            due_date: formData.due_date || undefined,
            assignee: formData.assignee ? parseInt(formData.assignee) : undefined,
            project: projectId,
            tenant: tenant,
        };

        onSave(data);
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={mode === 'add' ? 'Add Milestone' : 'Edit Milestone'} size="md">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700">Name *</label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>
                <div>
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description</label>
                    <textarea
                        id="description"
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        rows={3}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>
                <div>
                    <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
                    <select
                        id="status"
                        name="status"
                        value={formData.status}
                        onChange={handleChange}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                        <option value="planning">Planning</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
                 <div>
                     <label htmlFor="planned_start" className="block text-sm font-medium text-gray-700">Planned Start</label>
                     <input
                         type="date"
                         id="planned_start"
                         name="planned_start"
                         value={formData.planned_start}
                         onChange={handleChange}
                         min={projectStart}
                         max={projectEnd}
                         className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${errors.planned_start ? 'border-red-500' : 'border-gray-300'}`}
                     />
                     {errors.planned_start && <p className="text-red-500 text-sm mt-1">{errors.planned_start}</p>}
                 </div>

                 <div>
                     <label htmlFor="due_date" className="block text-sm font-medium text-gray-700">Due Date</label>
                     <input
                         type="date"
                         id="due_date"
                         name="due_date"
                         value={formData.due_date}
                         onChange={handleChange}
                         min={projectStart}
                         max={projectEnd}
                         className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${errors.due_date ? 'border-red-500' : 'border-gray-300'}`}
                     />
                     {errors.due_date && <p className="text-red-500 text-sm mt-1">{errors.due_date}</p>}
                 </div>
                <div>
                    <label htmlFor="assignee" className="block text-sm font-medium text-gray-700">Assignee</label>
                    <select
                        id="assignee"
                        name="assignee"
                        value={formData.assignee}
                        onChange={handleChange}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                        <option value="">Select Assignee</option>
                        {assignees.map(user => (
                            <option key={user.user} value={user.user}>
                                {user.user_first_name} {user.user_last_name}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                    <Button type="button" onClick={onClose} variant="outline">
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary">
                        {mode === 'add' ? 'Add Milestone' : 'Update Milestone'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};