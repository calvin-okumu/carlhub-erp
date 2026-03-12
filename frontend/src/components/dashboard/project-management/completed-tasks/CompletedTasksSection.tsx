"use client";

import React, { useState, useEffect } from 'react';
import { getTasks } from '@/api/project_mgmt';
import type { Task } from '@/api/types';
import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import Table from '@/components/ui/Table';
import Card from '@/components/ui/Card';
import { useProject } from '@/context/ProjectContext';
import { Trash2 } from 'lucide-react';

export default function CompletedTasksSection() {
    const { project } = useProject();
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchCompletedTasks = async () => {
            const token = localStorage.getItem('access_token');
            if (!token) {
                setError('No access token found');
                setLoading(false);
                return;
            }

            try {
                // Get all tasks for the project and filter for completed status
                const allTasks = await getTasks(token, { projectSlug: project?.slug });
                const completedTasks = allTasks.results.filter(task => task.status === 'done');
                setTasks(completedTasks);
            } catch (err) {
                console.error('Failed to fetch completed tasks:', err);
                setError(err instanceof Error ? err.message : 'Failed to fetch completed tasks');
            } finally {
                setLoading(false);
            }
        };

        if (project?.slug) {
            fetchCompletedTasks();
        }
    }, [project?.slug]);

    const handleDeleteTask = async (taskSlug: string) => {
        if (!confirm('Are you sure you want to delete this completed task?')) return;

        const token = localStorage.getItem('access_token');
        if (!token) return;

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/tasks/${taskSlug}/`, {
                method: 'DELETE',
                headers: {
                    Authorization: `Token ${token}`,
                },
            });

            if (!response.ok) {
                throw new Error('Failed to delete task');
            }

            // Remove from local state
            setTasks(tasks.filter(task => task.slug !== taskSlug));
        } catch (err) {
            console.error('Failed to delete task:', err);
            alert('Failed to delete task');
        }
    };

    if (loading) return <Loader />;
    if (error) return <div className="p-6 text-center text-red-500">{error}</div>;

    return (
        <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-200/70 bg-white/90 p-5 shadow-sm">
                <div>
                    <h2 className="text-xl font-semibold text-slate-900">Completed Tasks</h2>
                    <p className="text-xs text-slate-500">Delivered work across sprints.</p>
                </div>
                <div className="text-sm text-slate-500">
                    {tasks.length} completed task{tasks.length !== 1 ? 's' : ''}
                </div>
            </div>

            {tasks.length === 0 ? (
                <Card className="!rounded-2xl !border-slate-200/70 !shadow-sm text-center py-12">
                    <div className="text-slate-400 text-lg mb-2">No completed tasks yet</div>
                    <p className="text-slate-500">Tasks will appear here once they are marked as completed in sprints.</p>
                </Card>
            ) : (
                <div className="bg-white/90 rounded-2xl border border-slate-200/70 shadow-sm overflow-hidden">
                    <Table
                        headers={['Title', 'Description', 'Sprint', 'Completed Date', 'Actions']}
                        rows={tasks.map(task => ({
                            key: task.id,
                            data: [
                                task.title,
                                <span key="desc" className="max-w-xs truncate block">{task.description || 'No description'}</span>,
                                task.sprint_name || task.sprint || 'N/A',
                                task.updated_at ? new Date(task.updated_at).toLocaleDateString() : 'N/A',
                                <Button
                                    key="delete"
                                    onClick={() => handleDeleteTask(task.slug)}
                                    variant="outline"
                                    size="sm"
                                    className="text-red-600 hover:text-red-800"
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            ]
                        }))}
                    />
                </div>
            )}
        </div>
    );
}
