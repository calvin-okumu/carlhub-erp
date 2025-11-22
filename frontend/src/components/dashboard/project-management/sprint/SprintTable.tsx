"use client";

import type { Sprint } from '@/api/types';
import KanbanSection from '@/components/dashboard/project-management/sprint/kanban/KanbanSection';
import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import Table from '@/components/ui/Table';
import { AlertCircle, Columns, Edit, Trash2 } from 'lucide-react';
import React, { useCallback, useMemo, useState } from 'react';

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

const SprintTable = React.memo(function SprintTable({ sprints, loading, error, onEditSprint, onDeleteSprint, onAddSprint, searchValue, statusFilter, _projectSlug }: SprintTableProps) {
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

    const headers = ["Name", "Status", "Start Date", "End Date", "Milestone", "Tasks", "Progress", "Actions"];

    const rows: { key: string; data: (string | number | React.ReactNode)[] }[] = [];

    visibleSprints.forEach(sprint => {
        rows.push({
            key: sprint.id,
            data: [
                sprint.name,
                <span
                    key={sprint.id + '-status'}
                    className={`px-2 py-1 text-xs font-semibold rounded-full ${sprint.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : sprint.status === 'active'
                            ? 'bg-blue-100 text-blue-800'
                            : sprint.status === 'planned'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-gray-100 text-gray-800'
                        }`}
                >
                    {sprint.status}
                </span>,
                sprint.start_date ? new Date(sprint.start_date).toLocaleDateString() : "-",
                sprint.end_date ? new Date(sprint.end_date).toLocaleDateString() : "-",
                sprint.milestone_name || "-",
                sprint.tasks_count,
                `${sprint.progress}%`,
                <div key={sprint.slug + '-actions'} className="flex gap-2">
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
            ]
        });

        if (expandedSprintId === sprint.id) {
            rows.push({
                key: sprint.id + '-kanban',
                data: [
                    <td key={sprint.id + '-kanban-td'} colSpan={headers.length} className="p-4 bg-gray-50 border-t">
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
        return (
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 mb-4">No sprints found</p>
                <Button onClick={onAddSprint} className='mx-auto'>
                    Create Your First Sprint
                </Button>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
            <Table headers={headers} rows={rows} currentPage={page} totalPages={totalPages} onPageChange={setPage} itemsPerPage={itemsPerPage} totalItems={filteredSprints.length} />
        </div>
    );
});

export default SprintTable;
