import React, { useState, useEffect } from 'react';
import ProjectProgress from './ProjectProgress';
import MetricsGrid from './MetricsGrid';
import ProjectTimeline from './ProjectTimeline';
import ProjectHealth from './ProjectHealth';
import ProjectInformation from './ProjectInformation';
import { getTasks } from '@/api/project_mgmt';
import { useSprintsContext } from '@/context/SprintsContext';
import { useMilestonesContext } from '@/context/MilestonesContext';
import { getAccessToken } from '@/utils/auth';
import type { Project } from '@/api/types';

 interface OverviewSectionProps {
     project: Project;
 }

export default function OverviewSection({ project }: OverviewSectionProps) {
       const { sprints } = useSprintsContext();
       const { milestones } = useMilestonesContext();
       const [tasksCount, setTasksCount] = useState(0);

        useEffect(() => {
             const fetchTasksCount = async () => {
                 const token = getAccessToken();
                 if (!token) return;

                  try {
                      const tasks = await getTasks(token, { projectId: project.id });
                      setTasksCount(tasks.results.length);
                  } catch (err) {
                      console.error('Failed to fetch tasks count:', err);
                  }
             };

             fetchTasksCount();
        }, [project.id]);

       // Calculate project progress as average of milestone progress
       const calculateProjectProgress = () => {
           if (milestones.length === 0) return 0;
           const totalProgress = milestones.reduce((sum, milestone) => sum + milestone.progress, 0);
           return Math.round(totalProgress / milestones.length);
       };

    return (
        <div className="space-y-6">
              <MetricsGrid
                  milestonesCount={project.milestones_count}
                  tasksCount={tasksCount}
                  sprintsCount={sprints.length}
                  teamMembersCount={project.team_members.length}
              />
            <ProjectProgress progress={calculateProjectProgress()} />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ProjectTimeline milestonesCount={project.milestones_count} />
                <ProjectInformation project={project} />
            </div>
            <ProjectHealth project={project} />
        </div>
    );
}
