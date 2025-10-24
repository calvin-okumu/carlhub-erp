"use client";

import React, { useState, useMemo, useCallback } from 'react';
import Link from 'next/link';
import Table from '@/components/ui/Table';
import Loader from '@/components/shared/Loader';
import type { Sprint } from '@/api/types';
import { Edit, Trash2, AlertCircle, Columns } from 'lucide-react';
import Button from '@/components/ui/Button';

interface SprintTableProps {
      sprints: Sprint[];
      loading: boolean;
      error: string | null;
      onEditSprint: (sprint: Sprint) => void;
      onDeleteSprint: (id: number) => void;
      onAddSprint: () => void;
      projectId: number;
      searchValue: string;
      statusFilter: string;
  }

const SprintTable = React.memo(function SprintTable({ sprints, loading, error, onEditSprint, onDeleteSprint, onAddSprint, projectId, searchValue, statusFilter }: SprintTableProps) {
    const [page, setPage] = useState(1);

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

    const handleDelete = useCallback((id: number) => {
        if (confirm("Are you sure you want to delete this sprint?")) {
            onDeleteSprint(id);
        }
    }, [onDeleteSprint]);

    const headers = ["Name", "Status", "Start Date", "End Date", "Milestone", "Tasks", "Progress", "Actions"];

    const rows = visibleSprints.map(sprint => ({
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
            <div key={sprint.id + '-actions'} className="flex gap-2">
                <Link href={`/dashboard/project-management/${projectId}/sprint/${sprint.id}/kanban`}>
                    <Button variant="outline" size="sm">
                        <Columns className="h-4 w-4 mr-2" />
                        Open Kanban
                    </Button>
                </Link>
                <Button onClick={() => handleEdit(sprint)} variant="outline" size="sm">
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                </Button>
                <Button onClick={() => handleDelete(sprint.id)} variant="danger" size="sm">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                </Button>
            </div>
        ]
    }));

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
                <Button onClick={onAddSprint} variant="primary">
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
