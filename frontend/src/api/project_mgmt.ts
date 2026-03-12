import { Project, Milestone, Sprint, Task, PaginatedResponse } from './types';
import { API_BASE } from './index';
import { authFetch } from './client';

function getProjectErrorMessage(data: unknown, fallback: string) {
  if (data && typeof data === "object") {
    const record = data as Record<string, unknown>;
    const nameError = record.name;
    if (Array.isArray(nameError)) {
      const duplicateName = nameError.find(
        (message) =>
          typeof message === "string" &&
          message.toLowerCase().includes("already exists"),
      );
      if (duplicateName) {
        return "Project name already exists.";
      }
    }
    if (typeof record.detail === "string") return record.detail;
    if (typeof record.error === "string") return record.error;
    const nonFieldErrors = record.non_field_errors;
    if (Array.isArray(nonFieldErrors) && typeof nonFieldErrors[0] === "string") {
      return nonFieldErrors[0];
    }
  }

  return fallback;
}

function normalizeMilestoneStatus(status?: string) {
  if (status === "planned") return "planning";
  return status;
}

export async function getProjects(token: string, params?: { tenant?: string; search?: string; ordering?: string; status?: string; client?: string; priority?: string; page?: number; limit?: number }): Promise<PaginatedResponse<Project>> {
  const query = new URLSearchParams();
  if (params?.tenant) query.append('tenant', params.tenant.toString());
  if (params?.search) query.append('search', params.search);
  if (params?.ordering) query.append('ordering', params.ordering);
  if (params?.status) query.append('status', params.status);
  if (params?.client) query.append('client', params.client.toString());
  if (params?.priority) query.append('priority', params.priority);
  if (params?.page) query.append('page', params.page.toString());
  if (params?.limit) query.append('limit', params.limit.toString());

  const url = `${API_BASE}/projects/?${query.toString()}`;
  const response = await authFetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch projects");
  }

  // Return full paginated response
  return data;
}

export async function getProject(token: string, slug: string, tenant?: string): Promise<Project> {
  const query = new URLSearchParams();
  if (tenant) query.append('tenant', tenant.toString());
  const url = `${API_BASE}/projects/${slug}/${query.toString() ? `?${query.toString()}` : ''}`;
  const response = await authFetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(getProjectErrorMessage(data, "Failed to fetch project"));
  }

  return data;
}

export async function createProject(token: string, projectData: {
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
}): Promise<Project> {
  const response = await authFetch(`${API_BASE}/projects/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(projectData),
  });

  console.log('Response status:', response.status, response.statusText);

  const data = await response.json();

  if (!response.ok) {
    console.error('Create project failed:', data);
    throw new Error(
      getProjectErrorMessage(
        data,
        `Failed to create project: ${response.status} ${response.statusText}`,
      ),
    );
  }

  return data;
}

export async function updateProject(token: string, slug: string, projectData: Partial<{
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
}>): Promise<Project> {
  const response = await authFetch(`${API_BASE}/projects/${slug}/`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(projectData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      getProjectErrorMessage(
        data,
        `Failed to update project: ${response.status} ${response.statusText}`,
      ),
    );
  }

  return data;
}

export async function deleteProject(token: string, slug: string): Promise<void> {
  const response = await authFetch(`${API_BASE}/projects/${slug}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || "Failed to delete project");
  }
}

// Milestone API functions
export async function getMilestones(token: string, params?: { projectId?: string; projectSlug?: string; tenant?: number; search?: string; ordering?: string; status?: string; page?: number; limit?: number }): Promise<PaginatedResponse<Milestone>> {
  let url = `${API_BASE}/milestones/`;
  const query = new URLSearchParams();
  if (params?.projectSlug) {
    query.append('project__slug', params.projectSlug);
  } else if (params?.projectId) {
    query.append('project', params.projectId.toString());
  }
  if (params?.tenant) query.append('tenant', params.tenant.toString());
  if (params?.search) query.append('search', params.search);
  if (params?.ordering) query.append('ordering', params.ordering);
  if (params?.status) query.append('status', params.status);
  if (params?.page) query.append('page', params.page.toString());
  if (params?.limit) query.append('limit', params.limit.toString());
  if (query.toString()) url += `?${query.toString()}`;

  const response = await authFetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch milestones");
  }

  // Return full paginated response
  return data;
}

