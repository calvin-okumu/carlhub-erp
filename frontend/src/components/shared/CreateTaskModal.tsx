"use client";

import type { Milestone, Sprint, Task, UserTenant } from '@/api/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Modal from '@/components/ui/Modal';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';

// Utility function to format dates for HTML date inputs (YYYY-MM-DD format)
function formatDateForInput(dateString: string | undefined): string {
    if (!dateString) return '';
    const trimmed = dateString.slice(0, 10);
    if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
        return trimmed;
    }
    try {
        // Handle various date formats by extracting YYYY-MM-DD
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '';
        return date.toISOString().split('T')[0]; // Returns YYYY-MM-DD
    } catch {
        return '';
    }
}

function getLatestDate(dates: string[]): string {
    return dates.reduce((latest, date) => (date > latest ? date : latest), dates[0]);
}

function getEarliestDate(dates: string[]): string {
    return dates.reduce((earliest, date) => (date < earliest ? date : earliest), dates[0]);
}

function buildDateRange(options: {
    projectStart: string;
    projectEnd: string;
    milestoneStart?: string;
    milestoneEnd?: string;
    sprintStart?: string;
    sprintEnd?: string;
    preferSprint: boolean;
}) {
    const sprintRange = {
        min: options.sprintStart || '',
        max: options.sprintEnd || ''
    };
    const milestoneRange = {
        min: options.milestoneStart || '',
        max: options.milestoneEnd || ''
    };
    const projectRange = {
        min: options.projectStart || '',
        max: options.projectEnd || ''
    };

    if (options.preferSprint && (sprintRange.min || sprintRange.max)) {
        return sprintRange;
    }

    if (milestoneRange.min || milestoneRange.max) {
        return milestoneRange;
    }

    return projectRange;
}

interface CreateTaskModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'add' | 'edit';
    task?: Task;
    sprints: Sprint[];
    assignees: UserTenant[];
    milestones: Milestone[];
    projectStartDate?: string;
    projectEndDate?: string;
    onSave: (data: {
        title: string;
        description?: string;
        status: string;
        milestone: string;
        sprint?: string;
        assignee?: number;
        start_date?: string;
        end_date?: string;
        estimated_hours?: number;
    }) => void;
    defaultSprintId?: string; // For pre-filling sprint in Kanban
    isBacklog?: boolean; // To simplify fields for backlog
    isKanban?: boolean; // Hide milestone/sprint fields and auto-set them
    sprintContext?: Sprint; // Sprint object for kanban context
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

