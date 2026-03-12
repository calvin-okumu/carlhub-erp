import React, { useMemo, useState } from 'react';
import KanbanTaskCard from './KanbanTaskCard';
import type { Task } from '@/api/types';

interface KanbanColumnProps {
    title: string;
    tasks: Task[];
    color: string;
    onTaskClick: (task: Task) => void;
    onStatusChange: (taskSlug: string, newStatus: string) => void;
    onQuickAdd: (title: string) => void;
    selectedTaskIds: Set<string>;
    onToggleSelect: (task: Task, checked: boolean) => void;
}

export default function KanbanColumn({ title, tasks, color, onTaskClick, onStatusChange, onQuickAdd, selectedTaskIds, onToggleSelect }: KanbanColumnProps) {
    const [quickTitle, setQuickTitle] = useState('');
    const [collapsedGroups, setCollapsedGroups] = useState<Record<string, boolean>>({});
    const [searchValue, setSearchValue] = useState('');
    const [visibleCounts, setVisibleCounts] = useState<Record<string, number>>({});

    const groupedTasks = useMemo(() => {
        const filtered = searchValue
            ? tasks.filter((task) =>
                task.title.toLowerCase().includes(searchValue.toLowerCase()) ||
                (task.description || '').toLowerCase().includes(searchValue.toLowerCase())
            )
            : tasks;
        return filtered.reduce((acc, task) => {
            const key = task.milestone_name || 'Unassigned';
            if (!acc[key]) acc[key] = [];
            acc[key].push(task);
            return acc;
        }, {} as Record<string, Task[]>);
    }, [tasks, searchValue]);

    const handleQuickAdd = (event: React.FormEvent) => {
        event.preventDefault();
        const trimmed = quickTitle.trim();
        if (!trimmed) return;
        onQuickAdd(trimmed);
        setQuickTitle('');
    };

    const toggleGroup = (group: string) => {
        setCollapsedGroups((prev) => ({ ...prev, [group]: !prev[group] }));
    };

    const getVisibleCount = (group: string) => visibleCounts[group] || 20;
    const handleLoadMore = (group: string) => {
        setVisibleCounts((prev) => ({ ...prev, [group]: getVisibleCount(group) + 20 }));
    };

    return (
         <div className="flex h-full flex-col rounded-2xl border border-slate-200/70 bg-white/90 shadow-sm">
            <div className="sticky top-0 z-10 rounded-t-2xl border-b border-slate-200/70 bg-white/95 px-4 py-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
                        <h2 className="text-sm font-semibold text-slate-800">{title}</h2>
                    </div>
                    <span className="rounded-full border border-slate-200/70 bg-white px-2 py-0.5 text-xs font-semibold text-slate-500">
                        {tasks.length}
                    </span>
                </div>
                <form onSubmit={handleQuickAdd} className="mt-3 flex items-center gap-2">
                    <input
                        type="text"
                        value={quickTitle}
                        onChange={(event) => setQuickTitle(event.target.value)}
                        placeholder="Quick add"
                        className="w-full rounded-lg border border-slate-200/70 bg-white px-3 py-2 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-200"
                    />
                    <button
                        type="submit"
                        className="rounded-lg border border-slate-200/70 bg-white px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500 hover:border-slate-300"
                    >
                        Add
                    </button>
                </form>
                <input
                    type="text"
                    value={searchValue}
                    onChange={(event) => setSearchValue(event.target.value)}
                    placeholder="Search in column"
                    className="mt-3 w-full rounded-lg border border-slate-200/70 bg-slate-50 px-3 py-2 text-xs text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-200"
                />
            </div>
            <div className="flex-1 space-y-4 overflow-y-auto px-4 py-4">
                {Object.entries(groupedTasks).map(([group, groupTasks]) => {
                    const isCollapsed = collapsedGroups[group];
                    const visibleCount = getVisibleCount(group);
                    const visibleTasks = groupTasks.slice(0, visibleCount);
                    return (
                        <div key={group} className="space-y-3">
                            <button
                                type="button"
                                onClick={() => toggleGroup(group)}
                                className="flex w-full items-center justify-between rounded-lg border border-slate-200/70 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-600"
                            >
                                <span className="truncate">{group}</span>
                                <span className="rounded-full border border-slate-200/70 bg-white px-2 py-0.5 text-[10px] text-slate-500">
                                    {groupTasks.length}
                                </span>
                            </button>
                            {!isCollapsed && (
                                <div className="space-y-2">
                                    {visibleTasks.map(task => (
                                        <KanbanTaskCard
                                            key={task.id}
                                            task={task}
                                            onClick={() => onTaskClick(task)}
                                            onStatusChange={onStatusChange}
                                            isSelected={selectedTaskIds.has(task.slug)}
                                            onSelect={(checked) => onToggleSelect(task, checked)}
                                        />
                                    ))}
                                    {groupTasks.length > visibleCount && (
                                        <button
                                            type="button"
                                            onClick={() => handleLoadMore(group)}
                                            className="w-full rounded-lg border border-slate-200/70 bg-white px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500"
                                        >
                                            Load more
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
                {tasks.length === 0 && (
                    <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/70 px-4 py-8 text-center text-xs text-slate-500">
                        No tasks yet
                    </div>
                )}
            </div>
        </div>
    );
}
