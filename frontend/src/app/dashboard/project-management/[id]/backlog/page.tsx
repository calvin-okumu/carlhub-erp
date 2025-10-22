"use client";

import BacklogSection from '@/components/dashboard/project-management/backlog/Backlogsection';
import { useProject } from '@/context/ProjectContext';

export default function BacklogPage() {
    const { project } = useProject();

    if (!project) return null;

    return <BacklogSection projectId={project.id} />;
}