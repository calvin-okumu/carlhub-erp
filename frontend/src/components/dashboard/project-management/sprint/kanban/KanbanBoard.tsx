import React from 'react';
import KanbanColumn from './KanbanColumn';
import type { Task } from '@/api/types';

interface KanbanBoardProps {
    tasks: Task[];
    onTaskClick: (task: Task) => void;
    onStatusChange: (taskSlug: string, newStatus: string) => void;
    onQuickAdd: (status: string, title: string) => void;
    selectedTaskIds: Set<string>;
    onToggleSelect: (task: Task, checked: boolean) => void;
}

export default function KanbanBoard({ tasks, onTaskClick, onStatusChange, onQuickAdd, selectedTaskIds, onToggleSelect }: KanbanBoardProps) {
       const columns = [
            { id: 'to_do', title: 'To Do', status: 'to_do' },
            { id: 'in_progress', title: 'In Progress', status: 'in_progress' },
            { id: 'in_review', title: 'Review', status: 'in_review' },
            { id: 'testing', title: 'Testing', status: 'testing' }
        ];

       const colorMap: Record<string, string> = {
            to_do: 'bg-slate-300',
            in_progress: 'bg-pink-400',
            in_review: 'bg-blue-400',
            testing: 'bg-emerald-400'
        };

      const tasksByStatus = columns.reduce((acc, column) => {
          acc[column.id] = tasks.filter(task => task.status === column.status);
          return acc;
      }, {} as Record<string, Task[]>);

      return (
            <div className="grid gap-4 pb-4 sm:grid-cols-2 xl:grid-cols-4">
              {columns.map(column => (
                    <KanbanColumn
                        key={column.id}
                        title={column.title}
                        tasks={tasksByStatus[column.id]}
                        color={colorMap[column.status]}
                        onTaskClick={onTaskClick}
                        onStatusChange={onStatusChange}
                        onQuickAdd={(title) => onQuickAdd(column.status, title)}
                        selectedTaskIds={selectedTaskIds}
                        onToggleSelect={onToggleSelect}
                    />
               ))}
          </div>
      );
}
