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
            <div className="min-h-screen bg-slate-50 p-6">
                <div className="max-w-screen-2xl mx-auto text-center rounded-2xl border border-slate-200/70 bg-white/90 p-10 shadow-sm">
                    <h1 className="text-2xl font-semibold text-slate-900 mb-4">Invalid Parameters</h1>
                    <p className="text-slate-600">Sprint slug is invalid.</p>
                </div>
            </div>
        );
    }

    return <KanbanSection sprintSlug={sprintSlug} onBack={() => router.back()} />;
};

export default KanbanPage;
