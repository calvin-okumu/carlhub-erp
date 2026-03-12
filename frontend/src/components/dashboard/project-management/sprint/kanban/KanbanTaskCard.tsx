import React from 'react';
import { User } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import type { Task } from '@/api/types';

interface KanbanTaskCardProps {
    task: Task;
    onClick: () => void;
    onStatusChange: (taskSlug: string, newStatus: string) => void;
    isSelected?: boolean;
    onSelect?: (checked: boolean) => void;
}

const PriorityBadge = ({ priority }: { priority: string }) => {
    const styles: Record<string, string> = {
        high: 'bg-red-100 text-red-800',
        medium: 'bg-yellow-100 text-yellow-800',
        low: 'bg-green-100 text-green-800'
    };

    return (
        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${styles[priority] || styles.medium}`}>
            {priority}
        </span>
    );
};

export default function KanbanTaskCard({ task, onClick, onStatusChange, isSelected = false, onSelect }: KanbanTaskCardProps) {
    const formatDueDate = (date?: string) => {
        if (!date) return null;
        const parsed = new Date(date);
        if (Number.isNaN(parsed.getTime())) return null;
        return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(parsed);
    };

    const statusBandStyles: Record<string, string> = {
        done: 'border-l-emerald-500',
        in_progress: 'border-l-pink-500',
        in_review: 'border-l-blue-500',
        testing: 'border-l-green-500',
        to_do: 'border-l-gray-400'
    };

    const getNextStatuses = (currentStatus: string) => {
        const statusFlow: Record<string, string[]> = {
            'to_do': ['in_progress'],
            'in_progress': ['in_review'],
            'in_review': ['testing'],
            'testing': ['done']
        };
        return statusFlow[currentStatus] || [];
    };

    const nextStatuses = getNextStatuses(task.status);
    const dueDate = formatDueDate(task.end_date);

    const getButtonText = (status: string) => {
        if (status === 'in_progress') return 'Move to Progress';
        if (status === 'in_review') return 'Move to Review';
        if (status === 'testing') return 'Move to Testing';
        if (status === 'done') return 'Mark as Done';
        return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    const getButtonColor = (status: string) => {
        const colorMap: Record<string, string> = {
            'in_progress': 'bg-pink-500 hover:bg-pink-600 text-white',
            'in_review': 'bg-blue-500 hover:bg-blue-600 text-white',
            'testing': 'bg-green-500 hover:bg-green-600 text-white',
            'done': 'bg-emerald-500 hover:bg-emerald-600 text-white'
        };
        return colorMap[status] || 'bg-gray-500 hover:bg-gray-600 text-white';
    };
    return (
        <Card
            className={`!p-0 cursor-pointer border-l-4 border-slate-200/70 !shadow-sm rounded-xl transition-shadow hover:shadow-md ${statusBandStyles[task.status] || 'border-l-gray-400'}`}
            onClick={onClick}
        >
            <div className="space-y-2 p-3">
                <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2">
                        {onSelect && (
                            <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={(event) => onSelect(event.target.checked)}
                                onClick={(event) => event.stopPropagation()}
                                className="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-200"
                            />
                        )}
                        <h3 className="text-sm font-semibold text-slate-900 line-clamp-2">{task.title}</h3>
                    </div>
                    {task.assignee && (
                        <span className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-100 text-slate-600">
                            <User className="h-3.5 w-3.5" />
                        </span>
                    )}
                </div>
                {task.description && (
                    <p className="text-xs text-slate-500 line-clamp-2">{task.description}</p>
                )}
                <div className="flex flex-wrap items-center gap-2">
                    <PriorityBadge priority={task.priority} />
                    {dueDate && (
                        <span className="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600">
                            Due {dueDate}
                        </span>
                    )}
                    {task.estimated_hours && (
                        <span className="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600">
                            {task.estimated_hours}h
                        </span>
                    )}
                </div>
                <div className="flex items-center justify-between text-[10px] text-slate-500">
                    <span>{task.progress}%</span>
                    <div className="h-1.5 w-20 rounded-full bg-slate-200">
                        <div
                            className={`h-1.5 rounded-full ${task.progress === 100 ? 'bg-emerald-500' : 'bg-slate-600'}`}
                            style={{ width: `${Math.min(100, Math.max(0, task.progress))}%` }}
                        />
                    </div>
                </div>
                {nextStatuses.length > 0 && (
                    <div className="flex flex-wrap gap-2" onClick={(e) => e.stopPropagation()}>
                        {nextStatuses.map(status => (
                            <Button
                                key={status}
                                onClick={() => onStatusChange(task.slug, status)}
                                variant="outline"
                                size="sm"
                                className={`text-[10px] px-2 py-1 border-transparent ${getButtonColor(status)}`}
                            >
                                {getButtonText(status)}
                            </Button>
                        ))}
                    </div>
                )}
            </div>
        </Card>
    );
}
