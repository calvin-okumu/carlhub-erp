"use client";

import React, { useState, useMemo, useCallback } from 'react';
import Table from '@/components/ui/Table';
import Loader from '@/components/shared/Loader';
import type { Task } from '@/api/types';
import { Edit, Trash2, AlertCircle, User } from 'lucide-react';
import Button from '@/components/ui/Button';

interface BacklogTableProps {
    tasks: Task[];
    loading: boolean;
    error: string | null;
    onEditTask: (task: Task) => void;
    onDeleteTask: (slug: string) => void;
    onAddTask: () => void;
    searchValue: string;
    dueSoonOnly?: boolean;
}

const BacklogTable = React.memo(function BacklogTable({ tasks, loading, error, onEditTask, onDeleteTask, onAddTask, searchValue, dueSoonOnly = false }: BacklogTableProps) {
    const [page, setPage] = useState(1);

    const isDueSoon = useCallback((date?: string) => {
        if (!date) return false;
        const normalized = date.slice(0, 10);
        const target = new Date(normalized);
        if (Number.isNaN(target.getTime())) return false;
        const today = new Date();
        const startOfToday = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        const diffDays = Math.ceil((target.getTime() - startOfToday.getTime()) / (1000 * 60 * 60 * 24));
        return diffDays >= 0 && diffDays <= 7;
    }, []);

    const filteredTasks = useMemo(() => {
        const base = dueSoonOnly
            ? tasks.filter((task) => isDueSoon(task.end_date))
            : tasks;
        return base.filter(task =>
            task.title.toLowerCase().includes(searchValue.toLowerCase()) ||
            (task.description && task.description.toLowerCase().includes(searchValue.toLowerCase()))
        );
    }, [tasks, searchValue, dueSoonOnly, isDueSoon]);

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

    const handleDelete = useCallback((slug: string) => {
        if (confirm("Are you sure you want to delete this task?")) {
            onDeleteTask(slug);
        }
    }, [onDeleteTask]);

    const headers = ["Title", "Description", "Status", "Priority", "Progress", "Milestone", "Assignee", "Actions"];

    const formatDueDate = (date?: string) => {
        if (!date) return null;
        const parsed = new Date(date);
        if (Number.isNaN(parsed.getTime())) return null;
        return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(parsed);
    };

    const statusBandStyles: Record<string, string> = {
        done: 'bg-emerald-500',
        in_progress: 'bg-pink-500',
        in_review: 'bg-blue-500',
        testing: 'bg-green-500',
        to_do: 'bg-gray-400'
    };

    const rows = visibleTasks.map(task => {
        const dueDate = formatDueDate(task.end_date);

        return {
        key: task.id,
        data: [
            <div key={task.id + '-title'} className="flex items-center gap-3">
                <span className={`h-10 w-1 rounded-full ${statusBandStyles[task.status] || 'bg-gray-400'}`} />
                <div className="flex flex-col">
                    <span className="font-medium text-gray-900">{task.title}</span>
                    {dueDate && (
                        <span className="mt-1 inline-flex w-fit items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-semibold text-gray-600">
                            Due {dueDate}
                        </span>
                    )}
                </div>
            </div>,
            task.description || "-",
            <span
                key={task.id + '-status'}
                className={`px-2 py-1 text-xs font-semibold rounded-full ${task.status === 'done'
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
                className={`px-2 py-1 text-xs font-semibold rounded-full ${task.priority === 'high'
                        ? 'bg-red-100 text-red-800'
                        : task.priority === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                    }`}
            >
                {task.priority}
            </span>,
            <div key={task.id + '-progress'} className="flex items-center gap-2">
                <span className="text-sm font-medium">{task.progress}%</span>
                <div className="w-12 h-1 bg-gray-200 rounded">
                    <div
                        className={`h-1 rounded transition-all duration-300 ${task.progress === 100 ? 'bg-green-500' : 'bg-blue-500'
                            }`}
                        style={{ width: `${task.progress}%` }}
                    />
                </div>
            </div>,
            task.milestone_name || "-",
            task.assignee ? (
                <div className="flex items-center gap-2">
                    <span className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-100 text-slate-600">
                        <User className="h-3.5 w-3.5" />
                    </span>
                    <span className="text-xs text-slate-600">Assigned</span>
                </div>
            ) : "-",
            <div key={task.id + '-actions'} className="flex gap-2">
                <Button onClick={() => handleEdit(task)} variant="outline" size="sm">
                    <Edit className="h-4 w-4" />
                </Button>
                <Button onClick={() => handleDelete(task.slug)} variant="danger" size="sm">
                    <Trash2 className="h-4 w-4" />
                </Button>
            </div>
        ]
        };
    });

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
                <Button className='mx-auto' onClick={onAddTask}>
                    Create Your First Task
                </Button>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
            <Table headers={headers} rows={rows} currentPage={page} totalPages={totalPages} onPageChange={setPage} itemsPerPage={itemsPerPage} totalItems={filteredTasks.length} />
        </div>
    );
});

export default BacklogTable;
