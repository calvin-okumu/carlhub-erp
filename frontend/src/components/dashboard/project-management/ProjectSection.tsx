"use client";

import React from 'react';
import ProjectTable from '@/components/dashboard/project-management/table/ProjectTable';
import { useProjects } from '@/hooks/useProjects';

export default function ProjectSection() {
    const {
        projects,
        loading,
        error,
        currentPage,
        totalPages,
        totalItems,
        itemsPerPage,
        onPageChange,
        addProject,
        editProject,
        removeProject,
        summary,
        statusFilter,
        setStatusFilter,
    } = useProjects();

    return (
        <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
                {[
                    { label: 'Total projects', value: summary.total, note: 'Tracked this view', status: '' },
                    { label: 'Active', value: summary.active, note: 'In delivery', status: 'active' },
                    { label: 'Planning', value: summary.planning, note: 'Queued up', status: 'planning' },
                    { label: 'On hold', value: summary.onHold, note: 'Needs attention', status: 'on_hold' },
                    { label: 'Completed', value: summary.completed, note: 'Delivered', status: 'completed' },
                ].map((item) => {
                    const isActive = statusFilter === item.status;
                    return (
                        <button
                            key={item.label}
                            type="button"
                            onClick={() => setStatusFilter(item.status)}
                            className={`rounded-2xl border p-4 text-left shadow-[0_18px_45px_-35px_rgba(15,23,42,0.3)] transition-all ${
                                isActive
                                    ? 'border-slate-900 bg-slate-900 text-white'
                                    : 'border-slate-200/70 bg-white/90 text-slate-900 hover:-translate-y-0.5 hover:border-slate-300'
                            }`}
                        >
                            <p className={`text-xs font-semibold uppercase tracking-[0.28em] ${isActive ? 'text-white/70' : 'text-slate-400'}`}>
                                {item.label}
                            </p>
                            <div className="mt-3 text-2xl font-semibold">{item.value}</div>
                            <p className={`mt-1 text-xs ${isActive ? 'text-white/70' : 'text-slate-500'}`}>{item.note}</p>
                        </button>
                    );
                })}
            </div>
            {statusFilter && (
                <div className="flex items-center justify-between rounded-2xl border border-slate-200/70 bg-white/90 px-4 py-3 text-sm text-slate-600 shadow-sm">
                    <span>
                        Active filter: <span className="font-semibold text-slate-900">{statusFilter.replace('_', ' ')}</span>
                    </span>
                    <button
                        type="button"
                        onClick={() => setStatusFilter('')}
                        className="rounded-full border border-slate-200/70 bg-white px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-slate-500 hover:border-slate-300"
                    >
                        Clear
                    </button>
                </div>
            )}
            <ProjectTable
                projects={projects}
                loading={loading}
                error={error}
                currentPage={currentPage}
                totalPages={totalPages}
                totalItems={totalItems}
                itemsPerPage={itemsPerPage}
                onPageChange={onPageChange}
                onAddProject={addProject}
                onEditProject={editProject}
                onDeleteProject={removeProject}
            />
        </div>
    );
}
