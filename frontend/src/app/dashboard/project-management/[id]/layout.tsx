 "use client";

 import { useState } from 'react';
 import { usePathname } from 'next/navigation';
 import { ProjectProvider } from '@/context/ProjectContext';
 import ProjectLayout from '@/components/dashboard/project-management/ProjectLayout';
 import { useProject } from '@/context/ProjectContext';
 import Loader from '@/components/shared/Loader';
import OverviewSection from '@/components/dashboard/project-management/project-overview/OverviewSection';
import MilestoneSection from '@/components/dashboard/project-management/milestone/MilestoneSection';
import BacklogSection from '@/components/dashboard/project-management/backlog/Backlogsection';
import SprintSection from '@/components/dashboard/project-management/sprint/SprintSection';
import CompletedTasksSection from '@/components/dashboard/project-management/completed-tasks/CompletedTasksSection';

 function ProjectLayoutWrapper({ children }: { children: React.ReactNode }) {
     const { project, loading, error } = useProject();
     const [activeTab, setActiveTab] = useState('overview');
     const pathname = usePathname();

     // Skip project loading for kanban pages
     if (pathname.includes('/kanban')) {
         return <>{children}</>;
     }

     if (loading) return <Loader />;
     if (error) return <div>{error}</div>;
     if (!project) return <div>Project not found</div>;

     const renderContent = () => {
         switch (activeTab) {
              case 'overview':
                  return <OverviewSection project={project} />;
             case 'milestones':
                 return <MilestoneSection projectId={project.id} />;
             case 'backlog':
                 return <BacklogSection projectId={project.id} />;
             case 'sprints':
                 return <SprintSection projectId={project.id} />;
             case 'documents':
                 return <div className="p-6 text-center text-gray-500">Documents section coming soon.</div>;
              case 'completed-tasks':
                  return <CompletedTasksSection projectId={project.id} />;
              default:
                  return <OverviewSection project={project} />;
         }
     };

     return (
         <ProjectLayout
             project={project}
             activeTab={activeTab}
             onTabChange={setActiveTab}
         >
             {renderContent()}
         </ProjectLayout>
     );
 }

  export default function Layout({ children }: { children: React.ReactNode }) {
      return (
          <ProjectProvider activeTab="" onTabChange={() => {}}>
              <ProjectLayoutWrapper>{children}</ProjectLayoutWrapper>
          </ProjectProvider>
      );
  }