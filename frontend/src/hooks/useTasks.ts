import { useCallback, useState } from "react";
import { getAccessToken } from "../utils/auth";
import type { Task } from "../api/types";
import {
  createTask,
  getTasks,
  updateTask,
} from "../api/project_mgmt";

export function useTasks(projectId: string, backlog: boolean = false) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    try {
      const token = getAccessToken();
      if (!token) {
        throw new Error("No authentication token found");
      }
      const data = await getTasks(token, {
        projectId,
        backlog,
        ordering: "-created_at",
      });
      setTasks(data.results);
    } catch (err) {
      console.error(err);
      setError("Failed to load tasks. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [backlog, projectId]);

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
    const token = getAccessToken();
    if (!token) {
      setError("No authentication token found");
      return;
    }

    const taskData = { ...data, project: projectId };

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
      const newTask = await createTask(token, projectId, taskData);
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
    id: string,
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
    const token = getAccessToken();
    if (!token) return;

    const originalTask = tasks.find((t) => t.id === id);
    if (!originalTask) return;

    // Optimistic update
    setTasks((prev) => prev.map((t) => (t.id === id ? { ...t, ...data } : t)));

    setLoading(true);
    try {
      const updatedTask = await updateTask(token, id, data);
      setTasks((prev) => prev.map((t) => (t.id === id ? updatedTask : t)));
    } catch (err) {
      // Revert on error
      setTasks((prev) => prev.map((t) => (t.id === id ? originalTask : t)));
      setError(err instanceof Error ? err.message : "Failed to update task.");
    } finally {
      setLoading(false);
    }
  };

  const removeTask = async (id: string) => {
    const taskToRemove = tasks.find((t) => t.id === id);
    if (!taskToRemove) return;

    setTasks((prev) => prev.filter((t) => t.id !== id));

    // Since backend is read-only, don't call API, just keep the optimistic update
    // setLoading(true);
    // try {
    //   await deleteTask(token, id);
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
