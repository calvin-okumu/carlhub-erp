import React, { useState, useEffect } from 'react';
import ProjectProgress from './ProjectProgress';
import MetricsGrid from './MetricsGrid';
import ProjectHealth from './ProjectHealth';
import ProjectInformation from './ProjectInformation';
import DueSoonTray from './DueSoonTray';
import DeliveryRisk from './DeliveryRisk';
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
                      const sprints = await getSprints(token, { projectSlug: project.slug });
                     setSprintsCount(sprints.results.length);
                 } catch (err) {
                     console.error('Failed to fetch sprints count:', err);
                 }
            };

            const fetchTasksCount = async () => {
                const token = localStorage.getItem('access_token');
                if (!token) return;

                 try {
                      const tasks = await getTasks(token, { projectSlug: project.slug });
                     setTasksCount(tasks.results.length);
                 } catch (err) {
                     console.error('Failed to fetch tasks count:', err);
                 }
            };

            const fetchMilestones = async () => {
                const token = localStorage.getItem('access_token');
                if (!token) return;

                 try {
                      const milestonesData = await getMilestones(token, { projectSlug: project.slug });
                     setMilestones(milestonesData.results);
                 } catch (err) {
                     console.error('Failed to fetch milestones:', err);
                 }
            };

            fetchSprintsCount();
            fetchTasksCount();
            fetchMilestones();
        }, [project.slug]);

    // Calculate project progress as average of milestone progress
    const calculateProjectProgress = () => {
        if (milestones.length === 0) return 0;
        const totalProgress = milestones.reduce((sum, milestone) => sum + milestone.progress, 0);
        return Math.round(totalProgress / milestones.length);
    };

    const getTimelineProgress = (startDate?: string, endDate?: string) => {
        if (!startDate || !endDate) return null;
        const start = new Date(startDate).getTime();
        const end = new Date(endDate).getTime();
        if (Number.isNaN(start) || Number.isNaN(end) || end <= start) return null;
        const now = Date.now();
        const total = end - start;
        const elapsed = Math.min(Math.max(now - start, 0), total);
        return Math.round((elapsed / total) * 100);
    };

    const overallProgress = project.progress ?? calculateProjectProgress();
    const milestoneAverage = calculateProjectProgress();
    const timelineProgress = getTimelineProgress(project.start_date, project.end_date);

    return (
        <div className="space-y-4">
            <MetricsGrid
                milestonesCount={project.milestones_count}
                tasksCount={tasksCount}
                sprintsCount={sprintsCount}
                teamMembersCount={project.team_members.length}
            />

            <ProjectProgress
                overall={overallProgress}
                milestoneAverage={milestoneAverage}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                <ProjectInformation project={project} />
                <ProjectHealth project={project} />
                <DeliveryRisk
                    project={project}
                    timelineProgress={timelineProgress}
                    milestonesCount={project.milestones_count}
                    tasksCount={tasksCount}
                    sprintsCount={sprintsCount}
                />
                <DueSoonTray milestones={milestones} />
            </div>
        </div>
    );
}