export async function getMilestone(token: string, id: string): Promise<Milestone> {
  const response = await authFetch(`${API_BASE}/milestones/${id}/`, {  // Keep global for individual milestone access
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch milestone");
  }

  return data;
}

export async function createMilestone(token: string, milestoneData: {
  name: string;
  description?: string;
  status: string;
  planned_start?: string;
  actual_start?: string;
  due_date?: string;
  assignee?: number;
  project: string;
}): Promise<Milestone> {
  const response = await authFetch(`${API_BASE}/milestones/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ...milestoneData,
      status: normalizeMilestoneStatus(milestoneData.status),
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to create milestone");
  }

  return data;
}

type MilestoneUpdateData = Partial<{
  name: string;
  description: string;
  status: string;
  progress: number;
  planned_start: string;
  actual_start: string;
  due_date: string;
  assignee: number;
  project: string;
}>;

export async function updateMilestone(token: string, slug: string, milestoneData: MilestoneUpdateData): Promise<Milestone> {
  const response = await authFetch(`${API_BASE}/milestones/${slug}/`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ...milestoneData,
      status: normalizeMilestoneStatus(milestoneData.status),
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to update milestone");
  }

  return data;
}

export async function deleteMilestone(token: string, slug: string): Promise<void> {
  const response = await authFetch(`${API_BASE}/milestones/${slug}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || "Failed to delete milestone");
  }
}

// Sprint API functions
export async function getSprints(token: string, params?: { projectId?: string; projectSlug?: string; search?: string; ordering?: string; status?: string; page?: number; limit?: number }): Promise<PaginatedResponse<Sprint>> {
  let url = `${API_BASE}/sprints/`;
  const query = new URLSearchParams();
  if (params?.projectSlug) {
    query.append('milestone__project__slug', params.projectSlug);
  } else if (params?.projectId) {
    query.append('milestone__project', params.projectId.toString());
  }
  if (params?.search) query.append('search', params.search);
  if (params?.ordering) query.append('ordering', params.ordering);
  if (params?.status) query.append('status', params.status);
  if (params?.page) query.append('page', params.page.toString());
  if (params?.limit) query.append('limit', params.limit.toString());
  if (query.toString()) url += `?${query.toString()}`;

  const response = await authFetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch sprints");
  }

  // Return full paginated response
  return data;
}

export async function getSprint(token: string, id: string): Promise<Sprint> {
  const response = await authFetch(`${API_BASE}/sprints/${id}/`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch sprint");
  }

  return data;
}

export async function createSprint(token: string, sprintData: {
  name: string;
  status: string;
  start_date?: string;
  end_date?: string;
  milestone: string;
}): Promise<Sprint> {
  const response = await authFetch(`${API_BASE}/sprints/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(sprintData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to create sprint");
  }

  return data;
}

export async function updateSprint(token: string, slug: string, sprintData: Partial<{
  name: string;
  status: string;
  start_date: string;
  end_date: string;
  milestone: string;
}>): Promise<Sprint> {
  const response = await authFetch(`${API_BASE}/sprints/${slug}/`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(sprintData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to update sprint");
  }

  return data;
}

export async function deleteSprint(token: string, slug: string): Promise<void> {
  const response = await authFetch(`${API_BASE}/sprints/${slug}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || "Failed to delete sprint");
  }
}