export default function CreateTaskModal({ isOpen, onClose, mode, task, sprints, assignees, milestones, projectStartDate, projectEndDate, onSave, defaultSprintId, isBacklog = false, isKanban = false, sprintContext }: CreateTaskModalProps) {
    const { register, handleSubmit, setValue, watch, getValues, setError, formState: { errors } } = useForm<FormData>({
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
    const watchedMilestone = watch('milestone');
    const watchedStartDate = watch('start_date');
    const watchedEndDate = watch('end_date');

    const projectStart = formatDateForInput(projectStartDate);
    const projectEnd = formatDateForInput(projectEndDate);

    useEffect(() => {
        if (!isOpen) return;

        if (isKanban && sprintContext) {
            const milestone = milestones.find(milestone => milestone.id === sprintContext.milestone || milestone.slug === sprintContext.milestone);
            const { min, max } = buildDateRange({
                projectStart,
                projectEnd,
                milestoneStart: formatDateForInput(milestone?.planned_start),
                milestoneEnd: formatDateForInput(milestone?.due_date),
                sprintStart: formatDateForInput(sprintContext.start_date),
                sprintEnd: formatDateForInput(sprintContext.end_date),
                preferSprint: true
            });
            setMinDate(min);
            setMaxDate(max);
            return;
        }

        if (isBacklog) {
            const milestone = milestones.find(milestone => milestone.id === watchedMilestone || milestone.slug === watchedMilestone);
            const { min, max } = buildDateRange({
                projectStart,
                projectEnd,
                milestoneStart: formatDateForInput(milestone?.planned_start),
                milestoneEnd: formatDateForInput(milestone?.due_date),
                preferSprint: false
            });
            setMinDate(min);
            setMaxDate(max);
            return;
        }

        const sprint = sprints.find(sprintItem => sprintItem.slug === watchedSprint || sprintItem.id === watchedSprint);
        const milestoneId = sprint?.milestone || watchedMilestone;
        const milestone = milestones.find(milestoneItem => milestoneItem.id === milestoneId || milestoneItem.slug === milestoneId);
        const { min, max } = buildDateRange({
            projectStart,
            projectEnd,
            milestoneStart: formatDateForInput(milestone?.planned_start),
            milestoneEnd: formatDateForInput(milestone?.due_date),
            sprintStart: formatDateForInput(sprint?.start_date),
            sprintEnd: formatDateForInput(sprint?.end_date),
            preferSprint: Boolean(sprint)
        });
        setMinDate(min);
        setMaxDate(max);
    }, [watchedSprint, watchedMilestone, milestones, sprints, sprintContext, isBacklog, isKanban, isOpen, projectStart, projectEnd]);

    const startMax = (() => {
        const candidates = [maxDate, watchedEndDate].filter(Boolean) as string[];
        return candidates.length > 0 ? getEarliestDate(candidates) : '';
    })();

    const endMin = (() => {
        const candidates = [minDate, watchedStartDate].filter(Boolean) as string[];
        return candidates.length > 0 ? getLatestDate(candidates) : '';
    })();

    const onSubmit = (data: FormData) => {
        let milestoneId: string;
        let sprintId: string | undefined;

        if (isKanban && sprintContext) {
            // In kanban mode, auto-set milestone and sprint from context
            const normalize = (value: string | undefined) => (value || '').trim().toLowerCase();
            const sprintMilestoneRaw = sprintContext.milestone || '';
            const sprintMilestoneValue = sprintContext.milestone_name || sprintMilestoneRaw;
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
            const fallbackSlug = sprintContext.milestone && /^[a-z0-9-]+$/.test(sprintContext.milestone)
                ? sprintContext.milestone
                : '';
            milestoneId = milestoneMatch?.slug || fallbackSlug || '';
            if (!milestoneId) {
                setError('milestone', { type: 'manual', message: 'Milestone data is missing. Please reload the sprint and try again.' });
                return;
            }
            sprintId = sprintContext.slug;
        } else if (data.sprint) {
            // If sprint is selected, use the sprint's milestone
            const sprint = Array.isArray(sprints) ? sprints.find(s => s.slug === data.sprint) : null;
            if (!sprint) return;
            const milestone = milestones.find(m => m.id === sprint.milestone);
            milestoneId = milestone?.slug || '';
            sprintId = sprint.slug;
        } else {
            // For backlog tasks or tasks without sprint, use selected milestone
            const milestone = milestones.find(m => m.id === data.milestone);
            milestoneId = milestone?.slug || '';
        }

        // Find sprint object to get the ID (only for non-kanban mode)
        if (!isKanban && data.sprint) {
            const sprintObj = Array.isArray(sprints) ? sprints.find(s => s.slug === data.sprint) : null;
            sprintId = sprintObj?.id;
        }

        const saveData = {
            title: data.title,
            description: data.description || undefined,
            status: data.status,
            milestone: milestoneId,
            ...(sprintId && { sprint: sprintId }),
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
            setValue('milestone', task.milestone || '');
            setValue('sprint', task.sprint || '');
            setValue('assignee', task.assignee?.toString() || '');
            setValue('start_date', formatDateForInput(task.start_date) || '');
            setValue('end_date', formatDateForInput(task.end_date) || '');
            setValue('estimated_hours', task.estimated_hours?.toString() || '');
        } else {
            setValue('title', '');
            setValue('description', '');
            setValue('status', 'to_do');
            setValue('milestone', '');
            setValue('priority', 'medium');
            setValue('sprint', defaultSprintId?.toString() || '');
            setValue('assignee', '');
            setValue('start_date', '');
            setValue('end_date', '');
            setValue('estimated_hours', '');
        }
    }, [mode, task, isOpen, sprints, defaultSprintId, setValue]);





    return (
        <Modal isOpen={isOpen} onClose={onClose} title={mode === 'add' ? 'Add Task' : 'Edit Task'} size="md">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                {errors.milestone && isKanban && (
                    <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                        {errors.milestone.message}
                    </p>
                )}
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
                {!isKanban && milestones && Array.isArray(milestones) && (
                    <div>
                        <label htmlFor="milestone" className="block text-sm font-medium text-gray-700">Milestone</label>
                        <Select
                            id="milestone"
                            {...register('milestone', { required: !isKanban && 'Milestone is required' })}
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
                {!isBacklog && !isKanban && (
                    <div>
                        <label htmlFor="sprint" className="block text-sm font-medium text-gray-700">Sprint</label>
                        <Select
                            id="sprint"
                            {...register('sprint', { required: !isKanban && 'Sprint is required' })}
                        >
                            <option value="">Select Sprint</option>
                            {Array.isArray(sprints) && sprints.map(sprint => (
                                <option key={sprint.slug} value={sprint.slug}>
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
                                required: watchedMilestone ? 'Start date is required.' : false,
                                validate: value => {
                                    if (minDate && value && value < minDate) {
                                        return 'Task start date must be on or after the allowed start date.';
                                    }
                                    if (maxDate && value && value > maxDate) {
                                        return 'Task start date must be on or before the allowed end date.';
                                    }
                                    const endDate = getValues('end_date');
                                    if (endDate && value && value > endDate) {
                                        return 'Start date must be on or before end date.';
                                    }
                                    return true;
                                }
                            })}
                            min={minDate || undefined}
                            max={startMax || undefined}
                            className={errors.start_date ? 'border-red-500' : ''}
                        />
                        {errors.start_date && <p className="text-red-500 text-sm mt-1">{errors.start_date.message}</p>}
                        {(minDate || maxDate) && (
                            <p className="text-xs text-gray-500 mt-1">
                                Allowed range: {minDate || 'No minimum'} to {maxDate || 'No maximum'}
                            </p>
                        )}
                    </div>
                    <div>
                        <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">End Date</label>
                        <Input
                            type="date"
                            id="end_date"
                            {...register('end_date', {
                                required: watchedMilestone ? 'End date is required.' : false,
                                validate: value => {
                                    if (minDate && value && value < minDate) {
                                        return 'Task end date must be on or after the allowed start date.';
                                    }
                                    if (maxDate && value && value > maxDate) {
                                        return 'Task end date must be on or before the allowed end date.';
                                    }
                                    const startDate = getValues('start_date');
                                    if (startDate && value && value < startDate) {
                                        return 'End date must be on or after start date.';
                                    }
                                    return true;
                                }
                            })}
                            min={endMin || undefined}
                            max={maxDate || undefined}
                            className={errors.end_date ? 'border-red-500' : ''}
                        />
                        {errors.end_date && <p className="text-red-500 text-sm mt-1">{errors.end_date.message}</p>}
                        {(minDate || maxDate) && (
                            <p className="text-xs text-gray-500 mt-1">
                                Allowed range: {minDate || 'No minimum'} to {maxDate || 'No maximum'}
                            </p>
                        )}
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
                    <Button type="button" onClick={onClose} variant='secondary'>
                        Cancel
                    </Button>
                    <Button type="submit">
                        {mode === 'add' ? 'Add Task' : 'Update Task'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};
