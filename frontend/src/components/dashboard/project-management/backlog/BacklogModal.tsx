"use client";

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import type { Task, Sprint, UserTenant } from '@/api/types';

interface BacklogModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'add' | 'edit';
    task?: Task;
    sprints: Sprint[];
    assignees: UserTenant[];
    onSave: (data: {
        title: string;
        description?: string;
        status: string;
        milestone: number;
        sprint?: number;
        assignee?: number;
        start_date?: string;
        end_date?: string;
        estimated_hours?: number;
    }) => void;
}

export default function BacklogModal({ isOpen, onClose, mode, task, sprints, assignees, onSave }: BacklogModalProps) {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
                status: 'todo',
        priority: 'medium',
        sprint: '',
        assignee: '',
        start_date: '',
        end_date: '',
        estimated_hours: '',
    });
    const [minDate, setMinDate] = useState('');
    const [maxDate, setMaxDate] = useState('');
    const [errors, setErrors] = useState<{[key: string]: string}>({});

    useEffect(() => {
        if (mode === 'edit' && task) {
            setFormData({
                title: task.title,
                description: task.description || '',
                status: task.status,
                priority: task.priority || 'medium',
                sprint: task.sprint?.toString() || '',
                assignee: task.assignee?.toString() || '',
                start_date: task.start_date || '',
                end_date: task.end_date || '',
                estimated_hours: task.estimated_hours?.toString() || '',
            });
            const sprint = sprints.find(s => s.id === task.sprint);
            if (sprint) {
                setMinDate(sprint.start_date || '');
                setMaxDate(sprint.end_date || '');
            }
        } else {
            setFormData({
                title: '',
                description: '',
        status: 'todo',
                priority: 'medium',
                sprint: '',
                assignee: '',
                start_date: '',
                end_date: '',
                estimated_hours: '',
            });
            setMinDate('');
            setMaxDate('');
        }
        setErrors({});
    }, [mode, task, isOpen, sprints]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (name === 'sprint') {
            const sprint = sprints.find(s => s.id.toString() === value);
            if (sprint) {
                setMinDate(sprint.start_date || '');
                setMaxDate(sprint.end_date || '');
                // Re-validate dates after sprint change
                const newErrors = { ...errors };
                if (formData.start_date && sprint.start_date && formData.start_date < sprint.start_date) {
                    newErrors.start_date = 'Task start date cannot be before the sprint\'s start date.';
                } else {
                    delete newErrors.start_date;
                }
                if (formData.end_date && sprint.end_date && formData.end_date > sprint.end_date) {
                    newErrors.end_date = 'Task end date cannot be after the sprint\'s end date.';
                } else {
                    delete newErrors.end_date;
                }
                setErrors(newErrors);
            } else {
                setMinDate('');
                setMaxDate('');
                setErrors(prev => {
                    const { start_date, end_date, ...rest } = prev;
                    return rest;
                });
            }
        }
        if (name === 'start_date') {
            if (value && minDate && value < minDate) {
                setErrors(prev => ({ ...prev, start_date: 'Task start date cannot be before the sprint\'s start date.' }));
            } else {
                setErrors(prev => {
                    const { start_date, ...rest } = prev;
                    return rest;
                });
            }
        }
        if (name === 'end_date') {
            if (value && maxDate && value > maxDate) {
                setErrors(prev => ({ ...prev, end_date: 'Task end date cannot be after the sprint\'s end date.' }));
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
        if (!formData.title) return;

        if (Object.keys(errors).length > 0) return;

        let milestoneId: number;
        if (formData.sprint) {
            const sprint = sprints.find(s => s.id === parseInt(formData.sprint));
            if (!sprint) return;
            milestoneId = sprint.milestone;
        } else {
            // For backlog, perhaps require sprint, or set to a default milestone
            // For now, assume sprint is required for milestone
            alert('Please select a sprint to assign the milestone.');
            return;
        }

        const data = {
            title: formData.title,
            description: formData.description || undefined,
            status: formData.status,
            milestone: milestoneId,
            sprint: formData.sprint ? parseInt(formData.sprint) : undefined,
            assignee: formData.assignee ? parseInt(formData.assignee) : undefined,
            start_date: formData.start_date || undefined,
            end_date: formData.end_date || undefined,
            estimated_hours: formData.estimated_hours ? parseInt(formData.estimated_hours) : undefined,
        };

        onSave(data);
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={mode === 'add' ? 'Add Task' : 'Edit Task'} size="md">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700">Title *</label>
                    <input
                        type="text"
                        id="title"
                        name="title"
                        value={formData.title}
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
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
                        <select
                            id="status"
                            name="status"
                            value={formData.status}
                            onChange={handleChange}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="todo">To Do</option>
                            <option value="in_progress">In Progress</option>
                            <option value="in_review">Review</option>
                            <option value="testing">Testing</option>
                            <option value="done">Done</option>
                            <option value="completed">Completed</option>
                        </select>
                    </div>
                    <div>
                        <label htmlFor="priority" className="block text-sm font-medium text-gray-700">Priority</label>
                        <select
                            id="priority"
                            name="priority"
                            value={formData.priority}
                            onChange={handleChange}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                </div>
                <div>
                    <label htmlFor="sprint" className="block text-sm font-medium text-gray-700">Sprint (Optional)</label>
                    <select
                        id="sprint"
                        name="sprint"
                        value={formData.sprint}
                        onChange={handleChange}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                        <option value="">No Sprint</option>
                        {sprints.map(sprint => (
                            <option key={sprint.id} value={sprint.id}>
                                {sprint.name}
                            </option>
                        ))}
                    </select>
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
                 <div className="grid grid-cols-2 gap-4">
                     <div>
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
                 </div>
                <div>
                    <label htmlFor="estimated_hours" className="block text-sm font-medium text-gray-700">Estimated Hours</label>
                    <input
                        type="number"
                        id="estimated_hours"
                        name="estimated_hours"
                        value={formData.estimated_hours}
                        onChange={handleChange}
                        min="0"
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                    <Button type="button" onClick={onClose} variant="outline">
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary">
                        {mode === 'add' ? 'Add Task' : 'Update Task'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};