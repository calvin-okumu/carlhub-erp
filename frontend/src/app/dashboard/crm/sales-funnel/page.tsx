"use client";

import React, { useState } from 'react';
import { Funnel, Users, Target, CheckCircle } from 'lucide-react';
import MetricsBar from '@/components/dashboard/crm/components/MetricsBar';
import ClientsSection from '@/components/dashboard/crm/components/ClientsSection';
import ClientModal from '@/components/dashboard/crm/clients/ClientModal';
import type { CreateClientData, UpdateClientData } from '@/api/types';

export default function SalesFunnelPage() {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const metrics = [
        {
            title: "Leads",
            value: 0,
            label: "Top of funnel",
            icon: Users,
            color: "border-blue-200",
        },
        {
            title: "Qualified Prospects",
            value: 0,
            label: "Qualified leads",
            icon: Target,
            color: "border-yellow-200",
        },
        {
            title: "Opportunities",
            value: 0,
            label: "Sales opportunities",
            icon: Funnel,
            color: "border-purple-200",
        },
        {
            title: "Closed Deals",
            value: 0,
            label: "Won customers",
            icon: CheckCircle,
            color: "border-green-200",
        },
    ];

    const filters = [
        {
            options: [
                { value: "all", label: "All Stages" },
                { value: "leads", label: "Leads" },
                { value: "prospects", label: "Prospects" },
                { value: "opportunities", label: "Opportunities" },
                { value: "customers", label: "Customers" },
            ],
            defaultValue: "all",
        },
        {
            options: [
                { value: "all", label: "All Sources" },
                { value: "inbound", label: "Inbound" },
                { value: "outbound", label: "Outbound" },
                { value: "referrals", label: "Referrals" },
                { value: "marketing", label: "Marketing" },
            ],
            defaultValue: "all",
        },
        {
            options: [
                { value: "all", label: "All Time" },
                { value: "this_month", label: "This Month" },
                { value: "last_30_days", label: "Last 30 Days" },
                { value: "last_90_days", label: "Last 90 Days" },
            ],
            defaultValue: "all",
        },
    ];

    const emptyState = {
        icon: Funnel,
        title: "Sales Funnel is Empty",
        description: "Your sales funnel hasn't been populated yet. Start by adding leads and tracking their progress through your sales process.",
        buttonText: "+ Add Your First Lead",
    };

    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <MetricsBar metrics={metrics} />
            <ClientsSection
                title="Sales Funnel"
                addButtonText="Add Lead"
                onAdd={() => setIsModalOpen(true)}
                filters={filters}
                emptyState={emptyState}
            />
             <ClientModal
                 isOpen={isModalOpen}
                 onClose={() => setIsModalOpen(false)}
                 mode="add"
                 onSave={(data: CreateClientData | UpdateClientData) => console.log("Adding lead:", data)}
             />
        </div>
    );
}