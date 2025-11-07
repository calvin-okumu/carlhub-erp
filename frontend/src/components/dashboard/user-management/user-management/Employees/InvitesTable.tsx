import React from 'react';
import Table from '@/components/ui/Table';
import Button from '@/components/ui/Button';
import StatusBadge from '@/components/ui/StatusBadge';

interface Invite {
    id: number;
    email: string;
    sentDate: string;
    status: string;
}

interface InvitesTableProps {
    searchTerm: string;
    entriesPerPage: number;
    currentPage: number;
    invites?: Invite[];
    totalPages?: number;
    onPageChange?: (page: number) => void;
    itemsPerPage?: number;
    totalItems?: number;
    onResendInvite?: (inviteId: number) => void;
    onDeleteInvite?: (inviteId: number) => void;
}

export default function InvitesTable({ searchTerm, entriesPerPage, currentPage, invites = [], totalPages, onPageChange, itemsPerPage, totalItems, onResendInvite, onDeleteInvite }: InvitesTableProps) {
    const filteredInvites = invites.filter(invite =>
        invite.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const startIndex = (currentPage - 1) * entriesPerPage;
    const paginatedInvites = filteredInvites.slice(startIndex, startIndex + entriesPerPage);

    if (filteredInvites.length === 0) {
        return (
            <div className="text-center py-8">
                <p className="text-gray-500">No invitations sent</p>
            </div>
        );
    }

    const headers = ['Email Address', 'Last Sent', 'Status', 'Resend', 'Delete'];

    const rows = paginatedInvites.map(invite => ({
        key: invite.id,
        data: [
            invite.email,
            invite.sentDate,
            <StatusBadge key="status" status={invite.status} />,
            <Button key="resend" className="bg-blue-600 text-white" onClick={() => onResendInvite?.(invite.id)}>Resend</Button>,
            <Button key="delete" className="bg-red-600 text-white" onClick={() => onDeleteInvite?.(invite.id)}>Delete</Button>,
        ],
    }));

    return <Table headers={headers} rows={rows} currentPage={currentPage} totalPages={totalPages} onPageChange={onPageChange} itemsPerPage={itemsPerPage} totalItems={totalItems} />;
}