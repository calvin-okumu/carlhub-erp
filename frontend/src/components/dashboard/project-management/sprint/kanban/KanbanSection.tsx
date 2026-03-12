"use client";

import { getUserTenants } from '@/api/crm';
import { assignTaskToSprint, createTask, deleteTask, getSprint, getSprints, getTasks, updateTask, getMilestones } from '@/api/project_mgmt';
import type { Sprint, Task, UserTenant, Milestone } from '@/api/types';
import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import { useProject } from '@/context/ProjectContext';
import { useRouter } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';

import KanbanBoard from './KanbanBoard';
import KanbanHeader from './KanbanHeader';
import ViewTaskModal from './ViewTaskModal';
import CreateTaskModal from '@/components/shared/CreateTaskModal';

interface KanbanSectionProps {
    sprintSlug: string;
    onBack?: () => void;
}

export default function KanbanSection({ sprintSlug, onBack }: KanbanSectionProps) {
    const router = useRouter();
    const { project } = useProject();
    const [sprint, setSprint] = useState<Sprint | null>(null);
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedTask, setSelectedTask] = useState<Task | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [createModalOpen, setCreateModalOpen] = useState(false);
    const [createModalMode, setCreateModalMode] = useState<'add' | 'edit'>('add');
    const [createSelectedTask, setCreateSelectedTask] = useState<Task | null>(null);
    const [addModalOpen, setAddModalOpen] = useState(false);
    const [backlogTasks, setBacklogTasks] = useState<Task[]>([]);
    const [selectedTasks, setSelectedTasks] = useState<Array<{ id: string; slug?: string }>>([]);
    const [sprints, setSprints] = useState<Sprint[]>([]);
    const [milestones, setMilestones] = useState<Milestone[]>([]);
    const [users, setUsers] = useState<UserTenant[]>([]);
    const [addError, setAddError] = useState<string | null>(null);
    const [quickAddError, setQuickAddError] = useState<string | null>(null);
    const [dueSoonOnly, setDueSoonOnly] = useState(false);

    const fetchData = useCallback(async () => {
        const token = localStorage.getItem('access_token');
        console.log('Token:', token ? 'present' : 'missing');
            console.log('KanbanSection fetchData called with projectSlug:', project?.slug, 'sprintSlug:', sprintSlug);
        if (!token) {
            setError('No access token found. Redirecting to login...');
            setLoading(false);
            setTimeout(() => {
                router.push('/login');
            }, 2000);
            return;
        }

        try {
            // Fetch the sprint directly by ID
            console.log('Fetching sprint with slug:', sprintSlug);
            const sprint = await getSprint(token, sprintSlug);

            // Fetch tasks for this sprint
            const tasksData = await getTasks(token, { projectSlug: project?.slug, sprintSlug: sprintSlug });

            // Calculate sprint progress as average of task progress (inheriting backend pattern)
            const calculatedSprintProgress = tasksData.results.length > 0
                ? Math.round(tasksData.results.reduce((sum, task) => sum + task.progress, 0) / tasksData.results.length)
                : 0;

            setSprint({ ...sprint, progress: calculatedSprintProgress });
            setTasks(tasksData.results);
        } catch (err) {
            console.error('Fetch error:', err);
            setError(err instanceof Error ? err.message : 'Failed to fetch data. Please check your connection or try again.');
        } finally {
            setLoading(false);
        }
    }, [sprintSlug, router, project?.slug]);

    useEffect(() => {
        if (sprintSlug) {
            fetchData();
        }
    }, [sprintSlug, fetchData]);

    useEffect(() => {
        const fetchModalData = async () => {
            const token = localStorage.getItem('access_token');
            if (!token) return;
            try {
                const [sprintsData, milestonesData, usersData, backlogData] = await Promise.all([
                    getSprints(token, { projectSlug: project?.slug }),
                    getMilestones(token, { projectSlug: project?.slug }),
                    getUserTenants(token),
                    getTasks(token, { projectSlug: project?.slug, backlog: true }) // backlog=true
                ]);
                setSprints(sprintsData.results);
                setMilestones(milestonesData.results);
                setUsers(usersData);
                // Filter out tasks that are already in this sprint (safety check)
                const filteredBacklog = backlogData.results.filter((task: Task) => task.sprint !== sprint?.slug);
                setBacklogTasks(filteredBacklog);
            } catch (err) {
                console.error('Failed to fetch modal data:', err);
            }
        };
        fetchModalData();
    }, [project?.slug, sprintSlug, sprint]);

    const handleBack = () => {
        if (onBack) {
            onBack();
        } else {
            router.push(`/dashboard/project-management/${project?.slug}/sprint`);
        }
    };

    const handleTaskClick = (task: Task) => {
        setSelectedTask(task);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setSelectedTask(null);
    };

    const normalizeDate = (value?: string) => (value || '').slice(0, 10);

    const isDueSoon = (date?: string) => {
        if (!date) return false;
        const normalized = normalizeDate(date);
        if (!normalized) return false;
        const today = new Date();
        const startOfToday = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        const target = new Date(normalized);
        if (Number.isNaN(target.getTime())) return false;
        const diffDays = Math.ceil((target.getTime() - startOfToday.getTime()) / (1000 * 60 * 60 * 24));
        return diffDays >= 0 && diffDays <= 7;
    };

    const resolveMilestoneSlug = () => {
        if (!sprint) return '';
        const normalize = (value: string | undefined) => (value || '').trim().toLowerCase();
        const sprintMilestoneRaw = sprint.milestone || '';
        const sprintMilestoneValue = sprint.milestone_name || sprintMilestoneRaw;
        const sprintMilestoneNameOnly = sprintMilestoneRaw.includes('(')
            ? sprintMilestoneRaw.split('(')[0].trim()
            : sprintMilestoneRaw;
        const sprintMilestoneNormalized = normalize(sprintMilestoneValue);
        const sprintMilestoneNameNormalized = normalize(sprintMilestoneNameOnly);

        const milestoneMatch = milestones.find((milestone) => {
            const milestoneName = normalize(milestone.name);
            const milestoneSlug = normalize(milestone.slug);
            return (
                milestone.id === sprintMilestoneValue ||
                milestone.slug === sprintMilestoneValue ||
                milestoneName === sprintMilestoneNormalized ||
                milestoneSlug === sprintMilestoneNormalized ||
                milestoneName === sprintMilestoneNameNormalized
            );
        });

        const fallbackSlug = sprintMilestoneRaw && /^[a-z0-9-]+$/.test(sprintMilestoneRaw)
            ? sprintMilestoneRaw
            : '';

        return milestoneMatch?.slug || fallbackSlug;
    };

    const handleQuickAdd = async (status: string, title: string) => {
        const token = localStorage.getItem('access_token');
        if (!token) return;
        setQuickAddError(null);

        if (!project?.id || !sprint) {
            setQuickAddError('Project or sprint data is missing. Please refresh and try again.');
            return;
        }

        const milestoneSlug = resolveMilestoneSlug();
        if (!milestoneSlug) {
            setQuickAddError('Milestone data is missing. Please reload the sprint and try again.');
            return;
        }

        const startDate = normalizeDate(sprint.start_date);
        const endDate = normalizeDate(sprint.end_date);
        if (!startDate || !endDate) {
            setQuickAddError('Sprint dates are required for quick add.');
            return;
        }

        try {
            await createTask(token, project.id, {
                title,
                status,
                milestone: milestoneSlug,
                sprint: sprint.slug,
                start_date: startDate,
                end_date: endDate,
            });
            await fetchData();
        } catch (error) {
            console.error('Error creating quick task:', error);
            setQuickAddError(error instanceof Error ? error.message : 'Failed to create task');
        }
    };

    // Sprint progress calculated on frontend as average of task progress (inheriting backend averaging pattern)

    const handleStatusChange = async (taskSlug: string, newStatus: string) => {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        try {
            // Update task status - backend will handle progress calculation
            await updateTask(token, taskSlug, { status: newStatus });

            // Update local tasks state optimistically
            const updatedTasks = tasks.map(task =>
                task.slug === taskSlug
                    ? { ...task, status: newStatus, progress: getTaskProgress(newStatus) }
                    : task
            );
            setTasks(updatedTasks);

            // Recalculate sprint progress (inheriting backend averaging pattern)
            const newSprintProgress = updatedTasks.length > 0
                ? Math.round(updatedTasks.reduce((sum, task) => sum + task.progress, 0) / updatedTasks.length)
                : 0;

            if (sprint) {
                setSprint({ ...sprint, progress: newSprintProgress });
            }

            // Refetch to get updated progress from backend
            fetchData();
        } catch (error) {
            console.error('Error updating task status:', error);
            alert('Failed to update task status. Please try again.');
        }
    };

    // Helper function to get task progress based on status (matching backend Task.progress property)
    const getTaskProgress = (status: string): number => {
        const statusWeights: Record<string, number> = {
            'to_do': 0,
            'in_progress': 25,
            'in_review': 50,
            'testing': 75,
            'done': 100
        };
        return statusWeights[status] || 0;
    };

    const handleDeleteTask = async (taskSlug: string) => {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        if (!confirm('Are you sure you want to delete this task?')) return;

        try {
            await deleteTask(token, taskSlug);
            // Refetch tasks
            fetchData();
        } catch (error) {
            console.error('Error deleting task:', error);
            // TODO: Show error message
        }
    };

    const handleCreateTask = () => {
        setCreateModalMode('add');
        setCreateSelectedTask(null);
        setCreateModalOpen(true);
    };

    const handleAddTask = () => {
        setSelectedTasks([]);
        setAddError(null);
        setAddModalOpen(true);
    };

    const handleTaskSelection = (task: Task, checked: boolean) => {
        if (checked) {
            setSelectedTasks(prev => [...prev, { id: task.id, slug: task.slug }]);
        } else {
            setSelectedTasks(prev => prev.filter(item => item.id !== task.id));
        }
    };

    const handleAddSelectedTasks = async () => {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        setAddError(null);
        try {
            await Promise.all(
                selectedTasks.map(task => assignTaskToSprint(token, sprintSlug, task))
            );
            setAddModalOpen(false);
            setSelectedTasks([]);
            // Refetch tasks and update sprint progress
            await fetchData();
            // Sprint progress will be updated in fetchData since it gets the latest sprint data
        } catch (error) {
            console.error('Error adding tasks:', error);
            setAddError(error instanceof Error ? error.message : 'Failed to add tasks');
        }
    };

    const handleSaveTask = async (data: {
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
        const token = localStorage.getItem('access_token');
        if (!token) return;

        try {
            if (!project?.id) {
                setError('Project not loaded. Please refresh and try again.');
                return;
            }
            // Sprint is already set correctly by the modal
                await createTask(token, project.id, data);
            setCreateModalOpen(false);
            // Refetch tasks and update sprint progress
            await fetchData();
            // Sprint progress will be updated in fetchData since it gets the latest sprint data
        } catch (error) {
            console.error('Error saving task:', error);
            // TODO: Show error message
        }
    };

    if (loading) {
        return <Loader />;
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 p-6">
                <div className="max-w-7xl mx-auto">
                    <KanbanHeader sprint={{ id: '0', slug: 'error', name: 'Error', status: 'planned', start_date: '', end_date: '', progress: 0, tasks_count: 0, created_at: '', milestone: '0', milestone_name: '' }} onBack={handleBack} />
                    <div className="text-center">
                        <div className="text-red-500 mb-4">{error}</div>
                        <button
                            onClick={() => {
                                setError(null);
                                setLoading(true);
                                setSprint(null);
                                fetchData();
                            }}
                            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            Retry
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (!sprint) {
        return (
            <div className="min-h-screen bg-gray-50 p-6">
                <div className="max-w-7xl mx-auto">
                    <KanbanHeader sprint={{ id: '0', slug: 'not-found', name: 'Not Found', status: 'planned', start_date: '', end_date: '', progress: 0, tasks_count: 0, created_at: '', milestone: '0', milestone_name: '' }} onBack={handleBack} />
                    <div className="text-center">Sprint not found</div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto">
                <KanbanHeader
                    sprint={sprint}
                    onBack={handleBack}
                    dueSoonOnly={dueSoonOnly}
                    onToggleDueSoon={() => setDueSoonOnly((prev) => !prev)}
                />
                <div className="flex gap-2 mb-4">
                    <Button className='bg-green-600 hover:bg-green-400' onClick={handleAddTask}>Add Task</Button>
                    <Button onClick={handleCreateTask}>Create Task</Button>
                </div>
                {quickAddError && (
                    <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
                        {quickAddError}
                    </div>
                )}
                <KanbanBoard
                    tasks={dueSoonOnly ? tasks.filter((task) => isDueSoon(task.end_date)) : tasks}
                    onTaskClick={handleTaskClick}
                    onStatusChange={handleStatusChange}
                    onQuickAdd={handleQuickAdd}
                />
                {selectedTask && (
                    <ViewTaskModal
                        isOpen={isModalOpen}
                        onClose={handleCloseModal}
                        task={selectedTask}
                        onStatusChange={handleStatusChange}
                        onDelete={handleDeleteTask}
                    />
                )}
                <CreateTaskModal
                    isOpen={createModalOpen}
                    onClose={() => setCreateModalOpen(false)}
                    mode={createModalMode}
                    task={createSelectedTask || undefined}
                    sprints={sprints}
                    milestones={milestones}
                    assignees={users}
                    projectStartDate={project?.start_date}
                    projectEndDate={project?.end_date}
                    onSave={handleSaveTask}
                    isKanban={true}
                    sprintContext={sprint}
                />
                {addModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center">
                        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm" onClick={() => setAddModalOpen(false)}></div>
                        <div className="relative z-10 bg-white rounded-2xl shadow-lg w-full max-w-2xl p-6">
                            <button
                                onClick={() => setAddModalOpen(false)}
                                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Tasks from Backlog</h3>
                            {addError && (
                                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                                    {addError}
                                </div>
                            )}
                            <div className="max-h-96 overflow-y-auto">
                                {backlogTasks.length === 0 ? (
                                    <p className="text-gray-500">No backlog tasks available.</p>
                                ) : (
                                    backlogTasks.map(task => (
                                        <div key={task.id} className="flex items-center space-x-3 p-3 border-b">
                                            <input
                                                type="checkbox"
                                                checked={selectedTasks.some(item => item.id === task.id)}
                                                onChange={(e) => handleTaskSelection(task, e.target.checked)}
                                                className="h-4 w-4 text-blue-600"
                                            />
                                            <div>
                                                <p className="font-medium">{task.title}</p>
                                                <p className="text-sm text-gray-600">{task.description || 'No description'}</p>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                            <div className="mt-6 flex justify-end space-x-3">
                                <Button onClick={() => setAddModalOpen(false)} variant="outline">
                                    Cancel
                                </Button>
                                <Button onClick={handleAddSelectedTasks} variant="gradient">
                                    Add Selected ({selectedTasks.length})
                                </Button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
