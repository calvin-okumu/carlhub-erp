import { Project, Milestone, Sprint, Task, PaginatedResponse } from './types';
import { API_BASE } from './index';

export async function getProjects(token: string, params?: { tenant?: number; search?: string; ordering?: string; status?: string; client?: number; priority?: string; page?: number; limit?: number }): Promise<PaginatedResponse<Project>> {
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
  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
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

export async function getProject(token: string, id: string): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/${id}/`, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch project");
  }

  return data;
}

export async function createProject(token: string, projectData: {
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
}): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/`, {
    method: "POST",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(projectData),
  });

  console.log('Response status:', response.status, response.statusText);

  const data = await response.json();

  if (!response.ok) {
    console.error('Create project failed:', data);
    throw new Error(data.error || `Failed to create project: ${response.status} ${response.statusText}`);
  }

  return data;
}

export async function updateProject(token: string, slug: string, projectData: Partial<{
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
}>): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects/${slug}/`, {
    method: "PUT",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(projectData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to update project");
  }

  return data;
}

export async function deleteProject(token: string, slug: string): Promise<void> {
  const response = await fetch(`${API_BASE}/projects/${slug}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Token ${token}`,
    },
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || "Failed to delete project");
  }
}

// Milestone API functions
export async function getMilestones(token: string, params?: { projectSlug?: string; tenant?: number; search?: string; ordering?: string; status?: string; page?: number; limit?: number }): Promise<PaginatedResponse<Milestone>> {
  let url = `${API_BASE}/milestones/`;
  const query = new URLSearchParams();
  if (params?.projectSlug) query.append('project__slug', params.projectSlug);
  if (params?.tenant) query.append('tenant', params.tenant.toString());
  if (params?.search) query.append('search', params.search);
  if (params?.ordering) query.append('ordering', params.ordering);
  if (params?.status) query.append('status', params.status);
  if (params?.page) query.append('page', params.page.toString());
  if (params?.limit) query.append('limit', params.limit.toString());
  if (query.toString()) url += `?${query.toString()}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
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

export async function getMilestone(token: string, id: number): Promise<Milestone> {
  const response = await fetch(`${API_BASE}/milestones/${id}/`, {  // Keep global for individual milestone access
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch milestone");
  }

  return data;
}

export async function createMilestone(token: string, projectSlug: string, milestoneData: {
  name: string;
  description?: string;
  status: string;
  planned_start?: string;
  actual_start?: string;
  due_date?: string;
  assignee?: number;
  project: number;
  tenant: number;
}): Promise<Milestone> {
  const response = await fetch(`${API_BASE}/milestones/`, {
    method: "POST",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(milestoneData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to create milestone");
  }

  return data;
}

export async function updateMilestone(token: string, slug: string, milestoneData: Partial<{
  name: string;
  description: string;
  status: string;
  progress: number;
  planned_start: string;
  actual_start: string;
  due_date: string;
  assignee: number;
  project: number;
}>): Promise<Milestone> {
  const response = await fetch(`${API_BASE}/milestones/${slug}/`, {
    method: "PUT",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(milestoneData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to update milestone");
  }

  return data;
}

export async function deleteMilestone(token: string, slug: string): Promise<void> {
  const response = await fetch(`${API_BASE}/milestones/${slug}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Token ${token}`,
    },
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || "Failed to delete milestone");
  }
}

// Sprint API functions
export async function getSprints(token: string, params?: { projectSlug?: string; search?: string; ordering?: string; status?: string; page?: number; limit?: number }): Promise<PaginatedResponse<Sprint>> {
  let url = `${API_BASE}/sprints/`;
  const query = new URLSearchParams();
  if (params?.projectSlug) query.append('milestone__project__slug', params.projectSlug);
  if (params?.search) query.append('search', params.search);
  if (params?.ordering) query.append('ordering', params.ordering);
  if (params?.status) query.append('status', params.status);
  if (params?.page) query.append('page', params.page.toString());
  if (params?.limit) query.append('limit', params.limit.toString());
  if (query.toString()) url += `?${query.toString()}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
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
  const response = await fetch(`${API_BASE}/sprints/${id}/`, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch sprint");
  }

  return data;
}

export async function createSprint(token: string, projectSlug: string, sprintData: {
  name: string;
  status: string;
  start_date?: string;
  end_date?: string;
  milestone: string;
}): Promise<Sprint> {
  const response = await fetch(`${API_BASE}/sprints/`, {
    method: "POST",
    headers: {
      Authorization: `Token ${token}`,
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
  const response = await fetch(`${API_BASE}/sprints/${slug}/`, {
    method: "PUT",
    headers: {
      Authorization: `Token ${token}`,
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
  const response = await fetch(`${API_BASE}/sprints/${slug}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Token ${token}`,
    },
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || "Failed to delete sprint");
  }
}

// Sprint task management
export async function createTaskInSprint(token: string, projectSlug: string, sprintSlug: string, taskData: {
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
  const response = await fetch(`${API_BASE}/tasks/`, {
    method: "POST",
    headers: {
      Authorization: `Token ${token}`,
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

export async function assignTaskToSprint(token: string, sprintSlug: string, taskSlug: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/sprints/${sprintSlug}/assign_task/`, {
    method: "POST",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ task_id: taskSlug }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to assign task to sprint");
  }

  return data;
}

export async function unassignTaskFromSprint(token: string, sprintSlug: string, taskSlug: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/sprints/${sprintSlug}/unassign_task/`, {
    method: "POST",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ task_id: taskSlug }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to unassign task from sprint");
  }

  return data;
}

// Task API functions
export async function getTasks(token: string, params?: { milestoneSlug?: string; sprintSlug?: string; projectSlug?: string; backlog?: boolean; search?: string; ordering?: string; status?: string; page?: number; limit?: number }): Promise<PaginatedResponse<Task>> {
  let url = `${API_BASE}/tasks/`;
  const query = new URLSearchParams();

  if (params?.projectSlug) query.append('milestone__project__slug', params.projectSlug);
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

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch tasks");
  }

  // Return full paginated response
  return data;
}

export async function getTask(token: string, slug: string): Promise<Task> {
  const response = await fetch(`${API_BASE}/tasks/${slug}/`, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to fetch task");
  }

  return data;
}

export async function createTask(token: string, projectSlug: string, taskData: {
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
  const response = await fetch(`${API_BASE}/tasks/`, {
    method: "POST",
    headers: {
      Authorization: `Token ${token}`,
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
  const response = await fetch(`${API_BASE}/tasks/${slug}/`, {
    method: "PATCH",
    headers: {
      Authorization: `Token ${token}`,
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
  const response = await fetch(`${API_BASE}/tasks/${slug}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Token ${token}`,
    },
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || "Failed to delete task");
  }
}