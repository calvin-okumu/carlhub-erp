"use client";

import React from 'react';
import { LucideIcon } from 'lucide-react';
import Button from '@/components/ui/Button';
import EmptyState from '@/components/shared/EmptyState';

interface FilterOption {
    value: string;
    label: string;
}

interface Filter {
    options: FilterOption[];
    defaultValue: string;
}

interface EmptyStateData {
    icon: LucideIcon;
    title: string;
    description: string;
    buttonText: string;
}

interface ClientsSectionProps {
    title: string;
    addButtonText: string;
    onAdd: () => void;
    filters: Filter[];
    emptyState: EmptyStateData;
}

export default function ClientsSection({ title, addButtonText, onAdd, filters, emptyState }: ClientsSectionProps) {
    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
                <Button onClick={onAdd} variant="primary">
                    {addButtonText}
                </Button>
            </div>
            <div className="mb-6">
                <div className="flex space-x-4">
                    {filters.map((filter, index) => (
                        <select key={index} className="px-3 py-2 border border-gray-300 rounded-md">
                            {filter.options.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    ))}
                </div>
            </div>
            <EmptyState
                icon={emptyState.icon}
                title={emptyState.title}
                description={emptyState.description}
                buttonText={emptyState.buttonText}
                onButtonClick={onAdd}
            />
        </div>
    );
}