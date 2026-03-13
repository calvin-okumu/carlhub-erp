"use client";

import type { Sprint } from '@/api/types';
import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import Table from '@/components/ui/Table';
import { AlertCircle, Columns, Edit, Trash2 } from 'lucide-react';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import KanbanSection from '@/components/dashboard/project-management/sprint/kanban/KanbanSection';

interface SprintTableProps {
    sprints: Sprint[];
    loading: boolean;
    error: string | null;
    onEditSprint: (sprint: Sprint) => void;
    onDeleteSprint: (slug: string) => void;
    onAddSprint: () => void;
    projectSlug: string;
    searchValue: string;
    statusFilter: string;
}

const SprintTable = React.memo(function SprintTable({ sprints, loading, error, onEditSprint, onDeleteSprint, onAddSprint, projectSlug, searchValue, statusFilter }: SprintTableProps) {
    const [page, setPage] = useState(1);
    const [expandedSprintId, setExpandedSprintId] = useState<string | null>(null);

    const filteredSprints = useMemo(() =>
        sprints.filter(sprint =>
            sprint.name.toLowerCase().includes(searchValue.toLowerCase()) &&
            (statusFilter === 'all' || sprint.status === statusFilter)
        ),
        [sprints, searchValue, statusFilter]
    );

    const itemsPerPage = 10;
    const totalPages = useMemo(() =>
        Math.ceil(filteredSprints.length / itemsPerPage),
        [filteredSprints.length, itemsPerPage]
    );
    const visibleSprints = useMemo(() =>
        filteredSprints.slice((page - 1) * itemsPerPage, page * itemsPerPage),
        [filteredSprints, page, itemsPerPage]
    );

    const handleEdit = useCallback((sprint: Sprint) => {
        onEditSprint(sprint);
    }, [onEditSprint]);

    const handleDelete = useCallback((slug: string) => {
        if (confirm("Are you sure you want to delete this sprint?")) {
            onDeleteSprint(slug);
        }
    }, [onDeleteSprint]);

    useEffect(() => {
        setPage(1);
    }, [searchValue, statusFilter]);

    const headers = ["Sprint", "Status", "Dates", "Milestone", "Tasks", "Progress", "Actions"];

    const rows: { key: string; data: (string | number | React.ReactNode)[] }[] = [];

    visibleSprints.forEach(sprint => {
        const progressValue = Math.min(100, Math.max(0, sprint.progress ?? 0));
        const statusClasses = sprint.status === 'completed'
            ? 'bg-emerald-100 text-emerald-800'
            : sprint.status === 'active'
                ? 'bg-blue-100 text-blue-800'
                : sprint.status === 'planned'
                    ? 'bg-amber-100 text-amber-800'
                    : 'bg-slate-100 text-slate-700';
        rows.push({
            key: sprint.id,
            data: [
                <td className="px-4 py-4">
                    <div className="space-y-1">
                        <div className="text-sm font-semibold text-slate-900">{sprint.name}</div>
                        <div className="text-xs text-slate-500">Slug {sprint.slug}</div>
                    </div>
                </td>,
                <td className="px-4 py-4">
                    <span
                        key={sprint.id + '-status'}
                        className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold capitalize ${statusClasses}`}
                    >
                        <span className="h-2 w-2 rounded-full bg-current" />
                        {sprint.status}
                    </span>
                </td>,
                <td className="px-4 py-4">
                    <div className="space-y-1 text-xs text-slate-500">
                        <div>
                            <span className="font-semibold text-slate-700">Start</span>{' '}
                            {sprint.start_date ? new Date(sprint.start_date).toLocaleDateString() : "-"}
                        </div>
                        <div>
                            <span className="font-semibold text-slate-700">End</span>{' '}
                            {sprint.end_date ? new Date(sprint.end_date).toLocaleDateString() : "-"}
                        </div>
                    </div>
                </td>,
                <td className="px-4 py-4">
                    <div className="text-sm text-slate-700">{sprint.milestone_name || "-"}</div>
                </td>,
                <td className="px-4 py-4">
                    <div className="text-sm font-semibold text-slate-900">{sprint.tasks_count ?? 0}</div>
                    <div className="text-xs text-slate-500">Tasks</div>
                </td>,
                <td className="px-4 py-4">
                    <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs text-slate-500">
                            <span>{progressValue}%</span>
                            <span>{progressValue >= 100 ? 'Done' : 'In progress'}</span>
                        </div>
                        <div className="h-2 rounded-full bg-slate-100">
                            <div
                                className="h-2 rounded-full bg-slate-900"
                                style={{ width: `${progressValue}%` }}
                            />
                        </div>
                    </div>
                </td>,
                <td className="px-4 py-4">
                    <div key={sprint.slug + '-actions'} className="flex flex-wrap gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setExpandedSprintId(expandedSprintId === sprint.id ? null : sprint.id)}
                        >
                            <Columns className="h-4 w-4 mr-2" />
                            Open Kanban
                        </Button>
                        <Button onClick={() => handleEdit(sprint)} variant="outline" size="sm">
                            <Edit className="h-4 w-4 mr-2" />
                            Edit
                        </Button>
                        <Button onClick={() => handleDelete(sprint.slug)} variant="danger" size="sm">
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                        </Button>
                    </div>
                </td>
            ]
        });

        if (expandedSprintId === sprint.id) {
            rows.push({
                key: sprint.id + '-kanban',
                data: [
                    <td key={sprint.id + '-kanban-td'} colSpan={headers.length} className="p-4 bg-slate-50/70 border-t border-slate-100">
                        <KanbanSection sprintSlug={sprint.slug} onBack={() => setExpandedSprintId(null)} />
                    </td>
                ]
            });
        }
    });

    if (loading) {
        return <Loader />;
    }

    if (error) {
        return <div className="text-red-500">{error}</div>;
    }

    if (filteredSprints.length === 0) {
        const hasFilters = searchValue.trim().length > 0 || statusFilter !== 'all';
        return (
            <div className="bg-white/90 rounded-2xl border border-slate-200/70 shadow-sm p-8 text-center">
                <AlertCircle className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                <p className="text-slate-600 font-semibold mb-1">
                    {hasFilters ? 'No sprints match your filters' : 'No sprints found'}
                </p>
                <p className="text-sm text-slate-500 mb-4">
                    {hasFilters ? 'Try a different keyword or status filter.' : 'Create a sprint to start tracking delivery.'}
                </p>
                <Button onClick={onAddSprint} className="mx-auto">
                    Create Your First Sprint
                </Button>
            </div>
        );
    }

    return (
        <div className="bg-white/90 rounded-2xl border border-slate-200/70 shadow-sm overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200/70 px-6 py-4">
                <div>
                    <p className="text-sm font-semibold text-slate-900">Sprint roster</p>
                    <p className="text-xs text-slate-500">
                        {filteredSprints.length} sprint{filteredSprints.length === 1 ? '' : 's'} matched
                    </p>
                </div>
                <p className="text-xs font-medium text-slate-500">Page {page} of {totalPages}</p>
            </div>
            <Table headers={headers} rows={rows} currentPage={page} totalPages={totalPages} onPageChange={setPage} itemsPerPage={itemsPerPage} totalItems={filteredSprints.length} />
        </div>
    );
});

export default SprintTable;
