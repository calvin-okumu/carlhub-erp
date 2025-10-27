import React from 'react';
import KanbanTaskCard from './KanbanTaskCard';
import type { Task } from '@/api/types';

interface KanbanColumnProps {
    title: string;
    tasks: Task[];
    color: string;
    onTaskClick: (task: Task) => void;
    onStatusChange: (taskSlug: string, newStatus: string) => void;
}

export default function KanbanColumn({ title, tasks, color, onTaskClick, onStatusChange }: KanbanColumnProps) {
    return (
         <div className={`${color} rounded-lg p-4 h-full`}>
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center justify-between">
                {title}
                <span className="text-sm text-gray-500 bg-white px-2 py-1 rounded">
                    {tasks.length}
                </span>
            </h2>
            <div className="space-y-3 min-h-[400px]">
                 {tasks.map(task => (
                     <KanbanTaskCard key={task.id} task={task} onClick={() => onTaskClick(task)} onStatusChange={onStatusChange} />
                 ))}
                {tasks.length === 0 && (
                    <div className="text-gray-400 text-sm text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
                        No tasks
                    </div>
                )}
            </div>
        </div>
    );
}