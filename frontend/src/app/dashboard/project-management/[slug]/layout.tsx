 "use client";

import { useState } from 'react';
 import { ProjectProvider } from '@/context/ProjectContext';
 import { SprintsProvider } from '@/context/SprintsContext';
 import { MilestonesProvider } from '@/context/MilestonesContext';
 import ProjectLayout from '@/components/dashboard/project-management/ProjectLayout';
 import { useProject } from '@/context/ProjectContext';
 import Loader from '@/components/shared/Loader';
import OverviewSection from '@/components/dashboard/project-management/project-overview/OverviewSection';
import MilestoneSection from '@/components/dashboard/project-management/milestone/MilestoneSection';
import BacklogSection from '@/components/dashboard/project-management/backlog/Backlogsection';
import SprintSection from '@/components/dashboard/project-management/sprint/SprintSection';
import CompletedTasksSection from '@/components/dashboard/project-management/completed-tasks/CompletedTasksSection';

 function ProjectLayoutWrapper({ }: { children: React.ReactNode }) {
     const { project, loading, error } = useProject();
     const [activeTab, setActiveTab] = useState('overview');




     if (loading) return <Loader />;
     if (error) return <div>{error}</div>;
     if (!project) return <div>Project not found</div>;

     const renderContent = () => {
         switch (activeTab) {
              case 'overview':
                  return <OverviewSection project={project} />;
              case 'milestones':
                  return <MilestoneSection projectSlug={project.slug} />;
                case 'backlog':
                    return <BacklogSection projectSlug={project.slug} />;
              case 'sprints':
                  return <SprintSection projectSlug={project.slug} />;
              case 'documents':
                  return <div className="p-6 text-center text-gray-500">Documents section coming soon.</div>;
                  case 'completed-tasks':
                      return <CompletedTasksSection />;
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
               <SprintsProvider>
                   <MilestonesProvider>
                       <ProjectLayoutWrapper>{children}</ProjectLayoutWrapper>
                   </MilestonesProvider>
               </SprintsProvider>
           </ProjectProvider>
       );
   }