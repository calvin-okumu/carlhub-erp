"use client";

import { getUserTenants } from '@/api/crm';
import type { Milestone, UserTenant } from '@/api/types';
import SearchInput from '@/components/shared/SearchInput';
import Button from '@/components/ui/Button';
import { useProject } from '@/context/ProjectContext';
import { useMilestones } from '@/hooks/useMilestones';
import { Plus } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import MilestoneModal from './MilestoneModal';
import MilestoneTable from './MilestoneTable';

export default function MilestoneSection() {
    const { project } = useProject();
    const { milestones, loading, error, addMilestone, editMilestone, removeMilestone } = useMilestones(project?.slug ?? '');
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedMilestone, setSelectedMilestone] = useState<Milestone | null>(null);
    const [searchValue, setSearchValue] = useState('');
    const [statusFilter, setStatusFilter] = useState<'all' | 'planning' | 'active' | 'completed'>('all');
    const [users, setUsers] = useState<UserTenant[]>([]);

    useEffect(() => {
        const fetchUsers = async () => {
            const token = localStorage.getItem('access_token');
            if (!token) return;

            try {
                const data = await getUserTenants(token);
                setUsers(data);
            } catch (err) {
                console.error('Failed to fetch users:', err);
            }
        };

        fetchUsers();
    }, []);

    const handleAddMilestone = () => {
        setModalMode('add');
        setSelectedMilestone(null);
        setModalOpen(true);
    };

    const handleEditMilestone = (milestone: Milestone) => {
        setModalMode('edit');
        setSelectedMilestone(milestone);
        setModalOpen(true);
    };

    const handleSaveMilestone = async (data: {
        name: string;
        description?: string;
        status: string;
        planned_start?: string;
        actual_start?: string;
        due_date?: string;
        assignee?: number;
        project: string;
    }) => {
        try {
            if (modalMode === 'add') {
                await addMilestone(data);
            } else if (selectedMilestone) {
                await editMilestone(selectedMilestone.slug, data);
            }
            setModalOpen(false);
        } catch (error) {
            console.error('Error saving milestone:', error);
            // TODO: Show error message
        }
    };

    const milestoneStats = useMemo(() => {
        const counts = milestones.reduce(
            (acc, milestone) => {
                acc.total += 1;
                if (milestone.status === 'completed') acc.completed += 1;
                if (milestone.status === 'active') acc.active += 1;
                if (milestone.status === 'planning') acc.planning += 1;
                acc.progressTotal += milestone.progress || 0;
                if (milestone.due_date && milestone.status !== 'completed') {
                    const due = new Date(milestone.due_date).getTime();
                    if (due < Date.now()) acc.overdue += 1;
                }
                return acc;
            },
            { total: 0, completed: 0, active: 0, planning: 0, overdue: 0, progressTotal: 0 }
        );

        return {
            ...counts,
            averageProgress: counts.total ? Math.round(counts.progressTotal / counts.total) : 0,
        };
    }, [milestones]);

    return (
        <div className="space-y-6">
            <section className="rounded-2xl border border-slate-200/70 bg-white/90 p-6 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="min-w-[240px] flex-1 space-y-2">
                        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Project Milestones</p>
                        <div className="space-y-1">
                            <h1 className="text-2xl font-semibold text-slate-900">Milestone Details</h1>
                            <p className="text-sm text-slate-600">Track progress, dates, and momentum across each milestone.</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <Button onClick={handleAddMilestone}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Milestone
                        </Button>
                    </div>
                </div>

                <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,320px)_minmax(0,1fr)]">
                    <div className="space-y-4 rounded-xl border border-slate-200/70 bg-slate-50/70 p-4">
                        <div className="space-y-2">
                            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Filters</p>
                            <SearchInput
                                value={searchValue}
                                onChange={setSearchValue}
                                placeholder="Search milestones..."
                            />
                        </div>
                    </div>
                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                        {[
                            {
                                key: 'all',
                                label: 'Total',
                                value: milestoneStats.total,
                                note: `Avg. progress ${milestoneStats.averageProgress}%`,
                            },
                            {
                                key: 'active',
                                label: 'Active',
                                value: milestoneStats.active,
                                note: 'In progress',
                            },
                            {
                                key: 'planning',
                                label: 'Planning',
                                value: milestoneStats.planning,
                                note: 'Queued',
                            },
                            {
                                key: 'completed',
                                label: 'Completed',
                                value: milestoneStats.completed,
                                note: `${milestoneStats.overdue} overdue`,
                            },
                        ].map((item) => {
                            const isActive = statusFilter === item.key;
                            return (
                                <button
                                    key={item.key}
                                    type="button"
                                    onClick={() => setStatusFilter(item.key as 'all' | 'planning' | 'active' | 'completed')}
                                    className={`rounded-2xl border p-4 text-left shadow-sm transition-all ${
                                        isActive
                                            ? 'border-slate-900 bg-slate-900 text-white'
                                            : 'border-slate-200/70 bg-white/90 text-slate-900 hover:-translate-y-0.5 hover:border-slate-300'
                                    }`}
                                >
                                    <p className={`text-xs font-semibold uppercase tracking-wider ${isActive ? 'text-white/70' : 'text-slate-400'}`}>
                                        {item.label}
                                    </p>
                                    <div className="mt-3 flex items-baseline justify-between">
                                        <span className="text-2xl font-semibold">{item.value}</span>
                                        <span className={`text-xs font-medium ${isActive ? 'text-white/70' : 'text-slate-500'}`}>
                                            {item.label === 'Total' ? 'Milestones' : item.note}
                                        </span>
                                    </div>
                                    {item.label === 'Total' && (
                                        <div className="mt-4 h-2 rounded-full bg-slate-100">
                                            <div
                                                className={`h-2 rounded-full ${isActive ? 'bg-white/60' : 'bg-blue-500'}`}
                                                style={{ width: `${milestoneStats.averageProgress}%` }}
                                            />
                                        </div>
                                    )}
                                    <p className={`mt-2 text-xs ${isActive ? 'text-white/70' : 'text-slate-500'}`}>
                                        {item.label === 'Total' ? item.note : item.label === 'Completed' ? `${milestoneStats.overdue} overdue` : item.note}
                                    </p>
                                </button>
                            );
                        })}
                    </div>
                </div>
            </section>
            <MilestoneTable
                milestones={statusFilter === 'all'
                    ? milestones
                    : milestones.filter((milestone) => milestone.status === statusFilter)}
                loading={loading}
                error={error}
                onEditMilestone={handleEditMilestone}
                onDeleteMilestone={removeMilestone}
                onAddMilestone={handleAddMilestone}
                searchValue={searchValue}
                projectSlug={project?.slug}
            />
            <MilestoneModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                mode={modalMode}
                milestone={selectedMilestone || undefined}
                projectSlug={project?.slug || ''}
                assignees={users}
                projectStart={project?.start_date}
                projectEnd={project?.end_date}
                onSave={handleSaveMilestone}
            />
        </div>
    );
};
