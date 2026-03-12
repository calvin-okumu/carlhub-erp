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
import { useEffect, useState } from 'react';
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
            <div className="flex flex-wrap items-center justify-between gap-3">
                <SearchInput
                    value={searchValue}
                    onChange={setSearchValue}
                    placeholder="Search tasks..."
                />
                <button
                    type="button"
                    onClick={() => setDueSoonOnly((prev) => !prev)}
                    className={`rounded-full border px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] transition-all ${
                        dueSoonOnly
                            ? 'border-slate-900 bg-slate-900 text-white'
                            : 'border-slate-200/70 bg-white text-slate-500 hover:border-slate-300'
                    }`}
                >
                    Due soon
                </button>
                <Button onClick={handleAddTask}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Task
                </Button>
            </div>
            <BacklogTable
                tasks={tasks}
                loading={loading}
                error={error}
                onEditTask={handleEditTask}
                onDeleteTask={removeTask}
                onAddTask={handleAddTask}
                searchValue={searchValue}
                dueSoonOnly={dueSoonOnly}
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
