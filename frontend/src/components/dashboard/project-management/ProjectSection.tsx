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
        removeProject
    } = useProjects();

    return (
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
    );
}
