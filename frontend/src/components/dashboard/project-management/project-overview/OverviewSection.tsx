import React, { useState, useEffect } from 'react';
import ProjectProgress from './ProjectProgress';
import MetricsGrid from './MetricsGrid';
import ProjectTimeline from './ProjectTimeline';
import ProjectHealth from './ProjectHealth';
import ProjectInformation from './ProjectInformation';
import { getSprints, getTasks, getMilestones } from '@/api/project_mgmt';
import type { Project, Milestone } from '@/api/types';

 interface OverviewSectionProps {
     project: Project;
 }

export default function OverviewSection({ project }: OverviewSectionProps) {
      const [sprintsCount, setSprintsCount] = useState(0);
      const [tasksCount, setTasksCount] = useState(0);
      const [milestones, setMilestones] = useState<Milestone[]>([]);

       useEffect(() => {
           const fetchSprintsCount = async () => {
               const token = localStorage.getItem('access_token');
               if (!token) return;

                 try {
                     const sprints = await getSprints(token, { projectId: project.id });
                     setSprintsCount(sprints.results.length);
                 } catch (err) {
                     console.error('Failed to fetch sprints count:', err);
                 }
            };

            const fetchTasksCount = async () => {
                const token = localStorage.getItem('access_token');
                if (!token) return;

                 try {
                     const tasks = await getTasks(token, { projectId: project.id });
                     setTasksCount(tasks.results.length);
                 } catch (err) {
                     console.error('Failed to fetch tasks count:', err);
                 }
            };

            const fetchMilestones = async () => {
                const token = localStorage.getItem('access_token');
                if (!token) return;

                 try {
                     const milestonesData = await getMilestones(token, { projectId: project.id });
                     setMilestones(milestonesData.results);
                 } catch (err) {
                     console.error('Failed to fetch milestones:', err);
                 }
            };

            fetchSprintsCount();
            fetchTasksCount();
            fetchMilestones();
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
                 sprintsCount={sprintsCount}
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
