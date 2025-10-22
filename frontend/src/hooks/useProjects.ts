import { useCallback, useEffect, useState } from "react";
import { Project } from "../api/types";
import {
    getProjects,
    createProject,
    updateProject,
    deleteProject,
} from "../api/project_mgmt";
import { getUserTenants } from "../api/crm";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

export function useProjects() {
  const [projects, setProjects] = useState<Project[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async () => {
    const token = getToken();
    if (!token) return;

    setLoading(true);
    try {
      const tenants = await getUserTenants(token);
      const ownerTenant = Array.isArray(tenants) ? tenants.find((t) => t.is_owner) || tenants[0] : tenants;

      const data = await getProjects(token, { tenant: ownerTenant?.tenant, ordering: '-created_at' });
      setProjects(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load projects. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const addProject = async (data: {
    name: string;
    client: number;
    status: string;
    priority: string;
    start_date: string;
    end_date: string;
    budget?: string;
    tags?: string;
    team_members?: number[];
    access_groups?: number[];
  }) => {
    const token = getToken();
    if (!token) return;

    setLoading(true);
    try {
      const newProject = await createProject(token, data);
      setProjects(prev => [...prev, newProject]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project.");
    } finally {
      setLoading(false);
    }
  };

  const editProject = async (id: number, data: Partial<{
    name: string;
    client: number;
    status: string;
    priority: string;
    start_date: string;
    end_date: string;
    budget?: string;
    tags?: string;
    team_members?: number[];
    access_groups?: number[];
  }>) => {
    const token = getToken();
    if (!token) return;

    const originalProject = projects.find(p => p.id === id);
    if (!originalProject) return;

    // Optimistic update
    setProjects(prev => prev.map(p => p.id === id ? { ...p, ...data } : p));

    setLoading(true);
    try {
      const updatedProject = await updateProject(token, id, data);
      setProjects(prev => prev.map(p => p.id === id ? updatedProject : p));
    } catch (err) {
      // Revert on error
      setProjects(prev => prev.map(p => p.id === id ? originalProject : p));
      setError(err instanceof Error ? err.message : "Failed to update project.");
    } finally {
      setLoading(false);
    }
  };

  const removeProject = async (id: number) => {
    const token = getToken();
    if (!token) return;

    const projectToRemove = projects.find(p => p.id === id);
    if (!projectToRemove) return;

    setProjects((prev) => prev.filter((p) => p.id !== id));

    setLoading(true);
    try {
      await deleteProject(token, id);
    } catch (err) {
      setProjects((prev) => [...prev, projectToRemove]);
      setError(err instanceof Error ? err.message : "Failed to delete project.");
    } finally {
      setLoading(false);
    }
  };

  return {
    projects,
    loading,
    error,
    addProject,
    editProject,
    removeProject,
    refetch: fetchProjects,
    setError,
  };
}