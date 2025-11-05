import React from 'react';
import Table from '@/components/ui/Table';
import Button from '@/components/ui/Button';

interface User {
    id: number;
    name: string;
    avatar: string;
    email: string;
    job_title?: string;
    last_login?: string;
    role: string;
    status: string;
}

interface ActiveUsersTableProps {
    searchTerm: string;
    entriesPerPage: number;
    currentPage: number;
    users?: User[];
    totalPages?: number;
    onPageChange?: (page: number) => void;
    itemsPerPage?: number;
    totalItems?: number;
}

export default function ActiveUsersTable({ searchTerm, entriesPerPage, currentPage, users = [], totalPages, onPageChange, itemsPerPage, totalItems }: ActiveUsersTableProps) {
    const filteredUsers = users.filter(user =>
        user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const startIndex = (currentPage - 1) * entriesPerPage;
    const paginatedUsers = filteredUsers.slice(startIndex, startIndex + entriesPerPage);

    if (filteredUsers.length === 0) {
        return (
            <div className="text-center py-8">
                <p className="text-gray-500">No active users</p>
            </div>
        );
    }

    const headers = ['User', 'Email', 'Job Title', 'Last Login', 'Role', 'View'];

    const rows = paginatedUsers.map(user => ({
        key: user.id,
        data: [
            <div key="user" className="flex items-center">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium mr-3">
                    {user.avatar}
                </div>
                {user.name}
            </div>,
            user.email,
            user.job_title || 'N/A',
            user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never',
             user.role,
            <Button key="view" className="bg-blue-600 text-white">View</Button>,
        ],
    }));

    return <Table headers={headers} rows={rows} currentPage={currentPage} totalPages={totalPages} onPageChange={onPageChange} itemsPerPage={itemsPerPage} totalItems={totalItems} />;
}