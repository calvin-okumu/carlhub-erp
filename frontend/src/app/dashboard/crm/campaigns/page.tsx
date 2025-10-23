"use client";

import React, { useState } from 'react';
import { Mail, TrendingUp, DollarSign, Calendar } from 'lucide-react';
import MetricsBar from '@/components/dashboard/crm/components/MetricsBar';
import ClientsSection from '@/components/dashboard/crm/components/ClientsSection';
import ClientModal from '@/components/dashboard/crm/clients/ClientModal';
import type { CreateClientData, UpdateClientData } from '@/api/types';

export default function CampaignsPage() {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const metrics = [
        {
            title: "Total Campaigns",
            value: 0,
            label: "All campaigns created",
            icon: Mail,
            color: "border-purple-200",
        },
        {
            title: "Active Campaigns",
            value: 0,
            label: "Currently running",
            icon: TrendingUp,
            color: "border-green-200",
        },
        {
            title: "Budget Spent",
            value: 0,
            label: "Total expenditure",
            icon: DollarSign,
            color: "border-blue-200",
        },
        {
            title: "Campaign ROI",
            value: 0,
            label: "Return on investment",
            icon: Calendar,
            color: "border-orange-200",
        },
    ];

    const filters = [
        {
            options: [
                { value: "all", label: "All Campaigns" },
                { value: "active", label: "Active Only" },
                { value: "completed", label: "Completed" },
                { value: "draft", label: "Draft" },
            ],
            defaultValue: "all",
        },
        {
            options: [
                { value: "all", label: "All Types" },
                { value: "email", label: "Email Marketing" },
                { value: "social", label: "Social Media" },
                { value: "paid", label: "Paid Advertising" },
                { value: "content", label: "Content Marketing" },
            ],
            defaultValue: "all",
        },
        {
            options: [
                { value: "all", label: "All Time" },
                { value: "this_month", label: "This Month" },
                { value: "last_month", label: "Last Month" },
                { value: "this_quarter", label: "This Quarter" },
            ],
            defaultValue: "all",
        },
    ];

    const emptyState = {
        icon: Mail,
        title: "No Marketing Campaigns Found",
        description: "You haven't created any marketing campaigns yet. Start building your marketing strategy by creating your first campaign.",
        buttonText: "+ Create Your First Campaign",
    };

    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <MetricsBar metrics={metrics} />
            <ClientsSection
                title="Marketing Campaigns"
                addButtonText="Create Campaign"
                onAdd={() => setIsModalOpen(true)}
                filters={filters}
                emptyState={emptyState}
            />
             <ClientModal
                 isOpen={isModalOpen}
                 onClose={() => setIsModalOpen(false)}
                 mode="add"
                 onSave={(data: CreateClientData | UpdateClientData) => console.log("Creating campaign:", data)}
             />
        </div>
    );
}