"use client";

import type { Milestone } from '@/api/types';
import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import Table from '@/components/ui/Table';
import { AlertCircle, CalendarDays, Edit, Layers, Trash2 } from 'lucide-react';
import React, { useCallback, useMemo, useState } from 'react';

interface MilestoneTableProps {
    milestones: Milestone[];
    loading: boolean;
    error: string | null;
    onEditMilestone: (milestone: Milestone) => void;
    onDeleteMilestone: (slug: string) => void;
    onAddMilestone: () => void;
    searchValue: string;
}

const MilestoneTable = React.memo(function MilestoneTable({ milestones, loading, error, onEditMilestone, onDeleteMilestone, onAddMilestone, searchValue }: MilestoneTableProps) {
    const [page, setPage] = useState(1);

    const filteredMilestones = useMemo(() =>
        milestones.filter(milestone =>
            milestone.name.toLowerCase().includes(searchValue.toLowerCase()) ||
            (milestone.description && milestone.description.toLowerCase().includes(searchValue.toLowerCase()))
        ),
        [milestones, searchValue]
    );

    const itemsPerPage = 10;
    const totalPages = useMemo(() =>
        Math.ceil(filteredMilestones.length / itemsPerPage),
        [filteredMilestones.length, itemsPerPage]
    );
    const visibleMilestones = useMemo(() =>
        filteredMilestones.slice((page - 1) * itemsPerPage, page * itemsPerPage),
        [filteredMilestones, page, itemsPerPage]
    );

    const handleEdit = useCallback((milestone: Milestone) => {
        onEditMilestone(milestone);
    }, [onEditMilestone]);

    const handleDelete = useCallback((slug: string) => {
        if (confirm("Are you sure you want to delete this milestone?")) {
            onDeleteMilestone(slug);
        }
    }, [onDeleteMilestone]);

    const headers = ["Milestone", "Schedule", "Status", "Progress", "Actions"];

    const formatDate = (date?: string) => (date ? new Date(date).toLocaleDateString() : '—');

    const getStatusStyles = (status: string) => {
        if (status === 'completed') return 'bg-emerald-100 text-emerald-800';
        if (status === 'active') return 'bg-blue-100 text-blue-800';
        if (status === 'planning') return 'bg-amber-100 text-amber-800';
        return 'bg-slate-100 text-slate-700';
    };

    const rows = visibleMilestones.map((milestone) => ({
        key: milestone.id,
        data: [
            <td key={milestone.id + '-details'} className="px-4 py-4 align-top">
                <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                        <p className="text-sm font-semibold text-slate-900">{milestone.name}</p>
                        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                            {milestone.project_name}
                        </span>
                    </div>
                    <p className="text-xs text-slate-500">
                        {milestone.description || 'Add a description to clarify the milestone scope.'}
                    </p>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                        <span className="inline-flex items-center gap-1">
                            <Layers className="h-3.5 w-3.5" />
                            {milestone.sprints_count} sprint{milestone.sprints_count === 1 ? '' : 's'}
                        </span>
                        <span className="inline-flex items-center gap-1">
                            <CalendarDays className="h-3.5 w-3.5" />
                            Created {formatDate(milestone.created_at)}
                        </span>
                    </div>
                </div>
            </td>,
            <td key={milestone.id + '-schedule'} className="px-4 py-4 align-top">
                <div className="space-y-2 text-xs text-slate-600">
                    <div className="flex items-center justify-between gap-3">
                        <span className="text-slate-400">Planned start</span>
                        <span className="font-semibold text-slate-900">{formatDate(milestone.planned_start)}</span>
                    </div>
                    <div className="flex items-center justify-between gap-3">
                        <span className="text-slate-400">Due date</span>
                        <span className="font-semibold text-slate-900">{formatDate(milestone.due_date)}</span>
                    </div>
                </div>
            </td>,
            <td key={milestone.id + '-status'} className="px-4 py-4 align-top">
                <div className="inline-flex flex-col gap-2">
                    <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${getStatusStyles(milestone.status)}`}>
                        {milestone.status}
                    </span>
                    <span className="text-xs text-slate-500">{milestone.progress}% complete</span>
                </div>
            </td>,
            <td key={milestone.id + '-progress'} className="px-4 py-4 align-top">
                <div className="min-w-[140px]">
                    <div className="mb-2 flex items-center justify-between text-xs text-slate-500">
                        <span>Progress</span>
                        <span className="font-semibold text-slate-900">{milestone.progress}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-slate-100">
                        <div
                            className="h-2 rounded-full bg-emerald-500"
                            style={{ width: `${milestone.progress}%` }}
                        />
                    </div>
                </div>
            </td>,
            <td key={milestone.id + '-actions'} className="px-4 py-4 align-top">
                <div className="flex gap-2">
                    <Button onClick={() => handleEdit(milestone)} variant="outline" size="sm">
                        <Edit className="h-4 w-4" />
                    </Button>
                    <Button onClick={() => handleDelete(milestone.slug)} variant="danger" size="sm">
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </div>
            </td>
        ]
    }));

    if (loading) {
        return <Loader />;
    }

    if (error) {
        return <div className="text-red-500">{error}</div>;
    }

    if (filteredMilestones.length === 0) {
        return (
            <div className="bg-white/90 rounded-2xl border border-slate-200/70 shadow-sm p-10 text-center">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
                    <AlertCircle className="h-6 w-6 text-slate-400" />
                </div>
                <p className="text-lg font-semibold text-slate-900">No milestones yet</p>
                <p className="mt-2 text-sm text-slate-500">Start defining key delivery points to keep the team aligned.</p>
                <Button className="mx-auto mt-5" onClick={onAddMilestone}>
                    Create Your First Milestone
                </Button>
            </div>
        );
    }

    return (
        <div className="bg-white/90 rounded-2xl border border-slate-200/70 shadow-sm overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200/70 px-6 py-4">
                <div>
                    <p className="text-sm font-semibold text-slate-900">Milestone timeline</p>
                    <p className="text-xs text-slate-500">{filteredMilestones.length} milestone{filteredMilestones.length === 1 ? '' : 's'} matched</p>
                </div>
                <p className="text-xs font-medium text-slate-500">Page {page} of {totalPages}</p>
            </div>
            <Table headers={headers} rows={rows} currentPage={page} totalPages={totalPages} onPageChange={setPage} itemsPerPage={itemsPerPage} totalItems={filteredMilestones.length} />
        </div>
    );
});

export default MilestoneTable;
