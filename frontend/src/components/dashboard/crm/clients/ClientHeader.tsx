"use client";

import React from 'react';
import { Users, UserCheck, UserPlus } from 'lucide-react';
import StatCard from '@/components/ui/StatCard';
import Button from '@/components/ui/Button';

import { useClients } from '@/hooks/useClients';

interface ClientHeaderProps {
    onAddClient: () => void;
    searchValue: string;
    onSearchChange: (value: string) => void;
}

export default function ClientHeader({ onAddClient, searchValue, onSearchChange }: ClientHeaderProps) {
    const { clients } = useClients();

    const totalClients = clients.length;
    const activeClients = clients.filter(c => c.status === 'active').length;
    const prospects = clients.filter(c => c.status === 'prospect').length;
    const newClientsThisMonth = clients.filter(c => {
        const created = new Date(c.created_at);
        const now = new Date();
        return created.getMonth() === now.getMonth() && created.getFullYear() === now.getFullYear();
    }).length;

    const handleAddClient = () => {
        onAddClient();
    };

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Clients"
                    value={totalClients}
                    icon={Users}
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <StatCard
                    title="Active Clients"
                    value={activeClients}
                    icon={UserCheck}
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <StatCard
                    title="Prospects"
                    value={prospects}
                    icon={UserPlus}
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <StatCard
                    title="New This Month"
                    value={newClientsThisMonth}
                    icon={UserPlus}
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
            </div>
            <div className="flex justify-between items-center">
                <input
                    type="text"
                    placeholder="Search clients..."
                    value={searchValue}
                    onChange={(e) => onSearchChange(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <Button onClick={handleAddClient} variant="primary" size="md">
                    + Add Client
                </Button>
            </div>
        </div>
    );
};


