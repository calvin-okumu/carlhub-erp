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
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [itemsPerPage] = useState(10);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [summary, setSummary] = useState({
    total: 0,
    active: 0,
    planning: 0,
    onHold: 0,
    completed: 0,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async (page = 1) => {
    const token = getToken();
    if (!token) return;

    setLoading(true);
    try {
      const tenants = await getUserTenants(token);
      const ownerTenant = Array.isArray(tenants) ? tenants.find((t) => t.is_owner) || tenants[0] : tenants;

      const data = await getProjects(token, {
        tenant: ownerTenant?.tenant,
        ordering: '-created_at',
        ...(statusFilter ? { status: statusFilter } : {}),
        page,
        limit: itemsPerPage
      });

      // Handle paginated response
      setProjects(data.results);
      setTotalItems(data.count);
      setTotalPages(Math.ceil(data.count / itemsPerPage));
      setCurrentPage(page);

      const [activeCount, planningCount, onHoldCount, completedCount] = await Promise.all([
        getProjects(token, { tenant: ownerTenant?.tenant, status: 'active', page: 1, limit: 1 }),
        getProjects(token, { tenant: ownerTenant?.tenant, status: 'planning', page: 1, limit: 1 }),
        getProjects(token, { tenant: ownerTenant?.tenant, status: 'on_hold', page: 1, limit: 1 }),
        getProjects(token, { tenant: ownerTenant?.tenant, status: 'completed', page: 1, limit: 1 }),
      ]);

      setSummary({
        total: data.count,
        active: activeCount.count,
        planning: planningCount.count,
        onHold: onHoldCount.count,
        completed: completedCount.count,
      });
    } catch (err) {
      console.error(err);
      setError("Failed to load projects. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [itemsPerPage, statusFilter]);

  useEffect(() => {
    fetchProjects(1);
  }, [fetchProjects, statusFilter]);

  const handlePageChange = useCallback((page: number) => {
    fetchProjects(page);
  }, [fetchProjects]);

  const addProject = async (data: {
    name: string;
    client: string;
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

  const editProject = async (slug: string, data: Partial<{
    name: string;
    client: string;
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

    const originalProject = projects.find(p => p.slug === slug);
    if (!originalProject) return;

    // Optimistic update
    setProjects(prev => prev.map(p => p.slug === slug ? { ...p, ...data } : p));

    setLoading(true);
    try {
      const updatedProject = await updateProject(token, slug, data);
      setProjects(prev => prev.map(p => p.slug === slug ? updatedProject : p));
    } catch (err) {
      // Revert on error
      setProjects(prev => prev.map(p => p.slug === slug ? originalProject : p));
      setError(err instanceof Error ? err.message : "Failed to update project.");
    } finally {
      setLoading(false);
    }
  };

  const removeProject = async (slug: string) => {
    const token = getToken();
    if (!token) return;

    const projectToRemove = projects.find(p => p.slug === slug);
    if (!projectToRemove) return;

    setProjects((prev) => prev.filter((p) => p.slug !== slug));

    setLoading(true);
    try {
      await deleteProject(token, slug);
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
    currentPage,
    totalPages,
    totalItems,
    itemsPerPage,
    summary,
    statusFilter,
    setStatusFilter,
    onPageChange: handlePageChange,
    addProject,
    editProject,
    removeProject,
    refetch: fetchProjects,
    setError,
  };
}
