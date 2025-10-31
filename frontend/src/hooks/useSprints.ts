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
    milestone: string;
  }) => {
    const token = getToken();
    if (!token) return;

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
      const newSprint = await createSprint(token, projectSlug, data);
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
      setSprints((prev) => prev.map((s) => (s.slug === slug ? updatedSprint : s)));
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

