"use client";

import type { Project } from '@/api/types';
import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import Table from '@/components/ui/Table';
import type { ProjectFormData } from '@/types/project';
import { Edit, Plus, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { useCallback, useMemo, useState } from 'react';
import ProjectModal from '../ProjectModal';

interface ProjectTableProps {
    projects: Project[];
    loading: boolean;
    error: string | null;
    currentPage: number;
    totalPages: number;
    totalItems: number;
    itemsPerPage: number;
    onPageChange: (page: number) => void;
    onAddProject: (data: ProjectFormData) => void;
    onEditProject: (slug: string, data: ProjectFormData) => void;
    onDeleteProject: (slug: string) => void;
}

export default function ProjectTable({
    projects,
    loading,
    error,
    currentPage,
    totalPages,
    totalItems,
    itemsPerPage,
    onPageChange,
    onAddProject,
    onEditProject,
    onDeleteProject
}: ProjectTableProps) {
    const [searchValue, setSearchValue] = useState('');
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedProject, setSelectedProject] = useState<Project | null>(null);

    // For now, we'll do client-side search filtering on the current page's results
    // In a full implementation, search would be sent to the API
    const filteredProjects = useMemo(() =>
        projects.filter(project =>
            project.name.toLowerCase().includes(searchValue.toLowerCase()) ||
            project.client_name.toLowerCase().includes(searchValue.toLowerCase())
        ),
        [projects, searchValue]
    );

    const handleNewProject = useCallback(() => {
        setModalMode('add');
        setSelectedProject(null);
        setModalOpen(true);
    }, []);

    const handleEdit = useCallback((project: Project) => {
        setModalMode('edit');
        setSelectedProject(project);
        setModalOpen(true);
    }, []);

    const handleSaveProject = useCallback(async (data: ProjectFormData) => {
        try {
            if (modalMode === 'add') {
                await onAddProject(data);
            } else if (selectedProject) {
                await onEditProject(selectedProject.slug, data);
            }
            setModalOpen(false);
        } catch (error) {
            console.error('Error saving project:', error);
            // TODO: Show error message
        }
    }, [modalMode, selectedProject, onAddProject, onEditProject]);

    const handleDelete = useCallback((slug: string) => {
        if (confirm("Are you sure you want to delete this project?")) {
            onDeleteProject(slug);
        }
    }, [onDeleteProject]);

    const headers = ["Project", "Status", "Timeline", "Budget", "Progress", "Milestones", "Actions"];

    const statusClasses = (status: string) => (
        status === "active"
            ? "bg-green-100 text-green-800"
            : status === "completed"
                ? "bg-blue-100 text-blue-800"
                : status === "planning"
                    ? "bg-yellow-100 text-yellow-800"
                    : status === "on_hold"
                        ? "bg-orange-100 text-orange-800"
                        : status === "archived"
                            ? "bg-gray-200 text-gray-700"
                            : "bg-gray-100 text-gray-800"
    );

    const priorityClasses = (priority: string) => (
        priority === "high"
            ? "bg-red-100 text-red-800"
            : priority === "medium"
                ? "bg-yellow-100 text-yellow-800"
                : "bg-green-100 text-green-800"
    );

    const rows = filteredProjects.map(p => ({
        key: p.id,
        data: [
            <td key={p.id + '-project'} className="px-4 py-4">
                <div className="flex flex-col gap-1">
                    <Link href={`/dashboard/project-management/${p.slug}`} className="text-sm font-semibold text-blue-600 hover:text-blue-800 hover:underline">
                        {p.name}
                    </Link>
                    <div className="text-xs text-gray-500">Client: {p.client_name}</div>
                    <div className="inline-flex items-center gap-2 text-xs text-gray-500">
                        <span className={`rounded-full px-2 py-0.5 font-medium ${priorityClasses(p.priority)}`}>
                            Priority: {p.priority}
                        </span>
                    </div>
                </div>
            </td>,
            <td key={p.id + '-status'} className="px-4 py-4">
                <div className="flex flex-col gap-2">
                    <span
                        className={`w-fit px-2 py-1 text-xs font-semibold rounded-full ${statusClasses(p.status)}`}
                    >
                        {p.status.replace('_', ' ')}
                    </span>
                </div>
            </td>,
            <td key={p.id + '-timeline'} className="px-4 py-4 text-sm text-gray-700">
                <div className="flex flex-col gap-1">
                    <span>{new Date(p.start_date).toLocaleDateString()}</span>
                    <span className="text-xs text-gray-500">to {new Date(p.end_date).toLocaleDateString()}</span>
                </div>
            </td>,
            <td key={p.id + '-budget'} className="px-4 py-4 text-sm text-gray-900">
                <div className="font-medium">{p.budget ? `$${p.budget}` : "-"}</div>
            </td>,
            <td key={p.id + '-progress'} className="px-4 py-4">
                <div className="flex flex-col gap-2">
                    <div className="text-sm font-medium text-gray-900">{p.progress}%</div>
                    <div className="h-2 w-32 rounded-full bg-gray-200">
                        <div
                            className="h-2 rounded-full bg-blue-500"
                            style={{ width: `${Math.min(100, Math.max(0, p.progress))}%` }}
                        />
                    </div>
                </div>
            </td>,
            <td key={p.id + '-milestones'} className="px-4 py-4 text-sm text-gray-900">
                <div className="font-medium">{p.milestones_count}</div>
                <div className="text-xs text-gray-500">milestones</div>
            </td>,
            <td key={p.id + '-actions'} className="px-4 py-4">
                <div className="flex items-center gap-2">
                    <Button onClick={() => handleEdit(p)} variant="outline" size="sm">
                        <Edit className="h-4 w-4" />
                    </Button>
                    <Button onClick={() => handleDelete(p.slug)} variant="danger" size="sm">
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </div>
            </td>
        ]
    }));

    if (loading) {
        return <Loader />;
    }

    if (error) {
        return <div className="text-red-500">{error}</div>;
    }

    return (
        <>
            <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
                <div className="p-5 border-b border-gray-200 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <div className="text-lg font-semibold text-gray-900">Projects</div>
                        <div className="text-sm text-gray-500">
                            Showing {filteredProjects.length} of {totalItems} projects
                        </div>
                    </div>
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                        <input
                            type="text"
                            placeholder="Search projects by name or client..."
                            value={searchValue}
                            onChange={(e) => setSearchValue(e.target.value)}
                            className="w-full sm:w-64 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <Button onClick={handleNewProject}>
                            <Plus className="h-4 w-4 mr-2" />
                            New Project
                        </Button>
                    </div>
                </div>
                {filteredProjects.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        {searchValue ? `No projects found matching "${searchValue}"` : 'No projects found'}
                    </div>
                ) : (
                    <Table headers={headers} rows={rows} currentPage={currentPage} totalPages={totalPages} onPageChange={onPageChange} itemsPerPage={itemsPerPage} totalItems={totalItems} />
                )}
            </div>
            <ProjectModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                mode={modalMode}
                project={selectedProject || undefined}
                onSave={handleSaveProject}
            />
        </>
    );
}
