"use client";

import React, { useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import type { Client, CreateClientData, UpdateClientData } from '@/api/types';
import { useForm } from 'react-hook-form';

interface ClientModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'add' | 'edit';
    client?: Client;
    onSave: (data: CreateClientData | UpdateClientData) => void;
}

type FormData = {
    name: string;
    email: string;
    phone: string;
    status: 'active' | 'inactive' | 'prospect';
};

export default function ClientModal({ isOpen, onClose, mode, client, onSave }: ClientModalProps) {
    const { register, handleSubmit, setValue, formState: { errors } } = useForm<FormData>({
        defaultValues: {
            name: '',
            email: '',
            phone: '',
            status: 'active',
        }
    });

    useEffect(() => {
        if (mode === 'edit' && client) {
            setValue('name', client.name);
            setValue('email', client.email);
            setValue('phone', client.phone || '');
            setValue('status', client.status as 'active' | 'inactive' | 'prospect');
        } else {
            setValue('name', '');
            setValue('email', '');
            setValue('phone', '');
            setValue('status', 'active');
        }
    }, [mode, client, isOpen, setValue]);

    const onSubmit = (data: FormData) => {
        if (!data.name || !data.email) return;

        const submitData = {
            name: data.name,
            email: data.email,
            phone: data.phone || undefined,
            status: data.status,
        };

        onSave(submitData);
    };



    return (
        <Modal isOpen={isOpen} onClose={onClose} title={mode === 'add' ? 'Add Client' : 'Edit Client'} size="md">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700">Name *</label>
                    <input
                        type="text"
                        id="name"
                        {...register("name", { required: "Name is required" })}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                    {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>}
                </div>
                <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email *</label>
                    <input
                        type="email"
                        id="email"
                        {...register("email", { required: "Email is required", pattern: { value: /^\S+@\S+$/i, message: "Invalid email address" } })}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                    {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
                </div>
                <div>
                    <label htmlFor="phone" className="block text-sm font-medium text-gray-700">Phone</label>
                    <input
                        type="tel"
                        id="phone"
                        {...register("phone")}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>
                <div>
                    <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
                    <select
                        id="status"
                        {...register("status")}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="prospect">Prospect</option>
                    </select>
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                    <Button type="button" onClick={onClose} variant="outline">
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary">
                        {mode === 'add' ? 'Add Client' : 'Update Client'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};

