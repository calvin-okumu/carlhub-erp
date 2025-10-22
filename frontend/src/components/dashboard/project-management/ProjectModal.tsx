"use client";

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useClients } from '@/hooks/useClients';
import type { Project } from '@/api/types';
import type { ProjectFormData } from '@/types/project';

interface ProjectModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'add' | 'edit';
    project?: Project;
    onSave: (data: ProjectFormData) => Promise<void>;
}

export default function ProjectModal({ isOpen, onClose, mode, project, onSave }: ProjectModalProps) {
    const { clients } = useClients();
    const [formData, setFormData] = useState({
        name: '',
        client: 0,
        status: 'active' as 'active' | 'completed' | 'on-hold',
        priority: 'medium' as 'high' | 'medium' | 'low',
        start_date: '',
        end_date: '',
        budget: '',
    });

    useEffect(() => {
        if (mode === 'edit' && project) {
            setFormData({
                name: project.name,
                client: project.client,
                status: project.status as 'active' | 'completed' | 'on-hold',
                priority: project.priority as 'high' | 'medium' | 'low',
                start_date: project.start_date,
                end_date: project.end_date,
                budget: project.budget || '',
            });
        } else {
            setFormData({
                name: '',
                client: clients.length > 0 ? clients[0].id : 0,
                status: 'active',
                priority: 'medium',
                start_date: '',
                end_date: '',
                budget: '',
            });
        }
    }, [mode, project, clients]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: name === 'client' ? parseInt(value) : value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.name || !formData.client || !formData.start_date || !formData.end_date) return;

        const startDate = new Date(formData.start_date);
        const endDate = new Date(formData.end_date);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (startDate < today) {
            alert("Start date cannot be in the past.");
            return;
        }

        if (endDate <= startDate) {
            alert("End date must be after start date.");
            return;
        }

        await onSave({
            name: formData.name,
            client: formData.client,
            status: formData.status,
            priority: formData.priority,
            start_date: formData.start_date,
            end_date: formData.end_date,
            budget: formData.budget || undefined,
        });
    };



    return (
        <Modal isOpen={isOpen} onClose={onClose} title={mode === 'add' ? 'Add Project' : 'Edit Project'} size="md">
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
                    <label htmlFor="client" className="block text-sm font-medium text-gray-700">Client *</label>
                    <select
                        id="client"
                        name="client"
                        value={formData.client.toString()}
                        onChange={handleChange}
                        required
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                        {clients.map(client => (
                            <option key={client.id} value={client.id}>{client.name}</option>
                        ))}
                    </select>
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
                            <option value="active">Active</option>
                            <option value="completed">Completed</option>
                            <option value="on-hold">On Hold</option>
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
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                        </select>
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">Start Date *</label>
                        <input
                            type="date"
                            id="start_date"
                            name="start_date"
                            value={formData.start_date}
                            onChange={handleChange}
                            required
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                    </div>
                    <div>
                        <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">End Date *</label>
                        <input
                            type="date"
                            id="end_date"
                            name="end_date"
                            value={formData.end_date}
                            onChange={handleChange}
                            required
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                    </div>
                </div>
                <div>
                    <label htmlFor="budget" className="block text-sm font-medium text-gray-700">Budget</label>
                    <input
                        type="text"
                        id="budget"
                        name="budget"
                        value={formData.budget}
                        onChange={handleChange}
                        placeholder="e.g., 50000"
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                    <Button type="button" onClick={onClose} variant="outline">
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary">
                        {mode === 'add' ? 'Add Project' : 'Update Project'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
}