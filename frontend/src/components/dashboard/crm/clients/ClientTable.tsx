"use client";

import React, { useState } from 'react';
import Table from '@/components/ui/Table';
import Pagination from '@/components/shared/Pagination';
import Loader from '@/components/shared/Loader';
import type { Client } from '@/api/types';
import { Edit, Trash2 } from 'lucide-react';
import Button from '@/components/ui/Button';

interface ClientTableProps {
    clients: Client[];
    loading: boolean;
    error: string | null;
    onEditClient: (client: Client) => void;
    onDeleteClient: (id: number) => void;
    searchValue: string;
}

export default function ClientTable({ clients, loading, error, onEditClient, onDeleteClient, searchValue }: ClientTableProps) {
    const [page, setPage] = useState(1);

    const filteredClients = clients.filter(client =>
        client.name.toLowerCase().includes(searchValue.toLowerCase()) ||
        client.email.toLowerCase().includes(searchValue.toLowerCase())
    );

    const itemsPerPage = 10;
    const totalPages = Math.ceil(filteredClients.length / itemsPerPage);
    const visibleClients = filteredClients.slice((page - 1) * itemsPerPage, page * itemsPerPage);

    const handleEdit = (client: Client) => {
        onEditClient(client);
    };

    const handleDelete = (id: number) => {
        if (confirm("Are you sure you want to delete this client?")) {
            onDeleteClient(id);
        }
    };

    const headers = ["Name", "Email", "Phone", "Status", "Created", "Actions"];

    const rows = visibleClients.map(client => ({
        key: client.id,
        data: [
        client.name,
        client.email,
        client.phone || "-",
        <span
            key={client.id + '-status'}
            className={`px-2 py-1 text-xs font-semibold rounded-full ${
                client.status === 'active'
                    ? 'bg-green-100 text-green-800'
                    : client.status === 'inactive'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
            }`}
        >
            {client.status}
        </span>,
        new Date(client.created_at).toLocaleDateString(),
        <div key={client.id + '-actions'} className="flex gap-2">
            <Button onClick={() => handleEdit(client)} variant="outline" size="sm">
                <Edit className="h-4 w-4" />
            </Button>
            <Button onClick={() => handleDelete(client.id)} variant="danger" size="sm">
                <Trash2 className="h-4 w-4" />
            </Button>
        </div>
        ]
    }));

    if (loading) {
        return <Loader />;
    }

    if (error) {
        return <div className="text-red-500">{error}</div>;
    }

    return (
        <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
            <Table headers={headers} rows={rows} />
            <Pagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={setPage}
                itemsPerPage={itemsPerPage}
                totalItems={filteredClients.length}
            />
        </div>
    );
};

