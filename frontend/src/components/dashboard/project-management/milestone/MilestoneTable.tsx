"use client";

import React, { useState, useMemo, useCallback } from 'react';
import Table from '@/components/ui/Table';
import Pagination from '@/components/shared/Pagination';
import Loader from '@/components/shared/Loader';
import type { Milestone } from '@/api/types';
import { Edit, Trash2, AlertCircle } from 'lucide-react';
import Button from '@/components/ui/Button';

interface MilestoneTableProps {
    milestones: Milestone[];
    loading: boolean;
    error: string | null;
    onEditMilestone: (milestone: Milestone) => void;
    onDeleteMilestone: (id: number) => void;
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

    const handleDelete = useCallback((id: number) => {
        if (confirm("Are you sure you want to delete this milestone?")) {
            onDeleteMilestone(id);
        }
    }, [onDeleteMilestone]);

    const headers = ["Name", "Description", "Status", "Due Date", "Progress", "Actions"];

    const rows = visibleMilestones.map((milestone) => ({
        key: milestone.id,
        data: [
            milestone.name,
            milestone.description || "-",
            <span
                key={milestone.id + '-status'}
                className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    milestone.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : milestone.status === 'in_progress'
                        ? 'bg-blue-100 text-blue-800'
                        : milestone.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                }`}
            >
                {milestone.status.replace('_', ' ')}
            </span>,
            milestone.due_date ? new Date(milestone.due_date).toLocaleDateString() : "-",
            `${milestone.progress}%`,
            <div key={milestone.id + '-actions'} className="flex gap-2">
                <Button onClick={() => handleEdit(milestone)} variant="outline" size="sm">
                    <Edit className="h-4 w-4" />
                </Button>
                <Button onClick={() => handleDelete(milestone.id)} variant="danger" size="sm">
                    <Trash2 className="h-4 w-4" />
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

    if (filteredMilestones.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 mb-4">No milestones found</p>
                <Button onClick={onAddMilestone} variant="primary">
                    Create Your First Milestone
                </Button>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
            <Table headers={headers} rows={rows} />
            <Pagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={setPage}
                itemsPerPage={itemsPerPage}
                totalItems={filteredMilestones.length}
            />
        </div>
    );
});

export default MilestoneTable;