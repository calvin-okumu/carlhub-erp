"use client";

import { getUserTenants } from '@/api/crm';
import { getMilestones, getSprints } from '@/api/project_mgmt';
import type { Milestone, Sprint, Task, UserTenant } from '@/api/types';
import CreateTaskModal from '@/components/shared/CreateTaskModal';
import SearchInput from '@/components/shared/SearchInput';
import Button from '@/components/ui/Button';
import { useProject } from '@/context/ProjectContext';
import { useTasks } from '@/hooks/useTasks';
import { Plus } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import BacklogTable from './BacklogTable';

export default function BacklogSection() {
    const { project } = useProject();
    const { tasks, loading, error, addTask, editTask, removeTask } = useTasks(project?.slug || '', true);
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedTask, setSelectedTask] = useState<Task | null>(null);
    const [searchValue, setSearchValue] = useState('');
    const [dueSoonOnly, setDueSoonOnly] = useState(false);
    const [milestones, setMilestones] = useState<Milestone[]>([]);
    const [sprints, setSprints] = useState<Sprint[]>([]);
    const [users, setUsers] = useState<UserTenant[]>([]);

    const isDueSoon = useCallback((date?: string) => {
        if (!date) return false;
        const normalized = date.slice(0, 10);
        const target = new Date(normalized);
        if (Number.isNaN(target.getTime())) return false;
        const today = new Date();
        const startOfToday = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        const diffDays = Math.ceil((target.getTime() - startOfToday.getTime()) / (1000 * 60 * 60 * 24));
        return diffDays >= 0 && diffDays <= 7;
    }, []);

    const filteredTasks = useMemo(() => {
        const normalizedSearch = searchValue.trim().toLowerCase();
        const base = dueSoonOnly ? tasks.filter((task) => isDueSoon(task.end_date)) : tasks;
        if (!normalizedSearch) return base;
        return base.filter(task =>
            task.title.toLowerCase().includes(normalizedSearch) ||
            (task.description && task.description.toLowerCase().includes(normalizedSearch))
        );
    }, [tasks, searchValue, dueSoonOnly, isDueSoon]);

    const dueSoonCount = useMemo(() =>
        tasks.filter((task) => isDueSoon(task.end_date)).length,
        [tasks, isDueSoon]
    );

    const backlogStats = useMemo(() => {
        const total = tasks.length;
        const unassigned = tasks.filter((task) => !task.assignee).length;
        const highPriority = tasks.filter((task) => task.priority === 'high').length;
        const completed = tasks.filter((task) => task.status === 'done').length;
        return { total, unassigned, highPriority, completed };
    }, [tasks]);

    const hasFilters = searchValue.trim().length > 0 || dueSoonOnly;

    useEffect(() => {
        const fetchData = async () => {
            const token = localStorage.getItem('access_token');
            if (!token) return;

            try {
                const [milestonesData, sprintsData, usersData] = await Promise.all([
                    getMilestones(token, { projectSlug: project?.slug }),
                    getSprints(token, { projectSlug: project?.slug }),
                    getUserTenants(token)
                ]);
                setMilestones(milestonesData.results);
                setSprints(sprintsData.results);
                setUsers(usersData);
            } catch (err) {
                console.error('Failed to fetch data:', err);
            }
        };

        fetchData();
    }, [project?.slug]);

    const handleAddTask = () => {
        setModalMode('add');
        setSelectedTask(null);
        setModalOpen(true);
    };

    const handleEditTask = (task: Task) => {
        setModalMode('edit');
        setSelectedTask(task);
        setModalOpen(true);
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
        try {
            if (modalMode === 'add') {
                await addTask(data);
            } else if (selectedTask) {
                await editTask(selectedTask.slug, data);
            }
            setModalOpen(false);
        } catch (error) {
            console.error('Error saving task:', error);
            // TODO: Show error message
        }
    };

    return (
        <div className="space-y-6">
            <section className="rounded-2xl border border-slate-200/70 bg-white/90 p-6 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="min-w-[240px] flex-1 space-y-2">
                        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Project backlog</p>
                        <h2 className="text-2xl font-semibold text-slate-900">Backlog</h2>
                        <p className="text-sm text-slate-600">Review, prioritize, and prepare upcoming work for future sprints.</p>
                    </div>
                    <Button onClick={handleAddTask}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Task
                    </Button>
                </div>

                <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,320px)_minmax(0,1fr)]">
                    <div className="space-y-4 rounded-xl border border-slate-200/70 bg-slate-50/70 p-4">
                        <div className="space-y-2">
                            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Filters</p>
                            <SearchInput
                                value={searchValue}
                                onChange={setSearchValue}
                                placeholder="Search backlog tasks..."
                            />
                        </div>
                        <button
                            type="button"
                            onClick={() => setDueSoonOnly((prev) => !prev)}
                            className={`inline-flex items-center justify-between gap-2 rounded-full border px-4 py-1.5 text-[10px] font-semibold uppercase tracking-[0.25em] transition-all ${
                                dueSoonOnly
                                    ? 'border-slate-900 bg-slate-900 text-white'
                                    : 'border-slate-200/70 bg-white text-slate-500 hover:border-slate-300'
                            }`}
                        >
                            Due soon
                            <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold tracking-normal ${
                                dueSoonOnly ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'
                            }`}>
                                {dueSoonCount}
                            </span>
                        </button>
                        <div className="rounded-xl border border-slate-200/70 bg-white px-3 py-2 text-xs text-slate-500">
                            Showing <span className="font-semibold text-slate-900">{filteredTasks.length}</span> of {tasks.length} tasks
                        </div>
                        {hasFilters && (
                            <button
                                type="button"
                                onClick={() => {
                                    setSearchValue('');
                                    setDueSoonOnly(false);
                                }}
                                className="rounded-full border border-slate-200/70 bg-white px-3 py-1 text-xs font-semibold text-slate-600 transition-colors hover:border-slate-300 hover:text-slate-800"
                            >
                                Clear filters
                            </button>
                        )}
                    </div>
                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                        <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total</p>
                            <div className="mt-3 flex items-baseline justify-between">
                                <span className="text-2xl font-semibold text-slate-900">{backlogStats.total}</span>
                                <span className="text-xs font-medium text-slate-500">Tasks</span>
                            </div>
                            <p className="mt-3 text-xs text-slate-500">Active backlog items.</p>
                        </div>
                        <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Due soon</p>
                            <div className="mt-3 flex items-baseline justify-between">
                                <span className="text-2xl font-semibold text-slate-900">{dueSoonCount}</span>
                                <span className="text-xs font-medium text-amber-600">Next 7 days</span>
                            </div>
                            <p className="mt-3 text-xs text-slate-500">Upcoming deadlines.</p>
                        </div>
                        <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Unassigned</p>
                            <div className="mt-3 flex items-baseline justify-between">
                                <span className="text-2xl font-semibold text-slate-900">{backlogStats.unassigned}</span>
                                <span className="text-xs font-medium text-slate-500">Needs owner</span>
                            </div>
                            <p className="mt-3 text-xs text-slate-500">Assign for progress.</p>
                        </div>
                        <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">High priority</p>
                            <div className="mt-3 flex items-baseline justify-between">
                                <span className="text-2xl font-semibold text-slate-900">{backlogStats.highPriority}</span>
                                <span className="text-xs font-medium text-rose-600">Critical</span>
                            </div>
                            <p className="mt-3 text-xs text-slate-500">Requires focus.</p>
                        </div>
                    </div>
                </div>
            </section>
            <BacklogTable
                tasks={tasks}
                loading={loading}
                error={error}
                onEditTask={handleEditTask}
                onDeleteTask={removeTask}
                onAddTask={handleAddTask}
                searchValue={searchValue}
                dueSoonOnly={dueSoonOnly}
                onClearFilters={() => {
                    setSearchValue('');
                    setDueSoonOnly(false);
                }}
            />
            <CreateTaskModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                mode={modalMode}
                task={selectedTask || undefined}
                sprints={sprints}
                assignees={users}
                milestones={milestones}
                projectStartDate={project?.start_date}
                projectEndDate={project?.end_date}
                onSave={handleSaveTask}
                isBacklog={true}
            />
        </div>
    );
};
