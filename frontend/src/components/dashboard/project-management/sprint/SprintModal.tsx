"use client";

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import type { Sprint, Milestone } from '@/api/types';

interface SprintModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'add' | 'edit';
    sprint?: Sprint;

    milestones: Milestone[];
    onSave: (data: {
        name: string;
        status: string;
        start_date?: string;
        end_date?: string;
        milestone: number;
    }) => void;
}

export default function SprintModal({ isOpen, onClose, mode, sprint, milestones, onSave }: SprintModalProps) {
    const [formData, setFormData] = useState({
        name: '',
        status: 'planned',
        start_date: '',
        end_date: '',
        milestone: '',
    });
    const [minDate, setMinDate] = useState('');
    const [maxDate, setMaxDate] = useState('');
    const [errors, setErrors] = useState<{ [key: string]: string }>({});

    useEffect(() => {
        if (mode === 'edit' && sprint) {
            setFormData({
                name: sprint.name,
                status: sprint.status,
                start_date: sprint.start_date || '',
                end_date: sprint.end_date || '',
                milestone: sprint.milestone?.toString() || '',
            });
            const milestone = milestones.find(m => m.id === sprint.milestone);
            if (milestone) {
                setMinDate(milestone.planned_start || '');
                setMaxDate(milestone.due_date || '');
            }
        } else {
            setFormData({
                name: '',
                status: 'planned',
                start_date: '',
                end_date: '',
                milestone: '',
            });
            setMinDate('');
            setMaxDate('');
        }
        setErrors({});
    }, [mode, sprint, isOpen, milestones]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (name === 'milestone') {
            const milestone = milestones.find(m => m.id.toString() === value);
            if (milestone) {
                setMinDate(milestone.planned_start || '');
                setMaxDate(milestone.due_date || '');
            } else {
                setMinDate('');
                setMaxDate('');
            }
            // Re-validate dates after milestone change
            const newErrors = { ...errors };
            if (formData.start_date && milestone && formData.start_date < (milestone.planned_start || '')) {
                newErrors.start_date = 'Sprint start date cannot be before the milestone\'s planned start date.';
            } else {
                delete newErrors.start_date;
            }
            if (formData.end_date && milestone && formData.end_date > (milestone.due_date || '')) {
                newErrors.end_date = 'Sprint end date cannot be after the milestone\'s due date.';
            } else {
                delete newErrors.end_date;
            }
            setErrors(newErrors);
        }
        if (name === 'start_date') {
            if (value && minDate && value < minDate) {
                setErrors(prev => ({ ...prev, start_date: 'Sprint start date cannot be before the milestone\'s planned start date.' }));
            } else {
                setErrors(prev => {
                    const { start_date, ...rest } = prev;
                    return rest;
                });
            }
        }
        if (name === 'end_date') {
            if (value && maxDate && value > maxDate) {
                setErrors(prev => ({ ...prev, end_date: 'Sprint end date cannot be after the milestone\'s due date.' }));
            } else {
                setErrors(prev => {
                    const { end_date, ...rest } = prev;
                    return rest;
                });
            }
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.name || !formData.milestone) return;

        if (Object.keys(errors).length > 0) return;

        const data = {
            name: formData.name,
            status: formData.status,
            start_date: formData.start_date || undefined,
            end_date: formData.end_date || undefined,
            milestone: parseInt(formData.milestone),
        };

        onSave(data);
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={mode === 'add' ? 'Add Sprint' : 'Edit Sprint'} size="md">
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
                    <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
                    <select
                        id="status"
                        name="status"
                        value={formData.status}
                        onChange={handleChange}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                        <option value="planned">Planned</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="canceled">Canceled</option>
                    </select>
                </div>
                <div>
                    <div>
                        <label htmlFor="milestone" className="block text-sm font-medium text-gray-700">Milestone *</label>
                        <select
                            id="milestone"
                            name="milestone"
                            value={formData.milestone}
                            onChange={handleChange}
                            required
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="">Select Milestone</option>
                            {milestones.map(milestone => (
                                <option key={milestone.id} value={milestone.id}>
                                    {milestone.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">Start Date</label>
                    <input
                        type="date"
                        id="start_date"
                        name="start_date"
                        value={formData.start_date}
                        onChange={handleChange}
                        min={minDate}
                        max={maxDate}
                        className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${errors.start_date ? 'border-red-500' : 'border-gray-300'}`}
                    />
                    {errors.start_date && <p className="text-red-500 text-sm mt-1">{errors.start_date}</p>}
                </div>
                <div>
                    <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">End Date</label>
                    <input
                        type="date"
                        id="end_date"
                        name="end_date"
                        value={formData.end_date}
                        onChange={handleChange}
                        min={minDate}
                        max={maxDate}
                        className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${errors.end_date ? 'border-red-500' : 'border-gray-300'}`}
                    />
                    {errors.end_date && <p className="text-red-500 text-sm mt-1">{errors.end_date}</p>}
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                    <Button type="button" onClick={onClose} variant="outline">
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary">
                        {mode === 'add' ? 'Add Sprint' : 'Update Sprint'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};
