import { useCallback, useEffect, useState } from "react";
import type { Sprint } from "../api/types";
import { STORAGE_KEYS } from "../constants/storage";
import {
  createSprint,
  deleteSprint,
  getSprints,
  getTasks,
  updateSprint,
} from "../api/project_mgmt";

function getToken(): string | null {
  return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
}

export function useSprints(projectId: number) {
  const [sprints, setSprints] = useState<Sprint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSprints = useCallback(async () => {
    const token = getToken();
    if (!token || !projectId) return;

    setLoading(true);
    try {
      const data = await getSprints(token, { projectId, ordering: '-created_at' });

      let sprintsArray: Sprint[] = [];
      if (data && typeof data === 'object' && 'results' in data) {
        sprintsArray = (data as { results: Sprint[] }).results ?? [];
      } else {
        sprintsArray = (data as Sprint[]) ?? [];
      }

      // Calculate progress for each sprint based on tasks (inheriting backend averaging pattern)
      const sprintsWithProgress = await Promise.all(
        sprintsArray.map(async (sprint) => {
          try {
            const tasksData = await getTasks(token, { projectId, sprintSlug: sprint.slug });

            let tasksArray: Task[] = [];
            if (tasksData && typeof tasksData === 'object' && 'results' in tasksData) {
              tasksArray = (tasksData as { results: Task[] }).results ?? [];
            } else {
              tasksArray = (tasksData as Task[]) ?? [];
            }

            const calculatedProgress = tasksArray.length > 0
              ? Math.round(tasksArray.reduce((sum, task) => sum + task.progress, 0) / tasksArray.length)
              : 0;
            return { ...sprint, progress: calculatedProgress, tasks_count: tasksArray.length };
          } catch (err) {
            console.error(`Failed to fetch tasks for sprint ${sprint.slug}:`, err);
            return sprint; // Return sprint with original progress if task fetch fails
          }
        })
      );

      setSprints(sprintsWithProgress);
    } catch (err) {
      console.error(err);
      setError("Failed to load sprints. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchSprints();
  }, [fetchSprints]);

  const addSprint = async (data: {
    name: string;
    status: string;
    start_date?: string;
    end_date?: string;
    milestone: string;
  }) => {
    const token = getToken();
    if (!token || !projectId) {
      console.error('No token or projectId for addSprint');
      return;
    }

    // Temporary sprint for optimistic update
    const tempSprint: Sprint = {
      id: Date.now().toString(), // temporary id
      slug: `temp-${Date.now()}`, // temporary slug
      name: data.name,
      status: data.status,
      start_date: data.start_date,
      end_date: data.end_date,
      milestone: data.milestone,
      milestone_name: "", // will be set later
      tasks_count: 0,
      progress: 0,
      created_at: new Date().toISOString(),
    };

    setSprints((prev) => [...prev, tempSprint]);

    setLoading(true);
    try {
      const newSprint = await createSprint(token, projectId, data);
      console.log("Created sprint:", newSprint);
      // Calculate progress for the new sprint (should be 0 since no tasks yet)
      const tasksData = await getTasks(token, { projectId, sprintSlug: newSprint.slug });

      let tasksArray: Task[] = [];
      if (tasksData && typeof tasksData === 'object' && 'results' in tasksData) {
        tasksArray = (tasksData as { results: Task[] }).results ?? [];
      } else {
        tasksArray = (tasksData as Task[]) ?? [];
      }

      const calculatedProgress = tasksArray.length > 0
        ? Math.round(tasksArray.reduce((sum, task) => sum + task.progress, 0) / tasksArray.length)
        : 0;
      const sprintWithProgress = { ...newSprint, progress: calculatedProgress, tasks_count: tasksArray.length };
      setSprints((prev) =>
        prev.map((s) => (s.id === tempSprint.id ? sprintWithProgress : s)),
      );
    } catch (err) {
      setSprints((prev) => prev.filter((s) => s.id !== tempSprint.id));
      setError(err instanceof Error ? err.message : "Failed to create sprint.");
    } finally {
      setLoading(false);
    }
  };

  const editSprint = async (
    slug: string,
    data: Partial<{
      name: string;
      status: string;
      start_date: string;
      end_date: string;
      milestone: string;
    }>,
  ) => {
    const token = getToken();
    if (!token) return;

    const originalSprint = sprints.find((s) => s.slug === slug);
    if (!originalSprint) return;

    // Optimistic update
    setSprints((prev) =>
      prev.map((s) => (s.slug === slug ? { ...s, ...data } : s)),
    );

    setLoading(true);
    try {
      const updatedSprint = await updateSprint(token, slug, data);
      // Recalculate progress for the updated sprint
      const tasksData = await getTasks(token, { projectId, sprintSlug: slug });

      let tasksArray: Task[] = [];
      if (tasksData && typeof tasksData === 'object' && 'results' in tasksData) {
        tasksArray = (tasksData as { results: Task[] }).results ?? [];
      } else {
        tasksArray = (tasksData as Task[]) ?? [];
      }

      const calculatedProgress = tasksArray.length > 0
        ? Math.round(tasksArray.reduce((sum, task) => sum + task.progress, 0) / tasksArray.length)
        : 0;
      const sprintWithProgress = { ...updatedSprint, progress: calculatedProgress, tasks_count: tasksArray.length };
      setSprints((prev) => prev.map((s) => (s.slug === slug ? sprintWithProgress : s)));
    } catch (err) {
      // Revert on error
      setSprints((prev) => prev.map((s) => (s.slug === slug ? originalSprint : s)));
      setError(err instanceof Error ? err.message : "Failed to update sprint.");
    } finally {
      setLoading(false);
    }
  };

  const removeSprint = async (slug: string) => {
    const token = getToken();
    if (!token) return;

    const sprintToRemove = sprints.find((s) => s.slug === slug);
    if (!sprintToRemove) return;

    setSprints((prev) => prev.filter((s) => s.slug !== slug));

    setLoading(true);
    try {
      await deleteSprint(token, slug);
    } catch (err) {
      setSprints((prev) => [...prev, sprintToRemove]);
      setError(err instanceof Error ? err.message : "Failed to delete sprint.");
    } finally {
      setLoading(false);
    }
  };

  return {
    sprints,
    loading,
    error,
    addSprint,
    editSprint,
    removeSprint,
    refetch: fetchSprints,
    setError,
  };
}

