"use client";

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import KanbanSection from '@/components/dashboard/project-management/sprint/kanban/KanbanSection';

const KanbanPage = () => {
    const router = useRouter();
    const params = useParams();
    const sprintSlug = params.sprintSlug as string;

    if (!sprintSlug) {
        return (
            <div className="min-h-screen bg-gray-50 p-6">
                <div className="max-w-7xl mx-auto text-center">
                    <h1 className="text-2xl font-bold text-gray-900 mb-4">Invalid Parameters</h1>
                    <p className="text-gray-600">Sprint slug is invalid.</p>
                </div>
            </div>
        );
    }

    return <KanbanSection sprintSlug={sprintSlug} onBack={() => router.back()} />;
};

export default KanbanPage;
