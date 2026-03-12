import React, { useState } from 'react';
import KanbanTaskCard from './KanbanTaskCard';
import type { Task } from '@/api/types';

interface KanbanColumnProps {
    title: string;
    tasks: Task[];
    color: string;
    onTaskClick: (task: Task) => void;
    onStatusChange: (taskSlug: string, newStatus: string) => void;
    onQuickAdd: (title: string) => void;
}

export default function KanbanColumn({ title, tasks, color, onTaskClick, onStatusChange, onQuickAdd }: KanbanColumnProps) {
    const [quickTitle, setQuickTitle] = useState('');

    const handleQuickAdd = (event: React.FormEvent) => {
        event.preventDefault();
        const trimmed = quickTitle.trim();
        if (!trimmed) return;
        onQuickAdd(trimmed);
        setQuickTitle('');
    };

    return (
         <div className={`${color} rounded-lg p-4 h-full`}>
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center justify-between">
                {title}
                <span className="text-sm text-gray-500 bg-white px-2 py-1 rounded">
                    {tasks.length}
                </span>
            </h2>
            <form onSubmit={handleQuickAdd} className="mb-4 flex items-center gap-2">
                <input
                    type="text"
                    value={quickTitle}
                    onChange={(event) => setQuickTitle(event.target.value)}
                    placeholder="Quick add"
                    className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-200"
                />
                <button
                    type="submit"
                    className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-gray-500 hover:border-gray-300"
                >
                    Add
                </button>
            </form>
            <div className="space-y-3 min-h-[400px]">
                 {tasks.map(task => (
                     <KanbanTaskCard key={task.id} task={task} onClick={() => onTaskClick(task)} onStatusChange={onStatusChange} />
                 ))}
                {tasks.length === 0 && (
                    <div className="rounded-lg border border-dashed border-gray-300 bg-white/70 px-4 py-8 text-center text-sm text-gray-500 shadow-sm">
                        No tasks yet
                    </div>
                )}
            </div>
        </div>
    );
}
