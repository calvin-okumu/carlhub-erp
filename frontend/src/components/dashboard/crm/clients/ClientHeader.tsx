"use client";

import { getClients } from '@/api/crm';
import type { Client } from '@/api/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import StatCard from '@/components/ui/StatCard';
import { getAccessToken } from '@/utils/auth';
import { UserCheck, UserPlus, Users } from 'lucide-react';
import { useEffect, useState } from 'react';

interface ClientHeaderProps {
    onAddClient: () => void;
    searchValue: string;
    onSearchChange: (value: string) => void;
}

export default function ClientHeader({ onAddClient, searchValue, onSearchChange }: ClientHeaderProps) {
    const [allClients, setAllClients] = useState<Client[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAllClients = async () => {
            const token = getAccessToken();
            if (!token) return;

            try {
                // Fetch all clients with a high limit for metrics calculation
                const data = await getClients(token, { limit: 1000 });

                // Handle both paginated and non-paginated responses
                if (data && typeof data === 'object' && 'results' in data) {
                    setAllClients(data.results);
                } else {
                    setAllClients(data as Client[]);
                }
            } catch (error) {
                console.error('Failed to fetch clients for metrics:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchAllClients();
    }, []);

    const clients = allClients;

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
                <Input
                    type="text"
                    placeholder="Search clients..."
                    value={searchValue}
                    onChange={(e) => onSearchChange(e.target.value)}
                    className="max-w-xs"
                />
                <Button onClick={handleAddClient}>
                    + Add Client
                </Button>
            </div>
        </div>
    );
};


