"use client";

import type { Client, CreateClientData, UpdateClientData } from '@/api/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Modal from '@/components/ui/Modal';
import Select from '@/components/ui/Select';
import { useEffect } from 'react';
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
                    <Input
                        type="text"
                        id="name"
                        {...register("name", { required: "Name is required" })}
                    />
                    {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>}
                </div>
                <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email *</label>
                    <Input
                        type="email"
                        id="email"
                        {...register("email", { required: "Email is required", pattern: { value: /^\S+@\S+$/i, message: "Invalid email address" } })}
                    />
                    {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
                </div>
                <div>
                    <label htmlFor="phone" className="block text-sm font-medium text-gray-700">Phone</label>
                    <Input
                        type="tel"
                        id="phone"
                        {...register("phone")}
                    />
                </div>
                <div>
                    <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
                    <Select
                        id="status"
                        {...register("status")}
                    >
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="prospect">Prospect</option>
                    </Select>
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                    <Button type="button" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button type="submit">
                        {mode === 'add' ? 'Add Client' : 'Update Client'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};

