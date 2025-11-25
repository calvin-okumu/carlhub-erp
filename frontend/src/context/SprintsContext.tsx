"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getAccessToken } from '@/utils/auth';
import { getSprints, getTasks } from '@/api/project_mgmt';
import { useProject } from './ProjectContext';
import type { Sprint } from '@/api/types';

interface SprintsContextType {
  sprints: Sprint[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
  addSprintOptimistically: (sprint: Sprint) => void;
  updateSprintOptimistically: (slug: string, updatedSprint: Partial<Sprint>) => void;
  removeSprintOptimistically: (slug: string) => void;
}

const SprintsContext = createContext<SprintsContextType | undefined>(undefined);

export function SprintsProvider({ children }: { children: React.ReactNode }) {
  const { project } = useProject();
  const [sprints, setSprints] = useState<Sprint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSprints = useCallback(async () => {
    const token = getAccessToken();
    if (!token || !project?.id) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getSprints(token, { projectId: project.id, ordering: '-created_at' });

      let sprints: Sprint[] = [];
      if (data && typeof data === 'object' && 'results' in data) {
        sprints = (data as { results: Sprint[] }).results ?? [];
      } else {
        sprints = (data as Sprint[]) ?? [];
      }

      // Calculate progress for each sprint based on tasks
      const sprintsWithProgress = await Promise.all(
        sprints.map(async (sprint) => {
          try {
            const tasksData = await getTasks(token, { projectId: project.id, sprintSlug: sprint.slug });

            let tasks: Task[] = [];
            if (tasksData && typeof tasksData === 'object' && 'results' in tasksData) {
              tasks = (tasksData as { results: Task[] }).results ?? [];
            } else {
              tasks = (tasksData as Task[]) ?? [];
            }

            const calculatedProgress = tasks.length > 0
              ? Math.round(tasks.reduce((sum, task) => sum + task.progress, 0) / tasks.length)
              : 0;
            return { ...sprint, progress: calculatedProgress, tasks_count: tasks.length };
          } catch (err) {
            console.error(`Failed to fetch tasks for sprint ${sprint.slug}:`, err);
            return sprint; // Return sprint with original progress if task fetch fails
          }
        })

      );

      setSprints(sprintsWithProgress);
    } catch (err) {
      console.error('Failed to load sprints:', err);
      setError(err instanceof Error ? err.message : 'Failed to load sprints');
    } finally {
      setLoading(false);
    }
  }, [project?.id]);

  useEffect(() => {
    fetchSprints();
  }, [fetchSprints]);

  const addSprintOptimistically = (newSprint: Sprint) => {
    setSprints(prev => [newSprint, ...prev]);
  };

  const updateSprintOptimistically = (slug: string, updatedSprint: Partial<Sprint>) => {
    setSprints(prev => prev.map(s => s.slug === slug ? { ...s, ...updatedSprint } : s));
  };

  const removeSprintOptimistically = (slug: string) => {
    setSprints(prev => prev.filter(s => s.slug !== slug));
  };

  return (
    <SprintsContext.Provider value={{
      sprints,
      loading,
      error,
      refetch: fetchSprints,
      addSprintOptimistically,
      updateSprintOptimistically,
      removeSprintOptimistically
    }}>
      {children}
    </SprintsContext.Provider>
  );
}

export function useSprintsContext() {
  const context = useContext(SprintsContext);
  if (context === undefined) {
    throw new Error('useSprintsContext must be used within a SprintsProvider');
  }
  return context;
}