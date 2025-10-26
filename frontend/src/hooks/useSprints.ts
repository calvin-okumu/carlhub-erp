import { useCallback, useEffect, useState } from "react";
import type { Sprint } from "../api/types";
import {
  createSprint,
  deleteSprint,
  getSprints,
  updateSprint,
} from "../api/project_mgmt";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

export function useSprints(projectSlug: string) {
  const [sprints, setSprints] = useState<Sprint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSprints = useCallback(async () => {
    const token = getToken();
    if (!token) return;

    setLoading(true);
    try {
      const data = await getSprints(token, { projectSlug, ordering: '-created_at' });
      setSprints(data.results);
    } catch (err) {
      console.error(err);
      setError("Failed to load sprints. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [projectSlug]);

  useEffect(() => {
    fetchSprints();
  }, [fetchSprints]);

  const addSprint = async (data: {
    name: string;
    status: string;
    start_date?: string;
    end_date?: string;
    milestone: number;
  }) => {
    const token = getToken();
    if (!token) return;

    // Temporary sprint for optimistic update
    const tempSprint: Sprint = {
      id: Date.now(), // temporary id
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
      const newSprint = await createSprint(token, data);
      console.log("Created sprint:", newSprint);
      setSprints((prev) =>
        prev.map((s) => (s.id === tempSprint.id ? newSprint : s)),
      );
    } catch (err) {
      setSprints((prev) => prev.filter((s) => s.id !== tempSprint.id));
      setError(err instanceof Error ? err.message : "Failed to create sprint.");
    } finally {
      setLoading(false);
    }
  };

  const editSprint = async (
    id: number,
    data: Partial<{
      name: string;
      status: string;
      start_date: string;
      end_date: string;
      milestone: number;
    }>,
  ) => {
    const token = getToken();
    if (!token) return;

    const originalSprint = sprints.find((s) => s.id === id);
    if (!originalSprint) return;

    // Optimistic update
    setSprints((prev) =>
      prev.map((s) => (s.id === id ? { ...s, ...data } : s)),
    );

    setLoading(true);
    try {
      const updatedSprint = await updateSprint(token, id, data);
      setSprints((prev) => prev.map((s) => (s.id === id ? updatedSprint : s)));
    } catch (err) {
      // Revert on error
      setSprints((prev) => prev.map((s) => (s.id === id ? originalSprint : s)));
      setError(err instanceof Error ? err.message : "Failed to update sprint.");
    } finally {
      setLoading(false);
    }
  };

  const removeSprint = async (id: number) => {
    const token = getToken();
    if (!token) return;

    const sprintToRemove = sprints.find((s) => s.id === id);
    if (!sprintToRemove) return;

    setSprints((prev) => prev.filter((s) => s.id !== id));

    setLoading(true);
    try {
      await deleteSprint(token, id);
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

