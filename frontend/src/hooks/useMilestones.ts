import { useCallback, useEffect, useState } from "react";
import type { Milestone } from "../api/types";
import {
  createMilestone,
  deleteMilestone,
  getMilestones,
  updateMilestone,
} from "../api/project_mgmt";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

export function useMilestones(projectId: number, tenant?: number) {
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMilestones = useCallback(async () => {
    const token = getToken();
    if (!token) return;

    setLoading(true);
    try {
      const data = await getMilestones(token, { projectId, tenant, ordering: '-created_at' });
      setMilestones(data.results);
    } catch (err) {
      console.error(err);
      setError("Failed to load milestones. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [projectId, tenant]);

  useEffect(() => {
    fetchMilestones();
  }, [fetchMilestones]);

  const addMilestone = async (data: {
    name: string;
    description?: string;
    status: string;
    planned_start?: string;
    actual_start?: string;
    due_date?: string;
    assignee?: number;
    project: number;
    tenant: number;
  }) => {
    const token = getToken();
    if (!token) return;

    // Temporary milestone for optimistic update
    const tempMilestone: Milestone = {
      id: Date.now(), // temporary id
      name: data.name,
      description: data.description || "",
      status: data.status,
      planned_start: data.planned_start,
      actual_start: data.actual_start,
      due_date: data.due_date,
      assignee: data.assignee,
      progress: 0,
      project: data.project,
      project_name: "", // will be set later
      sprints_count: 0,
      created_at: new Date().toISOString(),
    };

    setMilestones((prev) => [...prev, tempMilestone]);

    setLoading(true);
    try {
      const newMilestone = await createMilestone(token, {
        ...data,
        progress: 0,
      });
      console.log("Created milestone:", newMilestone);
      setMilestones((prev) =>
        prev.map((m) => (m.id === tempMilestone.id ? newMilestone : m)),
      );
    } catch (err) {
      setMilestones((prev) => prev.filter((m) => m.id !== tempMilestone.id));
      setError(
        err instanceof Error ? err.message : "Failed to create milestone.",
      );
    } finally {
      setLoading(false);
    }
  };

  const editMilestone = async (
    id: number,
    data: Partial<{
      name: string;
      description: string;
      status: string;
      planned_start: string;
      actual_start: string;
      due_date: string;
      assignee: number;
      project: number;
    }>,
  ) => {
    const token = getToken();
    if (!token) return;

    const originalMilestone = milestones.find((m) => m.id === id);
    if (!originalMilestone) return;

    // Optimistic update
    setMilestones((prev) =>
      prev.map((m) => (m.id === id ? { ...m, ...data } : m)),
    );

    setLoading(true);
    try {
      const updatedMilestone = await updateMilestone(token, id, data);
      setMilestones((prev) =>
        prev.map((m) => (m.id === id ? updatedMilestone : m)),
      );
    } catch (err) {
      // Revert on error
      setMilestones((prev) =>
        prev.map((m) => (m.id === id ? originalMilestone : m)),
      );
      setError(
        err instanceof Error ? err.message : "Failed to update milestone.",
      );
    } finally {
      setLoading(false);
    }
  };

  const removeMilestone = async (id: number) => {
    const token = getToken();
    if (!token) return;

    const milestoneToRemove = milestones.find((m) => m.id === id);
    if (!milestoneToRemove) return;

    setMilestones((prev) => prev.filter((m) => m.id !== id));

    setLoading(true);
    try {
      await deleteMilestone(token, id);
    } catch (err) {
      setMilestones((prev) => [...prev, milestoneToRemove]);
      setError(
        err instanceof Error ? err.message : "Failed to delete milestone.",
      );
    } finally {
      setLoading(false);
    }
  };

  return {
    milestones,
    loading,
    error,
    addMilestone,
    editMilestone,
    removeMilestone,
    refetch: fetchMilestones,
    setError,
  };
}

