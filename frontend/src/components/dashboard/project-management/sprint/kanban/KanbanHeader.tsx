import React from 'react';
import { ArrowLeft } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import type { Sprint } from '@/api/types';

interface KanbanHeaderProps {
    sprint: Sprint;
    onBack: () => void;
    isModal?: boolean;
}

const StatusBadge = ({ status }: { status: string }) => {
    const styles: Record<string, string> = {
        active: 'bg-blue-100 text-blue-700 border-blue-200',
        planned: 'bg-yellow-100 text-yellow-700 border-yellow-200',
        completed: 'bg-green-100 text-green-700 border-green-200'
    };

    return (
        <span className={`px-3 py-1 rounded-md text-xs font-medium border ${styles[status] || styles.planned}`}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
    );
};

export default function KanbanHeader({ sprint, onBack, isModal = false }: KanbanHeaderProps) {
    return (
        <Card className="mb-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <h1 className="text-2xl font-bold text-gray-900">{sprint.name}</h1>
                    <StatusBadge status={sprint.status} />
                    <span className="text-sm text-gray-600">Progress: {sprint.progress}%</span>
                </div>

                {!isModal && (
                    <Button onClick={onBack} variant="outline">
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Back to Sprints
                    </Button>
                )}
            </div>
        </Card>
    );
}