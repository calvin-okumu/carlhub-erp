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
        active: 'bg-emerald-100 text-emerald-700 border-emerald-200',
        pending: 'bg-amber-100 text-amber-700 border-amber-200',
        completed: 'bg-blue-100 text-blue-700 border-blue-200',
        'on-hold': 'bg-gray-100 text-gray-700 border-gray-200'
    };

    return (
        <span className={`px-3 py-1 rounded-md text-xs font-medium border ${styles[status] || styles.pending}`}>
            {status.charAt(0).toUpperCase() + status.slice(1).replace('-', ' ')}
        </span>
    );
};

export default function ProjectHeader({ project, onEdit, onExport }: ProjectHeaderProps) {
    return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm mb-6 p-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
                    <StatusBadge status={project.status} />
                    <span className="text-sm text-gray-600">Client: {project.client_name}</span>
                </div>

                <div className="flex items-center space-x-2">
                    <button
                        onClick={onEdit}
                        className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 text-sm font-medium hover:bg-gray-50 hover:border-gray-400 transition-colors flex items-center space-x-2"
                    >
                        <Edit className="h-4 w-4" />
                        <span>Edit</span>
                    </button>

                    <button
                        onClick={onExport}
                        className="px-4 py-2 bg-blue-600 border border-blue-600 rounded-lg text-white text-sm font-medium hover:bg-blue-700 transition-colors flex items-center space-x-2 shadow-sm"
                    >
                        <Download className="h-4 w-4" />
                        <span>Export</span>
                    </button>
                </div>
            </div>
        </div>
    );
}


