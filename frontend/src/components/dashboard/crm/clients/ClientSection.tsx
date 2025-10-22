"use client";

import React, { useState } from 'react';
import ClientHeader from './ClientHeader';
import ClientTable from './ClientTable';
import ClientModal from './ClientModal';
import { useClients } from '@/hooks/useClients';
import type { Client, CreateClientData, UpdateClientData } from '@/api/types';

export default function ClientSection() {
    const { clients, loading, error, addClient, editClient, removeClient } = useClients();
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedClient, setSelectedClient] = useState<Client | null>(null);
    const [searchValue, setSearchValue] = useState('');

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
                searchValue={searchValue}
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

