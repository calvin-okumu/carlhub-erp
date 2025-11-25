import type { Client } from '@/api/types';
import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import Table from '@/components/ui/Table';
import { Edit, Trash2 } from 'lucide-react';

interface ClientTableProps {
    clients: Client[];
    loading: boolean;
    error: string | null;
    onEditClient: (client: Client) => void;
    onDeleteClient: (slug: string) => void;
    pagination?: {
        count: number;
        next: string | null;
        previous: string | null;
    } | null;
    currentPage: number;
    onPageChange: (page: number) => void;
    searchValue: string;
}

export default function ClientTable({ clients = [], loading, error, onEditClient, onDeleteClient, pagination, currentPage, onPageChange, searchValue }: ClientTableProps) {

    const handleEdit = (client: Client) => {
        onEditClient(client);
    };

    const handleDelete = (slug: string) => {
        if (confirm("Are you sure you want to delete this client?")) {
            onDeleteClient(slug);
        }
    };

    const headers = ["Name", "Email", "Phone", "Status", "Created", "Actions"];

    const rows = clients.map(client => ({
        key: client.id,
        data: [
            client.name,
            client.email,
            client.phone || "-",
            <span
                key={client.id + '-status'}
                className={`px-2 py-1 text-xs font-semibold rounded-full ${client.status === 'active'
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
                <Button onClick={() => handleDelete(client.slug)} variant="danger" size="sm">
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

    if (!loading && !error && clients.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 p-8 text-center text-gray-500">
                {searchValue ? `No clients found matching "${searchValue}"` : 'No clients found'}
            </div>
        );
    }

    const totalPages = pagination ? Math.ceil(pagination.count / 10) : 1;

    return (
        <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
            <Table
                headers={headers}
                rows={rows}
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={onPageChange}
                itemsPerPage={10}
                totalItems={pagination?.count || clients.length}
            />
        </div>
    );
};

