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
    onClearFilters?: () => void;
}

const BacklogTable = React.memo(function BacklogTable({ tasks, loading, error, onEditTask, onDeleteTask, onAddTask, searchValue, dueSoonOnly = false, onClearFilters }: BacklogTableProps) {
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

    const headers = ["Task", "Status", "Priority", "Progress", "Milestone", "Assignee", "Actions"];

    const formatDueDate = (date?: string) => {
        if (!date) return null;
        const parsed = new Date(date);
        if (Number.isNaN(parsed.getTime())) return null;
        return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(parsed);
    };

    const statusBandStyles: Record<string, string> = {
        done: 'bg-emerald-500',
        in_progress: 'bg-blue-500',
        in_review: 'bg-amber-500',
        testing: 'bg-sky-500',
        to_do: 'bg-slate-400'
    };

    const statusBadgeStyles: Record<string, string> = {
        done: 'bg-emerald-100 text-emerald-700 border-emerald-200',
        in_progress: 'bg-blue-100 text-blue-700 border-blue-200',
        in_review: 'bg-amber-100 text-amber-700 border-amber-200',
        testing: 'bg-sky-100 text-sky-700 border-sky-200',
        to_do: 'bg-slate-100 text-slate-700 border-slate-200'
    };

    const priorityBadgeStyles: Record<string, string> = {
        high: 'bg-rose-100 text-rose-700 border-rose-200',
        medium: 'bg-amber-100 text-amber-700 border-amber-200',
        low: 'bg-emerald-100 text-emerald-700 border-emerald-200'
    };

    const statusLabel = (status: string) => status.replace(/_/g, ' ');
    const priorityLabel = (priority: string) => priority.replace(/_/g, ' ');

    const rows = visibleTasks.map(task => {
        const dueDate = formatDueDate(task.end_date);
        const dueSoon = isDueSoon(task.end_date);

        return {
            key: task.id,
            data: [
                <td key={task.id + '-task'} className="px-4 py-4 align-top">
                    <div className="flex items-start gap-3">
                        <span className={`mt-1 h-10 w-1.5 rounded-full ${statusBandStyles[task.status] || 'bg-slate-400'}`} />
                        <div className="min-w-[220px]">
                            <div className="flex flex-wrap items-center gap-2">
                                <span className="text-sm font-semibold text-slate-900">{task.title}</span>
                                {dueDate && (
                                    <span
                                        className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.2em] ${
                                            dueSoon
                                                ? 'border-amber-200 bg-amber-100 text-amber-700'
                                                : 'border-slate-200 bg-slate-100 text-slate-600'
                                        }`}
                                    >
                                        Due {dueDate}
                                    </span>
                                )}
                            </div>
                            <p className="mt-1 max-w-[320px] text-xs leading-relaxed text-slate-500">
                                {task.description || 'No description yet.'}
                            </p>
                        </div>
                    </div>
                </td>,
                <td key={task.id + '-status'} className="px-4 py-4 align-top">
                    <span
                        className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${
                            statusBadgeStyles[task.status] || statusBadgeStyles.to_do
                        }`}
                    >
                        {statusLabel(task.status)}
                    </span>
                </td>,
                <td key={task.id + '-priority'} className="px-4 py-4 align-top">
                    <span
                        className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${
                            priorityBadgeStyles[task.priority] || priorityBadgeStyles.medium
                        }`}
                    >
                        {priorityLabel(task.priority)}
                    </span>
                </td>,
                <td key={task.id + '-progress'} className="px-4 py-4 align-top">
                    <div className="flex items-center gap-3">
                        <span className="text-sm font-semibold text-slate-900">{task.progress}%</span>
                        <div className="h-2 w-24 rounded-full bg-slate-100">
                            <div
                                className={`h-2 rounded-full transition-all duration-300 ${
                                    task.progress === 100 ? 'bg-emerald-500' : 'bg-blue-500'
                                }`}
                                style={{ width: `${task.progress}%` }}
                            />
                        </div>
                    </div>
                </td>,
                <td key={task.id + '-milestone'} className="px-4 py-4 align-top text-sm text-slate-600">
                    {task.milestone_name || 'Unassigned'}
                </td>,
                <td key={task.id + '-assignee'} className="px-4 py-4 align-top">
                    {task.assignee ? (
                        <div className="flex items-center gap-2 text-xs text-slate-600">
                            <span className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-500">
                                <User className="h-3.5 w-3.5" />
                            </span>
                            Assigned
                        </div>
                    ) : (
                        <span className="text-xs text-slate-400">Unassigned</span>
                    )}
                </td>,
                <td key={task.id + '-actions'} className="px-4 py-4 align-top">
                    <div className="flex gap-2">
                        <Button onClick={() => handleEdit(task)} variant="outline" size="sm">
                            <Edit className="h-4 w-4" />
                        </Button>
                        <Button onClick={() => handleDelete(task.slug)} variant="danger" size="sm">
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    </div>
                </td>
            ]
        };
    });

    if (loading) {
        return <Loader />;
    }

    if (error) {
        return (
            <div className="rounded-2xl border border-red-100 bg-red-50/80 p-6 text-sm text-red-600">
                {error}
            </div>
        );
    }

    if (filteredTasks.length === 0) {
        const hasFilters = searchValue.trim().length > 0 || dueSoonOnly;

        return (
            <div className="bg-white/90 rounded-2xl border border-slate-200/70 shadow-sm p-8 text-center">
                <AlertCircle className="h-8 w-8 text-slate-400 mx-auto mb-3" />
                <p className="text-slate-900 text-base font-semibold">
                    {hasFilters ? 'No tasks match your filters' : 'No backlog tasks yet'}
                </p>
                <p className="mt-1 text-sm text-slate-500">
                    {hasFilters
                        ? 'Try adjusting your search or filters to find tasks faster.'
                        : 'Start by creating a task and keep the backlog ready for planning.'}
                </p>
                <div className="mt-5 flex flex-wrap justify-center gap-3">
                    {hasFilters && onClearFilters && (
                        <Button variant="outline" onClick={onClearFilters}>
                            Clear filters
                        </Button>
                    )}
                    <Button onClick={onAddTask}>
                        Create Task
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white/90 rounded-2xl border border-slate-200/70 shadow-sm overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200/70 px-6 py-4">
                <div>
                    <p className="text-sm font-semibold text-slate-900">Backlog pipeline</p>
                    <p className="text-xs text-slate-500">
                        {filteredTasks.length} task{filteredTasks.length === 1 ? '' : 's'} matched
                    </p>
                </div>
                <p className="text-xs font-medium text-slate-500">Page {page} of {totalPages}</p>
            </div>
            <Table headers={headers} rows={rows} currentPage={page} totalPages={totalPages} onPageChange={setPage} itemsPerPage={itemsPerPage} totalItems={filteredTasks.length} />
        </div>
    );
});

export default BacklogTable;
