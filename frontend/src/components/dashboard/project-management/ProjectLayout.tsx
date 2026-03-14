import React from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
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
                <div className="sticky top-0 z-30 -mx-4 bg-slate-50/95 px-4 pb-3 pt-6 backdrop-blur sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
                    <div className="space-y-3">
                        <div className="flex flex-wrap items-center gap-3 text-sm">
                            <Link
                                href="/dashboard/project-management"
                                className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 font-semibold text-slate-700 shadow-sm transition-colors hover:border-slate-300 hover:text-slate-900"
                            >
                                <ArrowLeft className="h-4 w-4" />
                                <span>Back to Projects</span>
                            </Link>
                            <span className="text-slate-300">/</span>
                            <span className="font-semibold text-slate-500">Project</span>
                            <span className="text-slate-300">/</span>
                            <span className="font-semibold text-slate-900">{project.name}</span>
                        </div>
                        <ProjectTabs activeTab={activeTab} onTabChange={onTabChange} />
                    </div>
                </div>
                <ProjectHeader project={project} />
                {children}
            </div>
        </div>
    );
}
