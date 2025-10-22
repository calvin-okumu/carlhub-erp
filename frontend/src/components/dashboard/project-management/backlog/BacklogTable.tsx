"use client";

import React, { useState, useMemo, useCallback } from 'react';
import Table from '@/components/ui/Table';
import Pagination from '@/components/shared/Pagination';
import Loader from '@/components/shared/Loader';
import type { Task } from '@/api/types';
import { Edit, Trash2, AlertCircle } from 'lucide-react';
import Button from '@/components/ui/Button';

interface BacklogTableProps {
    tasks: Task[];
    loading: boolean;
    error: string | null;
    onEditTask: (task: Task) => void;
    onDeleteTask: (id: number) => void;
    onAddTask: () => void;
    searchValue: string;
}

const BacklogTable = React.memo(function BacklogTable({ tasks, loading, error, onEditTask, onDeleteTask, onAddTask, searchValue }: BacklogTableProps) {
    const [page, setPage] = useState(1);

    const filteredTasks = useMemo(() =>
        tasks.filter(task =>
            task.title.toLowerCase().includes(searchValue.toLowerCase()) ||
            (task.description && task.description.toLowerCase().includes(searchValue.toLowerCase()))
        ),
        [tasks, searchValue]
    );

    const itemsPerPage = 10;
    const totalPages = useMemo(() =>
        Math.ceil(filteredTasks.length / itemsPerPage),
        [filteredTasks.length, itemsPerPage]
    );
    const visibleTasks = useMemo(() =>
        filteredTasks.slice((page - 1) * itemsPerPage, page * itemsPerPage),
        [filteredTasks, page, itemsPerPage]
    );

    const handleEdit = useCallback((task: Task) => {
        onEditTask(task);
    }, [onEditTask]);

    const handleDelete = useCallback((id: number) => {
        if (confirm("Are you sure you want to delete this task?")) {
            onDeleteTask(id);
        }
    }, [onDeleteTask]);

    const headers = ["Title", "Description", "Status", "Priority", "Milestone", "Assignee", "Actions"];

    const rows = visibleTasks.map(task => ({
        key: task.id,
        data: [
        task.title,
        task.description || "-",
        <span
            key={task.id + '-status'}
            className={`px-2 py-1 text-xs font-semibold rounded-full ${
                task.status === 'done'
                    ? 'bg-green-100 text-green-800'
                    : task.status === 'in_progress'
                    ? 'bg-blue-100 text-blue-800'
                    : task.status === 'in_review'
                    ? 'bg-yellow-100 text-yellow-800'
                    : task.status === 'testing'
                    ? 'bg-purple-100 text-purple-800'
                    : 'bg-gray-100 text-gray-800'
            }`}
        >
            {task.status.replace('_', ' ')}
        </span>,
        <span
            key={task.id + '-priority'}
            className={`px-2 py-1 text-xs font-semibold rounded-full ${
                task.priority === 'high'
                    ? 'bg-red-100 text-red-800'
                    : task.priority === 'medium'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-green-100 text-green-800'
            }`}
        >
            {task.priority}
        </span>,
        task.milestone_name || "-",
        task.assignee ? "Assigned" : "-", // Placeholder
        <div key={task.id + '-actions'} className="flex gap-2">
            <Button onClick={() => handleEdit(task)} variant="outline" size="sm">
                <Edit className="h-4 w-4" />
            </Button>
            <Button onClick={() => handleDelete(task.id)} variant="danger" size="sm">
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

    if (filteredTasks.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 mb-4">No tasks in backlog</p>
                <Button onClick={onAddTask} variant="primary">
                    Create Your First Task
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
                totalItems={filteredTasks.length}
            />
        </div>
    );
});

export default BacklogTable;