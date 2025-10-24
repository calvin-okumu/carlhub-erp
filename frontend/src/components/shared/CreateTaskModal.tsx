"use client";

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import Select from '@/components/ui/Select';
import type { Task, Sprint, UserTenant, Milestone } from '@/api/types';
import { useForm } from 'react-hook-form';

interface CreateTaskModalProps {
     isOpen: boolean;
     onClose: () => void;
     mode: 'add' | 'edit';
     task?: Task;
     sprints: Sprint[];
     assignees: UserTenant[];
     milestones: Milestone[];
     onSave: (data: {
         title: string;
         description?: string;
         status: string;
         milestone: number;
         sprint?: number;
         assignee?: number;
         start_date?: string;
         end_date?: string;
         estimated_hours?: number;
     }) => void;
     defaultSprintId?: number; // For pre-filling sprint in Kanban
     isBacklog?: boolean; // To simplify fields for backlog
 }

type FormData = {
     title: string;
     description: string;
     status: string;
     priority: string;
     sprint: string;
     assignee: string;
     milestone: string;
     start_date: string;
     end_date: string;
     estimated_hours: string;
 };

export default function CreateTaskModal({ isOpen, onClose, mode, task, sprints, assignees, milestones, onSave, defaultSprintId, isBacklog = false }: CreateTaskModalProps) {
     const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<FormData>({
         defaultValues: {
             title: '',
             description: '',
             status: 'to_do',
             priority: 'medium',
             sprint: defaultSprintId?.toString() || '',
             assignee: '',
             milestone: milestones?.[0]?.id?.toString() || '',
             start_date: '',
             end_date: '',
             estimated_hours: '',
         }
     });
    const [minDate, setMinDate] = useState('');
    const [maxDate, setMaxDate] = useState('');

    const watchedSprint = watch('sprint');

    useEffect(() => {
        if (watchedSprint) {
            const sprint = sprints.find(s => s.id.toString() === watchedSprint);
            if (sprint) {
                setMinDate(sprint.start_date || '');
                setMaxDate(sprint.end_date || '');
            }
        } else {
            setMinDate('');
            setMaxDate('');
        }
    }, [watchedSprint, sprints]);

    const onSubmit = (data: FormData) => {
        let milestoneId: number;
        if (isBacklog) {
            milestoneId = parseInt(data.milestone);
        } else {
            if (data.sprint) {
                const sprint = sprints.find(s => s.id === parseInt(data.sprint));
                if (!sprint) return;
                milestoneId = sprint.milestone;
            } else {
                alert('Please select a sprint to assign the milestone.');
                return;
            }
        }

        const saveData = {
            title: data.title,
            description: data.description || undefined,
            status: data.status,
            milestone: milestoneId,
            sprint: data.sprint ? parseInt(data.sprint) : undefined,
            assignee: data.assignee ? parseInt(data.assignee) : undefined,
            start_date: data.start_date || undefined,
            end_date: data.end_date || undefined,
            estimated_hours: data.estimated_hours ? parseFloat(data.estimated_hours) : undefined,
        };

        onSave(saveData);
    };

    useEffect(() => {
        if (mode === 'edit' && task) {
            setValue('title', task.title);
            setValue('description', task.description || '');
            setValue('status', task.status);
            setValue('priority', task.priority || 'medium');
            setValue('sprint', task.sprint?.toString() || '');
            setValue('assignee', task.assignee?.toString() || '');
            setValue('start_date', task.start_date || '');
            setValue('end_date', task.end_date || '');
            setValue('estimated_hours', task.estimated_hours?.toString() || '');
            const sprint = sprints.find(s => s.id === task.sprint);
            if (sprint) {
                setMinDate(sprint.start_date || '');
                setMaxDate(sprint.end_date || '');
            }
        } else {
            setValue('title', '');
            setValue('description', '');
            setValue('status', 'to_do');
            setValue('priority', 'medium');
            setValue('sprint', defaultSprintId?.toString() || '');
            setValue('assignee', '');
            setValue('start_date', '');
            setValue('end_date', '');
            setValue('estimated_hours', '');
            setMinDate('');
            setMaxDate('');
        }
    }, [mode, task, isOpen, sprints, defaultSprintId, setValue]);





    return (
        <Modal isOpen={isOpen} onClose={onClose} title={mode === 'add' ? 'Add Task' : 'Edit Task'} size="md">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700">Title *</label>
                    <Input
                        type="text"
                        id="title"
                        {...register('title', { required: 'Title is required' })}
                    />
                </div>
                <div>
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description</label>
                    <Textarea
                        id="description"
                        {...register('description')}
                        rows={3}
                    />
                </div>
                <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
                            <Select
                                id="status"
                                {...register('status')}
                            >
                                <option value="to_do">To Do</option>
                                <option value="in_progress">In Progress</option>
                                <option value="in_review">Review</option>
                                <option value="testing">Testing</option>
                            </Select>
                        </div>
                        <div>
                            <label htmlFor="priority" className="block text-sm font-medium text-gray-700">Priority</label>
                            <Select
                                id="priority"
                                {...register('priority')}
                            >
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                            </Select>
                        </div>
                 </div>
                  {isBacklog && milestones && Array.isArray(milestones) && (
                      <div>
                          <label htmlFor="milestone" className="block text-sm font-medium text-gray-700">Milestone</label>
                          <Select
                              id="milestone"
                              {...register('milestone', { required: 'Milestone is required' })}
                          >
                              <option value="">Select Milestone</option>
                              {Array.isArray(milestones) && milestones.map(milestone => (
                                  <option key={milestone.id} value={milestone.id}>
                                      {milestone.name}
                                  </option>
                              ))}
                          </Select>
                      </div>
                  )}
                 {!isBacklog && (
                      <div>
                          <label htmlFor="sprint" className="block text-sm font-medium text-gray-700">Sprint</label>
                          <Select
                              id="sprint"
                              {...register('sprint', { required: 'Sprint is required' })}
                          >
                              <option value="">Select Sprint</option>
                              {Array.isArray(sprints) && sprints.map(sprint => (
                                  <option key={sprint.id} value={sprint.id}>
                                      {sprint.name}
                                  </option>
                              ))}
                          </Select>
                      </div>
                 )}
                 {!isBacklog && (
                      <div>
                          <label htmlFor="assignee" className="block text-sm font-medium text-gray-700">Assignee</label>
                          <Select
                              id="assignee"
                              {...register('assignee')}
                          >
                              <option value="">Select Assignee</option>
                              {Array.isArray(assignees) && assignees.map(user => (
                                  <option key={user.user} value={user.user}>
                                      {user.user_first_name} {user.user_last_name}
                                  </option>
                              ))}
                          </Select>
                      </div>
                 )}
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">Start Date</label>
                        <Input
                            type="date"
                            id="start_date"
                            {...register('start_date', {
                                validate: value => {
                                    if (value && minDate && value < minDate) return 'Task start date cannot be before the sprint\'s start date.';
                                    return true;
                                }
                            })}
                            min={minDate}
                            max={maxDate}
                            className={errors.start_date ? 'border-red-500' : ''}
                        />
                        {errors.start_date && <p className="text-red-500 text-sm mt-1">{errors.start_date.message}</p>}
                    </div>
                    <div>
                        <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">End Date</label>
                        <Input
                            type="date"
                            id="end_date"
                            {...register('end_date', {
                                validate: value => {
                                    if (value && maxDate && value > maxDate) return 'Task end date cannot be after the sprint\'s end date.';
                                    return true;
                                }
                            })}
                            min={minDate}
                            max={maxDate}
                            className={errors.end_date ? 'border-red-500' : ''}
                        />
                        {errors.end_date && <p className="text-red-500 text-sm mt-1">{errors.end_date.message}</p>}
                    </div>
                </div>
                 {!isBacklog && (
                      <div>
                          <label htmlFor="estimated_hours" className="block text-sm font-medium text-gray-700">Estimated Hours</label>
                          <Input
                              type="number"
                              id="estimated_hours"
                              {...register('estimated_hours')}
                              min="0"
                          />
                      </div>
                 )}
                <div className="flex justify-end space-x-3 pt-4">
                    <Button type="button" onClick={onClose} variant="outline">
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary">
                        {mode === 'add' ? 'Add Task' : 'Update Task'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};