"use client";

import MilestoneSection from '@/components/dashboard/project-management/milestone/MilestoneSection';
import { useProject } from '@/context/ProjectContext';

export default function MilestonePage() {
    const { project } = useProject();

    if (!project) return null;

    return <MilestoneSection projectId={project.id} />;
}