// Sprint task management
export async function createTaskInSprint(token: string, projectId: string, sprintSlug: string, taskData: {
  title: string;
  description?: string;
  status: string;
  milestone: string;
  assignee?: number;
  start_date?: string;
  end_date?: string;
  estimated_hours?: number;
}): Promise<Task> {
  const taskDataWithSprint = { ...taskData, sprint: sprintSlug };
  const response = await authFetch(`${API_BASE}/tasks/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(taskDataWithSprint),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to create task in sprint");
  }

  return data;
}

export async function assignTaskToSprint(token: string, sprintSlug: string, task: { id?: string; slug?: string } | string): Promise<{ message: string }> {
  const payload = typeof task === 'string'
    ? { task_slug: task }
    : task.slug
      ? { task_slug: task.slug }
      : { task_id: task.id };
  if (!payload.task_slug && !payload.task_id) {
    throw new Error('task_slug or task_id is required');
  }
  const response = await authFetch(`${API_BASE}/sprints/${sprintSlug}/assign_task/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to assign task to sprint");
  }

  return data;
}

export async function unassignTaskFromSprint(token: string, sprintSlug: string, task: { id?: string; slug?: string } | string): Promise<{ message: string }> {
  const payload = typeof task === 'string'
    ? { task_slug: task }
    : task.slug
      ? { task_slug: task.slug }
      : { task_id: task.id };
  if (!payload.task_slug && !payload.task_id) {
    throw new Error('task_slug or task_id is required');
  }
  const response = await authFetch(`${API_BASE}/sprints/${sprintSlug}/unassign_task/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to unassign task from sprint");
  }

  return data;
}

// Task API functions
export async function getTasks(token: string, params?: { milestoneSlug?: string; sprintSlug?: string; projectId?: string; projectSlug?: string; backlog?: boolean; search?: string; ordering?: string; status?: string; page?: number; limit?: number }): Promise<PaginatedResponse<Task>> {
  let url = `${API_BASE}/tasks/`;
  const query = new URLSearchParams();

  if (params?.projectSlug) {
    query.append('milestone__project__slug', params.projectSlug);
  } else if (params?.projectId) {
    query.append('milestone__project', params.projectId.toString());
  }
  if (params?.milestoneSlug) query.append('milestone__slug', params.milestoneSlug);
  if (params?.sprintSlug) query.append('sprint__slug', params.sprintSlug);
  if (params?.backlog !== undefined) query.append('backlog', params.backlog.toString());
  if (params?.search) query.append('search', params.search);
  if (params?.ordering) query.append('ordering', params.ordering);
  if (params?.status) query.append('status', params.status);
  if (params?.page) query.append('page', params.page.toString());
  if (params?.limit) query.append('limit', params.limit.toString());

  if (query.toString()) {
    url += `?${query.toString()}`;
  }

  const response = await authFetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  let data;
  try {
    data = await response.json();
  } catch {
    data = { error: 'Invalid JSON response' };
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.status} ${response.statusText}. ${data.error || ''}`);
  }

  // Return full paginated response
  return data;
}

export async function getTask(token: string, slug: string): Promise<Task> {
  const response = await authFetch(`${API_BASE}/tasks/${slug}/`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch task");
  }

  return data;
}

export async function createTask(token: string, projectId: string, taskData: {
  title: string;
  description?: string;
  status: string;
  milestone: string;
  sprint?: string;
  assignee?: number;
  start_date?: string;
  end_date?: string;
  estimated_hours?: number;
}): Promise<Task> {
  const response = await authFetch(`${API_BASE}/tasks/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(taskData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to create task");
  }

  return data;
}

export async function updateTask(token: string, slug: string, taskData: Partial<{
  title: string;
  description: string;
  status: string;
  progress: number;
  milestone: string;
  sprint: string;
  assignee: number;
  start_date: string;
  end_date: string;
  estimated_hours: number;
}>): Promise<Task> {
  const response = await authFetch(`${API_BASE}/tasks/${slug}/`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(taskData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to update task");
  }

  return data;
}

export async function deleteTask(token: string, slug: string): Promise<void> {
  const response = await authFetch(`${API_BASE}/tasks/${slug}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || "Failed to delete task");
  }
}
