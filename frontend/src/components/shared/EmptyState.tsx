"use client";

import React from 'react';
import { LucideIcon } from 'lucide-react';
import Button from '@/components/ui/Button';

interface EmptyStateProps {
    icon: LucideIcon;
    title: string;
    description: string;
    buttonText: string;
    onButtonClick: () => void;
}

export default function EmptyState({ icon: Icon, title, description, buttonText, onButtonClick }: EmptyStateProps) {
    return (
        <div className="text-center py-12">
            <Icon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">{title}</h3>
            <p className="mt-1 text-sm text-gray-500">{description}</p>
            <div className="mt-6">
                <Button onClick={onButtonClick} variant="primary">
                    {buttonText}
                </Button>
            </div>
        </div>
    );
}