import React from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import type { Task } from '@/api/types';

interface KanbanTaskCardProps {
    task: Task;
    onClick: () => void;
    onStatusChange: (taskSlug: string, newStatus: string) => void;
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

export default function KanbanTaskCard({ task, onClick, onStatusChange }: KanbanTaskCardProps) {
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
        <Card className="mb-3 cursor-pointer hover:shadow-md transition-shadow" onClick={onClick}>
            <div className="p-3">
                <h3 className="font-medium text-gray-900 mb-2">{task.title}</h3>
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">{task.description}</p>
                <div className="flex justify-between items-center mb-2">
                    <PriorityBadge priority={task.priority} />
                    <div className="text-xs text-gray-500">
                        {task.assignee && <span>Assigned to: {task.assignee}</span>}
                        {task.estimated_hours && <span className="ml-2">{task.estimated_hours}h</span>}
                    </div>
                </div>
                <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-gray-600">
                        Progress: {task.progress}%
                    </span>
                    <div className="w-16 h-1 bg-gray-200 rounded">
                        <div
                            className={`h-1 rounded transition-all duration-300 ${
                                task.progress === 100 ? 'bg-green-500' : 'bg-blue-500'
                            }`}
                            style={{ width: `${task.progress}%` }}
                        />
                    </div>
                </div>
                {nextStatuses.length > 0 && (
                    <div className="flex gap-1 mt-2" onClick={(e) => e.stopPropagation()}>
                        {nextStatuses.map(status => (
                             <Button
                                 key={status}
                                 onClick={() => onStatusChange(task.slug, status)}
                                 variant="outline"
                                 size="sm"
                                 className={`text-xs px-2 py-1 ${getButtonColor(status)}`}
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