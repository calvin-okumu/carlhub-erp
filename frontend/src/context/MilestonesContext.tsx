"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getAccessToken } from '@/utils/auth';
import { getMilestones } from '@/api/project_mgmt';
import { useProject } from './ProjectContext';
import type { Milestone } from '@/api/types';

interface MilestonesContextType {
  milestones: Milestone[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
  addMilestoneOptimistically: (milestone: Milestone) => void;
  updateMilestoneOptimistically: (slug: string, updatedMilestone: Partial<Milestone>) => void;
  removeMilestoneOptimistically: (slug: string) => void;
}

const MilestonesContext = createContext<MilestonesContextType | undefined>(undefined);

export function MilestonesProvider({ children }: { children: React.ReactNode }) {
  const { project } = useProject();
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMilestones = useCallback(async () => {
    const token = getAccessToken();
    if (!token || !project?.id) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getMilestones(token, { projectId: project.id, ordering: '-created_at' });

      let milestones: Milestone[] = [];
      if (data && typeof data === 'object' && 'results' in data) {
        milestones = (data as { results: Milestone[] }).results ?? [];
      } else {
        milestones = (data as Milestone[]) ?? [];
      }

      setMilestones(milestones);
    } catch (err) {
      console.error('Failed to load milestones:', err);
      setError(err instanceof Error ? err.message : 'Failed to load milestones');
    } finally {
      setLoading(false);
    }
  }, [project?.id]);

  useEffect(() => {
    fetchMilestones();
  }, [fetchMilestones]);

  const addMilestoneOptimistically = (newMilestone: Milestone) => {
    setMilestones(prev => [newMilestone, ...prev]);
  };

  const updateMilestoneOptimistically = (slug: string, updatedMilestone: Partial<Milestone>) => {
    setMilestones(prev => prev.map(m => m.slug === slug ? { ...m, ...updatedMilestone } : m));
  };

  const removeMilestoneOptimistically = (slug: string) => {
    setMilestones(prev => prev.filter(m => m.slug !== slug));
  };

  return (
    <MilestonesContext.Provider value={{
      milestones,
      loading,
      error,
      refetch: fetchMilestones,
      addMilestoneOptimistically,
      updateMilestoneOptimistically,
      removeMilestoneOptimistically
    }}>
      {children}
    </MilestonesContext.Provider>
  );
}

export function useMilestonesContext() {
  const context = useContext(MilestonesContext);
  if (context === undefined) {
    throw new Error('useMilestonesContext must be used within a MilestonesProvider');
  }
  return context;
}