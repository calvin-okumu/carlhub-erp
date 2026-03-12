import React from 'react';
import { ArrowLeft } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import type { Sprint } from '@/api/types';

interface KanbanHeaderProps {
    sprint: Sprint;
    onBack: () => void;
    isModal?: boolean;
    dueSoonOnly?: boolean;
    onToggleDueSoon?: () => void;
}

const StatusBadge = ({ status }: { status: string }) => {
    const styles: Record<string, string> = {
        active: 'bg-blue-100 text-blue-700 border-blue-200',
        planned: 'bg-amber-100 text-amber-700 border-amber-200',
        completed: 'bg-emerald-100 text-emerald-700 border-emerald-200',
        canceled: 'bg-red-100 text-red-700 border-red-200'
    };

    return (
        <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${styles[status] || styles.planned}`}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
    );
};

export default function KanbanHeader({ sprint, onBack, isModal = false, dueSoonOnly = false, onToggleDueSoon }: KanbanHeaderProps) {
    return (
        <Card className="!rounded-2xl !border-slate-200/70 !shadow-sm mb-6 p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <div className="flex flex-wrap items-center gap-3">
                        <h1 className="text-2xl font-semibold text-slate-900">{sprint.name}</h1>
                        <StatusBadge status={sprint.status} />
                        <span className="text-sm text-slate-500">Progress: <span className="font-semibold text-slate-900">{sprint.progress}%</span></span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">Sprint focus board and delivery flow.</p>
                </div>

                <div className="flex items-center gap-2">
                    {onToggleDueSoon && (
                        <button
                            type="button"
                            onClick={onToggleDueSoon}
                            className={`rounded-full border px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] transition-all ${
                                dueSoonOnly
                                    ? 'border-slate-900 bg-slate-900 text-white'
                                    : 'border-slate-200/70 bg-white text-slate-500 hover:border-slate-300'
                            }`}
                        >
                            Due soon
                        </button>
                    )}
                    {!isModal && (
                        <Button onClick={onBack} variant="outline" className="rounded-full">
                            <ArrowLeft className="h-4 w-4 mr-2" />
                            Back to Sprints
                        </Button>
                    )}
                </div>
            </div>
        </Card>
    );
}
