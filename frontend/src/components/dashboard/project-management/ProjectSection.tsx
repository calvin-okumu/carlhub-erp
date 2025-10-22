"use client";

import React from 'react';
import ProjectTable from '@/components/dashboard/project-management/table/ProjectTable';
import { useProjects } from '@/hooks/useProjects';

export default function ProjectSection() {
    const { projects, loading, error, addProject, editProject, removeProject } = useProjects();

    return (
        <ProjectTable
            projects={projects}
            loading={loading}
            error={error}
            onAddProject={addProject}
            onEditProject={editProject}
            onDeleteProject={removeProject}
        />
    );
}
