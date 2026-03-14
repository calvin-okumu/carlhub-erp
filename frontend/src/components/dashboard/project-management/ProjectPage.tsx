"use client";

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import ProjectLayout from '@/components/dashboard/project-management/ProjectLayout';
import { useProject } from '@/context/ProjectContext';
import Loader from '@/components/shared/Loader';
import OverviewSection from '@/components/dashboard/project-management/project-overview/OverviewSection';
import MilestoneSection from '@/components/dashboard/project-management/milestone/MilestoneSection';
import BacklogSection from '@/components/dashboard/project-management/backlog/Backlogsection';
import SprintSection from '@/components/dashboard/project-management/sprint/SprintSection';
import CompletedTasksSection from '@/components/dashboard/project-management/completed-tasks/CompletedTasksSection';

export default function ProjectPage() {
  const { project, loading, error } = useProject();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  if (loading) return <Loader />;
  if (error) return <div>{error}</div>;
  if (!project) return <div>Project not found</div>;

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewSection project={project} />;
      case 'milestones':
        return <MilestoneSection />;
      case 'backlog':
        return <BacklogSection />;
      case 'sprints':
        return <SprintSection />;
      case 'documents':
        return (
          <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-10 text-center text-slate-500 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Project Documents</p>
            <h2 className="mt-3 text-xl font-semibold text-slate-900">Documents Hub</h2>
            <p className="mt-2 text-sm text-slate-500">Store briefs, contracts, and deliverables here.</p>
            <div className="mt-6 inline-flex items-center gap-2 rounded-full border border-slate-200/70 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Coming soon
            </div>
          </div>
        );
      case 'completed-tasks':
        return <CompletedTasksSection />;
      default:
        return <OverviewSection project={project} />;
    }
  };

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    if (project?.slug) {
      router.push(`/dashboard/project-management/${project.slug}?tab=${tab}`);
    }
  };

  return (
    <ProjectLayout project={project} activeTab={activeTab} onTabChange={handleTabChange}>
      {renderContent()}
    </ProjectLayout>
  );
}
