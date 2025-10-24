"use client";

import React, { useState, useEffect } from 'react';
import ClientHeader from './ClientHeader';
import ClientTable from './ClientTable';
import ClientModal from './ClientModal';
import { useClients } from '@/hooks/useClients';
import type { Client, CreateClientData, UpdateClientData } from '@/api/types';

export default function ClientSection() {
    const [currentPage, setCurrentPage] = useState(1);
    const [searchValue, setSearchValue] = useState('');
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedClient, setSelectedClient] = useState<Client | null>(null);
    const { clients, loading, error, pagination, addClient, editClient, removeClient, refetch } = useClients();

    useEffect(() => {
        refetch({ page: currentPage, limit: 10, search: searchValue });
    }, [currentPage, searchValue, refetch]);

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
    };

    const handleAddClient = () => {
        setModalMode('add');
        setSelectedClient(null);
        setModalOpen(true);
    };

    const handleEditClient = (client: Client) => {
        setModalMode('edit');
        setSelectedClient(client);
        setModalOpen(true);
    };

    const handleSaveClient = async (data: CreateClientData | UpdateClientData) => {
        try {
            if (modalMode === 'add') {
                await addClient(data as CreateClientData);
            } else if (selectedClient) {
                await editClient(selectedClient.id, data as UpdateClientData);
            }
            setModalOpen(false);
        } catch (error) {
            console.error('Error saving client:', error);
            // TODO: Show error message
        }
    };

    return (
        <div className="space-y-6">
            <ClientHeader onAddClient={handleAddClient} searchValue={searchValue} onSearchChange={setSearchValue} />
            <ClientTable
                clients={clients}
                loading={loading}
                error={error}
                onEditClient={handleEditClient}
                onDeleteClient={removeClient}
                pagination={pagination}
                currentPage={currentPage}
                onPageChange={handlePageChange}
            />
            <ClientModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                mode={modalMode}
                client={selectedClient || undefined}
                onSave={handleSaveClient}
            />
        </div>
    );
};

