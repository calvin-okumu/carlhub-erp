"use client";

import React, { useState, useEffect } from 'react';
import { getTasks } from '@/api/project_mgmt';
import type { Task } from '@/api/types';
import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import Table from '@/components/ui/Table';
import Card from '@/components/ui/Card';
import { Trash2 } from 'lucide-react';

interface CompletedTasksSectionProps {
    projectId: number;
}

export default function CompletedTasksSection({ projectId }: CompletedTasksSectionProps) {
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
                const allTasks = await getTasks(token, { projectId });
                const completedTasks = allTasks.filter(task => task.status === 'done');
                setTasks(completedTasks);
            } catch (err) {
                console.error('Failed to fetch completed tasks:', err);
                setError(err instanceof Error ? err.message : 'Failed to fetch completed tasks');
            } finally {
                setLoading(false);
            }
        };

        fetchCompletedTasks();
    }, [projectId]);

    const handleDeleteTask = async (taskId: number) => {
        if (!confirm('Are you sure you want to delete this completed task?')) return;

        const token = localStorage.getItem('access_token');
        if (!token) return;

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/tasks/${taskId}/`, {
                method: 'DELETE',
                headers: {
                    Authorization: `Token ${token}`,
                },
            });

            if (!response.ok) {
                throw new Error('Failed to delete task');
            }

            // Remove from local state
            setTasks(tasks.filter(task => task.id !== taskId));
        } catch (err) {
            console.error('Failed to delete task:', err);
            alert('Failed to delete task');
        }
    };

    if (loading) return <Loader />;
    if (error) return <div className="p-6 text-center text-red-500">{error}</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Completed Tasks</h2>
                <div className="text-sm text-gray-500">
                    {tasks.length} completed task{tasks.length !== 1 ? 's' : ''}
                </div>
            </div>

             {tasks.length === 0 ? (
                 <Card className="text-center py-12">
                     <div className="text-gray-400 text-lg mb-2">No completed tasks yet</div>
                     <p className="text-gray-500">Tasks will appear here once they are marked as completed in sprints.</p>
                 </Card>
             ) : (
                <Table
                    headers={['Title', 'Description', 'Sprint', 'Completed Date', 'Actions']}
                    rows={tasks.map(task => ({
                        key: task.id,
                        data: [
                            task.title,
                            <span key="desc" className="max-w-xs truncate block">{task.description || 'No description'}</span>,
                            task.sprint_name || 'N/A',
                            task.updated_at ? new Date(task.updated_at).toLocaleDateString() : 'N/A',
                            <Button
                                key="delete"
                                onClick={() => handleDeleteTask(task.id)}
                                variant="outline"
                                size="sm"
                                className="text-red-600 hover:text-red-800"
                            >
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        ]
                    }))}
                    className="shadow-lg"
                />
            )}
        </div>
    );
}