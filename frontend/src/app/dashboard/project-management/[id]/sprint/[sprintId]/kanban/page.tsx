"use client";

import React from 'react';
import { useParams } from 'next/navigation';
import KanbanSection from '@/components/dashboard/project-management/sprint/kanban/KanbanSection';

const KanbanPage = () => {
    const params = useParams();
    const projectId = parseInt(params.id as string);
    const sprintId = parseInt(params.sprintId as string);

    if (isNaN(projectId) || isNaN(sprintId)) {
        return (
            <div className="min-h-screen bg-gray-50 p-6">
                <div className="max-w-7xl mx-auto text-center">
                    <h1 className="text-2xl font-bold text-gray-900 mb-4">Invalid Parameters</h1>
                    <p className="text-gray-600">Project ID or Sprint ID is invalid.</p>
                </div>
            </div>
        );
    }

    return <KanbanSection projectId={projectId} sprintId={sprintId} />;
};

export default KanbanPage;
