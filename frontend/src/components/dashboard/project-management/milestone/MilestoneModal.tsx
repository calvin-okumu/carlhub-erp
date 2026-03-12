"use client";

import type { Milestone, UserTenant } from '@/api/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Modal from '@/components/ui/Modal';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import React, { useEffect, useState } from 'react';

interface MilestoneModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'add' | 'edit';
    milestone?: Milestone;
    projectSlug: string;
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
        project: string;
    }) => void;
}

export default function MilestoneModal({ isOpen, onClose, mode, milestone, projectSlug, assignees, projectStart, projectEnd, onSave }: MilestoneModalProps) {
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        status: 'planning',
        planned_start: '',
        due_date: '',
        assignee: '',
    });
    const [errors, setErrors] = useState<{ [key: string]: string }>({});

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
            setErrors(prev => {
                const next = { ...prev };
                if (value && projectStart && value < projectStart) {
                    next.planned_start = 'Milestone planned start date cannot be before the project start date.';
                } else if (formData.due_date && value && value >= formData.due_date) {
                    next.planned_start = 'Planned start date must be before the due date.';
                } else {
                    delete next.planned_start;
                }
                if (formData.due_date && value && value >= formData.due_date) {
                    next.due_date = 'Due date must be after the planned start date.';
                } else if (next.due_date === 'Due date must be after the planned start date.') {
                    delete next.due_date;
                }
                return next;
            });
        }
        if (name === 'due_date') {
            setErrors(prev => {
                const next = { ...prev };
                if (value && projectEnd && value > projectEnd) {
                    next.due_date = 'Milestone due date cannot be after the project end date.';
                } else if (formData.planned_start && value && value <= formData.planned_start) {
                    next.due_date = 'Due date must be after the planned start date.';
                } else {
                    delete next.due_date;
                }
                if (formData.planned_start && value && value <= formData.planned_start) {
                    next.planned_start = 'Planned start date must be before the due date.';
                } else if (next.planned_start === 'Planned start date must be before the due date.') {
                    delete next.planned_start;
                }
                return next;
            });
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
            planned_start: formData.planned_start || undefined,
            due_date: formData.due_date || undefined,
            assignee: formData.assignee ? parseInt(formData.assignee) : undefined,
            project: projectSlug,
        };

        onSave(data);
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={mode === 'add' ? 'Add Milestone' : 'Edit Milestone'} size="md">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700">Name *</label>
                    <Input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description</label>
                    <Textarea
                        id="description"
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        rows={3}
                    />
                </div>
                <div>
                    <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
                    <Select
                        id="status"
                        name="status"
                        value={formData.status}
                        onChange={handleChange}
                    >
                        <option value="planning">Planning</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                    </Select>
                </div>
                <div>
                    <label htmlFor="planned_start" className="block text-sm font-medium text-gray-700">Planned Start</label>
                    <Input
                        type="date"
                        id="planned_start"
                        name="planned_start"
                        value={formData.planned_start}
                        onChange={handleChange}
                        min={projectStart}
                        max={projectEnd}
                        className={errors.planned_start ? 'border-red-500' : ''}
                    />
                    {errors.planned_start && <p className="text-red-500 text-sm mt-1">{errors.planned_start}</p>}
                </div>

                <div>
                    <label htmlFor="due_date" className="block text-sm font-medium text-gray-700">Due Date</label>
                    <Input
                        type="date"
                        id="due_date"
                        name="due_date"
                        value={formData.due_date}
                        onChange={handleChange}
                        min={projectStart}
                        max={projectEnd}
                        className={errors.due_date ? 'border-red-500' : ''}
                    />
                    {errors.due_date && <p className="text-red-500 text-sm mt-1">{errors.due_date}</p>}
                </div>
                <div>
                    <label htmlFor="assignee" className="block text-sm font-medium text-gray-700">Assignee</label>
                    <Select
                        id="assignee"
                        name="assignee"
                        value={formData.assignee}
                        onChange={handleChange}
                    >
                        <option value="">Select Assignee</option>
                        {Array.isArray(assignees) && assignees.map(user => (
                            <option key={user.user} value={user.user}>
                                {user.user_first_name} {user.user_last_name}
                            </option>
                        ))}
                    </Select>
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                    <Button type="button" onClick={onClose} variant='secondary'>
                        Cancel
                    </Button>
                    <Button type="submit">
                        {mode === 'add' ? 'Add Milestone' : 'Update Milestone'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};
