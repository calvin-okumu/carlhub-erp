import { useCallback, useEffect, useState } from "react";
import type { Task } from "../api/types";
import {
  createTask,
  deleteTask,
  getTasks,
  updateTask,
} from "../api/project_mgmt";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

export function useTasks(projectSlug: string, backlog: boolean = false) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    const token = getToken();
    if (!token) return;

    setLoading(true);
    try {
      const data = await getTasks(token, { projectSlug, backlog, ordering: '-created_at' });
      setTasks(data.results);
    } catch (err) {
      console.error(err);
      setError("Failed to load tasks. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [backlog, projectSlug]);

    useEffect(() => {
        fetchTasks();
    }, [fetchTasks]);

  const addTask = async (data: {
     title: string;
     description?: string;
     status: string;
     milestone: string;
     sprint?: string;
     assignee?: number;
     start_date?: string;
     end_date?: string;
     estimated_hours?: number;
   }) => {
     const taskData = { ...data, project: projectSlug };
    const token = getToken();
    if (!token) return;

    // Temporary task for optimistic update
    const tempTask: Task = {
      id: Date.now().toString(), // temporary id
      slug: `temp-${Date.now()}`, // temporary slug
      title: data.title,
      description: data.description || "",
      status: data.status,
      priority: "medium", // default
      milestone: data.milestone,
      milestone_name: "", // will be set later
      sprint: data.sprint,
      sprint_name: data.sprint ? "" : undefined,
      assignee: data.assignee,
      start_date: data.start_date,
      end_date: data.end_date,
      estimated_hours: data.estimated_hours,
      progress: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

     setTasks((prev) => [...prev, tempTask]);

     setLoading(true);
      try {
        const newTask = await createTask(token, projectSlug, taskData);
       console.log("Created task:", newTask);
      setTasks((prev) => prev.map((t) => (t.id === tempTask.id ? newTask : t)));
    } catch (err) {
      setTasks((prev) => prev.filter((t) => t.id !== tempTask.id));
      setError(err instanceof Error ? err.message : "Failed to create task.");
    } finally {
      setLoading(false);
    }
  };

  const editTask = async (
    slug: string,
    data: Partial<{
      title: string;
      description: string;
      status: string;
      milestone: string;
      sprint: string;
      assignee: number;
      start_date: string;
      end_date: string;
      estimated_hours: number;
    }>,
  ) => {
    const token = getToken();
    if (!token) return;

    const originalTask = tasks.find((t) => t.slug === slug);
    if (!originalTask) return;

    // Optimistic update
    setTasks((prev) => prev.map((t) => (t.slug === slug ? { ...t, ...data } : t)));

    setLoading(true);
    try {
      const updatedTask = await updateTask(token, slug, data);
      setTasks((prev) => prev.map((t) => (t.slug === slug ? updatedTask : t)));
    } catch (err) {
      // Revert on error
      setTasks((prev) => prev.map((t) => (t.slug === slug ? originalTask : t)));
      setError(err instanceof Error ? err.message : "Failed to update task.");
    } finally {
      setLoading(false);
    }
  };

   const removeTask = async (slug: string) => {
      const token = getToken();
      if (!token) return;

      const taskToRemove = tasks.find((t) => t.slug === slug);
      if (!taskToRemove) return;

      setTasks((prev) => prev.filter((t) => t.slug !== slug));

     // Since backend is read-only, don't call API, just keep the optimistic update
     // setLoading(true);
     // try {
      //   await deleteTask(token, slug);
     // } catch (err) {
     //   setTasks((prev) => [...prev, taskToRemove]);
     //   setError(err instanceof Error ? err.message : "Failed to delete task.");
     // } finally {
     //   setLoading(false);
     // }
   };

  return {
    tasks,
    loading,
    error,
    addTask,
    editTask,
    removeTask,
    refetch: fetchTasks,
    setError,
  };
}
