"use client";

import React from 'react';
import { Edit, Download } from 'lucide-react';
import type { Project } from '@/api/types';

interface ProjectHeaderProps {
    project: Project;
    onEdit?: () => void;
    onExport?: () => void;
}

const StatusBadge = ({ status }: { status: string }) => {
    const styles: Record<string, string> = {
        planning: 'bg-amber-100 text-amber-700 border-amber-200',
        active: 'bg-emerald-100 text-emerald-700 border-emerald-200',
        completed: 'bg-blue-100 text-blue-700 border-blue-200',
        on_hold: 'bg-orange-100 text-orange-700 border-orange-200',
        archived: 'bg-slate-200 text-slate-700 border-slate-300'
    };

    return (
        <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${styles[status] || styles.planning}`}>
            {status.charAt(0).toUpperCase() + status.slice(1).replace(/[_-]/g, ' ')}
        </span>
    );
};

const PriorityBadge = ({ priority }: { priority: string }) => {
    const styles: Record<string, string> = {
        low: 'bg-emerald-100 text-emerald-700 border-emerald-200',
        medium: 'bg-amber-100 text-amber-700 border-amber-200',
        high: 'bg-red-100 text-red-700 border-red-200',
        urgent: 'bg-red-100 text-red-700 border-red-200'
    };

    if (!priority) return null;

    return (
        <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${styles[priority] || styles.medium}`}>
            {priority.charAt(0).toUpperCase() + priority.slice(1).replace(/[_-]/g, ' ')}
        </span>
    );
};

const formatDate = (date?: string) => {
    if (!date) return '—';
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};

const getTimelineProgress = (startDate?: string, endDate?: string) => {
    if (!startDate || !endDate) return null;
    const start = new Date(startDate).getTime();
    const end = new Date(endDate).getTime();
    if (Number.isNaN(start) || Number.isNaN(end) || end <= start) return null;
    const now = Date.now();
    const total = end - start;
    const elapsed = Math.min(Math.max(now - start, 0), total);
    return Math.round((elapsed / total) * 100);
};

export default function ProjectHeader({ project, onEdit, onExport }: ProjectHeaderProps) {
    const timelineProgress = getTimelineProgress(project.start_date, project.end_date);

    return (
        <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-6 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                    <div className="flex flex-wrap items-center gap-3">
                        <h1 className="text-3xl font-semibold text-slate-900">{project.name}</h1>
                        <StatusBadge status={project.status} />
                        <PriorityBadge priority={project.priority} />
                    </div>
                    <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-slate-600">
                        <span>Client: <span className="font-medium text-slate-900">{project.client_name}</span></span>
                        <span>Timeline: {formatDate(project.start_date)} → {formatDate(project.end_date)}</span>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={onEdit}
                        className="px-4 py-2 bg-white border border-slate-200/70 rounded-full text-slate-700 text-sm font-semibold hover:border-slate-300 hover:bg-slate-50 transition-colors flex items-center gap-2"
                    >
                        <Edit className="h-4 w-4" />
                        <span>Edit</span>
                    </button>

                    <button
                        onClick={onExport}
                        className="px-4 py-2 bg-slate-900 border border-slate-900 rounded-full text-white text-sm font-semibold hover:bg-slate-800 transition-colors flex items-center gap-2 shadow-sm"
                    >
                        <Download className="h-4 w-4" />
                        <span>Export</span>
                    </button>
                </div>
            </div>

            <div className="mt-6">
                <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>{formatDate(project.start_date)}</span>
                    <span>{formatDate(project.end_date)}</span>
                </div>
                <div className="mt-2 h-2 w-full rounded-full bg-slate-100">
                    <div
                        className="h-2 rounded-full bg-blue-500 transition-all"
                        style={{ width: `${timelineProgress ?? 0}%` }}
                    />
                </div>
                <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                    <span>{timelineProgress === null ? 'Timeline not set' : 'Schedule progress'}</span>
                    <span>{timelineProgress === null ? '—' : `${timelineProgress}% elapsed`}</span>
                </div>
            </div>
        </div>
    );
}
