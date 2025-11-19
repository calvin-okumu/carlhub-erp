"use client";

import { getUserTenants } from '@/api/crm';
import type { Task, UserTenant } from '@/api/types';
import CreateTaskModal from '@/components/shared/CreateTaskModal';
import SearchInput from '@/components/shared/SearchInput';
import Button from '@/components/ui/Button';
import { useProject } from '@/context/ProjectContext';
import { useSprintsContext } from '@/context/SprintsContext';
import { useMilestonesContext } from '@/context/MilestonesContext';
import { useTasks } from '@/hooks/useTasks';
import { getAccessToken } from '@/utils/auth';
import { Plus } from 'lucide-react';
import { useEffect, useState } from 'react';
import BacklogTable from './BacklogTable';

export default function BacklogSection() {
    const { project } = useProject();
    const { sprints } = useSprintsContext();
    const { milestones } = useMilestonesContext();
    const { tasks, loading, error, addTask, editTask, removeTask } = useTasks(project?.id || '', true);
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedTask, setSelectedTask] = useState<Task | null>(null);
    const [searchValue, setSearchValue] = useState('');
    const [users, setUsers] = useState<UserTenant[]>([]);

    useEffect(() => {
        const fetchUsers = async () => {
            const token = getAccessToken();
            if (!token) return;

            try {
                const usersData = await getUserTenants(token);
                setUsers(usersData);
            } catch (err) {
                console.error('Failed to fetch users:', err);
            }
        };

        fetchUsers();
    }, []);

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
                await editTask(selectedTask.id, data);
            }
            setModalOpen(false);
        } catch (error) {
            console.error('Error saving task:', error);
            // TODO: Show error message
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <SearchInput
                    value={searchValue}
                    onChange={setSearchValue}
                    placeholder="Search tasks..."
                />
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
                projectSlug={project?.slug || ''}
            />
            <CreateTaskModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                mode={modalMode}
                task={selectedTask || undefined}
                sprints={sprints}
                assignees={users}
                milestones={milestones}
                onSave={handleSaveTask}
                isBacklog={true}
            />
        </div>
    );
};
