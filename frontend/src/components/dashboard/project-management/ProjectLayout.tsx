 import React from 'react';
import type { Project } from '@/api/types';
import ProjectHeader from './project-overview/ProjectHeader';
import ProjectTabs from './project-overview/ProjectTabs';

 interface ProjectLayoutProps {
     project: Project;
     activeTab: string;
     onTabChange: (tab: string) => void;
     children: React.ReactNode;
 }

 export default function ProjectLayout({
     project,
     activeTab,
     onTabChange,
     children
 }: ProjectLayoutProps) {
    return (
        <div className="min-h-screen bg-slate-50">
            <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
                <ProjectHeader project={project} />
                <ProjectTabs activeTab={activeTab} onTabChange={onTabChange} />
                {children}
            </div>
        </div>
    );
}
