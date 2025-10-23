"use client";

import SprintSection from '@/components/dashboard/project-management/sprint/SprintSection';
import { useProject } from '@/context/ProjectContext';

export default function SprintPage() {
    const { project } = useProject();

    if (!project) return null;

    return <SprintSection projectId={project.id} />;
}