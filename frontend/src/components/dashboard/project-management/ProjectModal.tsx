"use client";

import type { Project } from '@/api/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Modal from '@/components/ui/Modal';
import Select from '@/components/ui/Select';
import { useClients } from '@/hooks/useClients';
import type { ProjectFormData } from '@/types/project';
import React, { useEffect, useState } from 'react';

interface ProjectModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'add' | 'edit';
    project?: Project;
    onSave: (data: ProjectFormData) => Promise<void>;
}

export default function ProjectModal({ isOpen, onClose, mode, project, onSave }: ProjectModalProps) {
    const { clients, currentTenant, refetch } = useClients();
    const [formData, setFormData] = useState<{
        name: string;
        client: string;
        status: 'planning' | 'active' | 'on_hold' | 'completed' | 'archived';
        priority: 'high' | 'medium' | 'low';
        start_date: string;
        end_date: string;
        budget: string;
    }>({
        name: '',
        client: '',
        status: 'active',
        priority: 'medium',
        start_date: '',
        end_date: '',
        budget: '',
    });

    useEffect(() => {
        if (isOpen) {
            // Fetch clients when modal opens
            refetch();
        }
    }, [isOpen, refetch]);

    useEffect(() => {
        const tenantClients = currentTenant
            ? clients.filter((client) => String(client.tenant) === String(currentTenant.tenant))
            : clients;

        if (mode === 'edit' && project) {
            setFormData({
                name: project.name,
                client: project.client,
                status: project.status as 'planning' | 'active' | 'on_hold' | 'completed' | 'archived',
                priority: project.priority as 'high' | 'medium' | 'low',
                start_date: project.start_date,
                end_date: project.end_date,
                budget: project.budget || '',
            });
        } else {
            setFormData({
                name: '',
                client: tenantClients.length > 0 ? tenantClients[0].id : '',
                status: 'active',
                priority: 'medium',
                start_date: '',
                end_date: '',
                budget: '',
            });
        }
    }, [mode, project, clients, currentTenant]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        if (name === 'client') {
            setFormData(prev => ({ ...prev, client: value }));
            return;
        }
        setFormData(prev => ({ ...prev, [name]: value }));
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
                    <Input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        className="mt-1"
                    />
                </div>
                <div>
                    <label htmlFor="client" className="block text-sm font-medium text-gray-700">Client *</label>
                    <Select
                        id="client"
                        name="client"
                        value={formData.client}
                        onChange={handleChange}
                        required
                        className="mt-1"
                    >
                        {(currentTenant
                            ? clients.filter((client) => String(client.tenant) === String(currentTenant.tenant))
                            : clients
                        ).map(client => (
                            <option key={client.id} value={client.id}>{client.name}</option>
                        ))}
                    </Select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
                        <Select
                            id="status"
                            name="status"
                            value={formData.status}
                            onChange={handleChange}
                            className="mt-1"
                        >
                            <option value="planning">Planning</option>
                            <option value="active">Active</option>
                            <option value="on_hold">On Hold</option>
                            <option value="completed">Completed</option>
                            <option value="archived">Archived</option>
                        </Select>
                    </div>
                    <div>
                        <label htmlFor="priority" className="block text-sm font-medium text-gray-700">Priority</label>
                        <Select
                            id="priority"
                            name="priority"
                            value={formData.priority}
                            onChange={handleChange}
                            className="mt-1"
                        >
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                        </Select>
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">Start Date *</label>
                        <Input
                            type="date"
                            id="start_date"
                            name="start_date"
                            value={formData.start_date}
                            onChange={handleChange}
                            required
                            className="mt-1"
                        />
                    </div>
                    <div>
                        <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">End Date *</label>
                        <Input
                            type="date"
                            id="end_date"
                            name="end_date"
                            value={formData.end_date}
                            onChange={handleChange}
                            required
                            className="mt-1"
                        />
                    </div>
                </div>
                <div>
                    <label htmlFor="budget" className="block text-sm font-medium text-gray-700">Budget</label>
                    <Input
                        type="text"
                        id="budget"
                        name="budget"
                        value={formData.budget}
                        onChange={handleChange}
                        placeholder="e.g., 50000"
                        className="mt-1"
                    />
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                    <Button onClick={onClose} variant='secondary'>
                        Cancel
                    </Button>
                     <Button type="submit">
                         {mode === 'add' ? 'Add Project' : 'Update Project'}
                     </Button>
                </div>
            </form>
        </Modal>
    );
}
