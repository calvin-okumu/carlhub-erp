"use client";

import { getMilestones } from '@/api/project_mgmt';
import type { Milestone, Sprint } from '@/api/types';
import SearchInput from '@/components/shared/SearchInput';
import Button from '@/components/ui/Button';
import { useProject } from '@/context/ProjectContext';
import { useSprints } from '@/hooks/useSprints';
import { Plus } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import SprintModal from './SprintModal';
import SprintTable from './SprintTable';

interface SprintSectionProps {
    milestoneSlug?: string;
    embedded?: boolean;
}

export default function SprintSection({ milestoneSlug, embedded = false }: SprintSectionProps) {
    const { project } = useProject();
    const { sprints, loading, error, addSprint, editSprint, removeSprint, refetch } = useSprints(project?.slug ?? '', milestoneSlug);
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedSprint, setSelectedSprint] = useState<Sprint | null>(null);
    const [searchValue, setSearchValue] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('all');
    const [milestones, setMilestones] = useState<Milestone[]>([]);

    const summary = useMemo(() => {
        const total = sprints.length;
        const active = sprints.filter((sprint) => sprint.status === 'active').length;
        const planned = sprints.filter((sprint) => sprint.status === 'planned').length;
        const completed = sprints.filter((sprint) => sprint.status === 'completed').length;
        const totalTasks = sprints.reduce((count, sprint) => count + (sprint.tasks_count ?? 0), 0);
        const averageProgress = total
            ? Math.round(sprints.reduce((sum, sprint) => sum + (sprint.progress ?? 0), 0) / total)
            : 0;
        return {
            total,
            active,
            planned,
            completed,
            totalTasks,
            averageProgress,
        };
    }, [sprints]);

    const filteredCount = useMemo(() => {
        return sprints.filter(
            (sprint) =>
                sprint.name.toLowerCase().includes(searchValue.toLowerCase()) &&
                (statusFilter === 'all' || sprint.status === statusFilter)
        ).length;
    }, [sprints, searchValue, statusFilter]);

    useEffect(() => {
        const fetchMilestones = async () => {
            const token = localStorage.getItem('access_token');
            if (!token) return;

            try {
                const data = await getMilestones(token, { projectSlug: project?.slug });
                const results = data.results;
                if (milestoneSlug) {
                    setMilestones(results.filter((milestone) => milestone.slug === milestoneSlug));
                } else {
                    setMilestones(results);
                }
            } catch (err) {
                console.error('Failed to fetch milestones:', err);
            }
        };

        fetchMilestones();
    }, [project?.slug, milestoneSlug]);

    const handleAddSprint = () => {
        setModalMode('add');
        setSelectedSprint(null);
        setModalOpen(true);
    };



    const handleEditSprint = (sprint: Sprint) => {
        setModalMode('edit');
        setSelectedSprint(sprint);
        setModalOpen(true);
    };

    const handleDelete = async (slug: string) => {
        if (confirm("Are you sure you want to delete this sprint?")) {
            await removeSprint(slug);
        }
    };

    const handleSaveSprint = async (data: {
        name: string;
        status: string;
        start_date?: string;
        end_date?: string;
        milestone: string;
    }) => {
        try {
            if (modalMode === 'add') {
                await addSprint(data);
            } else if (selectedSprint) {
                await editSprint(selectedSprint.slug, data);
            }
            setModalOpen(false);
        } catch (error) {
            console.error('Error saving sprint:', error);
            // TODO: Show error message
        }
    };



    return (
        <div className="space-y-6">
            {!embedded && (
            <section className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="min-w-[240px] flex-1 space-y-1">
                        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Project Sprints</p>
                        <h2 className="text-lg font-semibold text-slate-900">Sprint Delivery Hub</h2>
                        <p className="text-xs text-slate-500">
                            {milestoneSlug
                                ? "Sprints tied to this milestone."
                                : "Monitor cadence, track progress, and open Kanban boards per sprint."}
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <Button onClick={handleAddSprint}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Sprint
                        </Button>
                    </div>
                </div>

                <div className="mt-3 grid gap-3 xl:grid-cols-[minmax(0,260px)_minmax(0,1fr)]">
                    <div className="space-y-3 rounded-xl border border-slate-200/70 bg-slate-50/70 p-3">
                        <div className="space-y-2">
                            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Filters</p>
                            <SearchInput
                                value={searchValue}
                                onChange={setSearchValue}
                                placeholder="Search sprint names..."
                            />
                        </div>
                        <div className="rounded-xl border border-slate-200/70 bg-white px-3 py-2 text-[11px] text-slate-500">
                            Showing <span className="font-semibold text-slate-900">{filteredCount}</span> of {summary.total} sprints
                        </div>
                    </div>
                    <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-4">
                        {[
                            {
                                key: 'all',
                                label: 'Total Sprints',
                                value: summary.total,
                                note: `${summary.totalTasks} tasks tracked`,
                                tag: 'All',
                            },
                            {
                                key: 'active',
                                label: 'Active',
                                value: summary.active,
                                note: `${summary.planned} planned next`,
                                tag: 'In flight',
                            },
                            {
                                key: 'completed',
                                label: 'Completed',
                                value: summary.completed,
                                note: `Avg ${summary.averageProgress}% progress`,
                                tag: 'Done',
                            },
                            {
                                key: 'planned',
                                label: 'In Planning',
                                value: summary.planned,
                                note: 'Keep backlog ready',
                                tag: 'Queued',
                            },
                        ].map((item) => {
                            const isActive = statusFilter === item.key;
                            return (
                                <button
                                    key={item.key}
                                    type="button"
                                    onClick={() => setStatusFilter(item.key)}
                                    className={`rounded-2xl border p-2.5 text-left shadow-sm transition-all ${
                                        isActive
                                            ? 'border-slate-900 bg-slate-900 text-white'
                                            : 'border-slate-200/70 bg-white/90 text-slate-900 hover:-translate-y-0.5 hover:border-slate-300'
                                    }`}
                                >
                                    <p className={`text-xs font-semibold uppercase tracking-wider ${isActive ? 'text-white/70' : 'text-slate-400'}`}>
                                        {item.label}
                                    </p>
                                    <div className="mt-1 flex items-baseline justify-between">
                                        <span className="text-2xl font-semibold">{item.value}</span>
                                        <span className={`text-xs font-medium ${isActive ? 'text-white/70' : 'text-slate-500'}`}>
                                            {item.tag}
                                        </span>
                                    </div>
                                    <p className={`mt-1 text-[11px] ${isActive ? 'text-white/70' : 'text-slate-500'}`}>{item.note}</p>
                                </button>
                            );
                        })}
                    </div>
                </div>
            </section>
            )}
            {embedded && (
                <section className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Milestone Sprints</p>
                            <h2 className="text-lg font-semibold text-slate-900">Sprint Delivery Hub</h2>
                        </div>
                        <Button onClick={handleAddSprint}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Sprint
                        </Button>
                    </div>
                    <div className="mt-4 grid gap-3 lg:grid-cols-[minmax(0,260px)_minmax(0,1fr)]">
                        <div className="space-y-3 rounded-xl border border-slate-200/70 bg-slate-50/70 p-3">
                            <div className="space-y-2">
                                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Filters</p>
                                <SearchInput
                                    value={searchValue}
                                    onChange={setSearchValue}
                                    placeholder="Search sprint names..."
                                />
                            </div>
                            <div className="rounded-xl border border-slate-200/70 bg-white px-3 py-2 text-[11px] text-slate-500">
                                Showing <span className="font-semibold text-slate-900">{filteredCount}</span> of {summary.total} sprints
                            </div>
                        </div>
                    <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
                        {[
                            { key: 'all', label: 'Total', value: summary.total, tag: 'All' },
                            { key: 'active', label: 'Active', value: summary.active, tag: 'In flight' },
                            { key: 'completed', label: 'Completed', value: summary.completed, tag: 'Done' },
                            { key: 'planned', label: 'Planned', value: summary.planned, tag: 'Queued' },
                        ].map((item) => {
                            const isActive = statusFilter === item.key;
                            return (
                                <button
                                    key={item.key}
                                    type="button"
                                    onClick={() => setStatusFilter(item.key)}
                                    className={`rounded-2xl border p-2.5 text-left shadow-sm transition-all ${
                                        isActive
                                            ? 'border-slate-900 bg-slate-900 text-white'
                                            : 'border-slate-200/70 bg-white/90 text-slate-900 hover:-translate-y-0.5 hover:border-slate-300'
                                    }`}
                                >
                                    <p className={`text-xs font-semibold uppercase tracking-wider ${isActive ? 'text-white/70' : 'text-slate-400'}`}>
                                        {item.label}
                                    </p>
                                    <div className="mt-1 flex items-baseline justify-between">
                                        <span className="text-2xl font-semibold">{item.value}</span>
                                        <span className={`text-xs font-medium ${isActive ? 'text-white/70' : 'text-slate-500'}`}>
                                            {item.tag}
                                        </span>
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                    </div>
                </section>
            )}
            <SprintTable
                sprints={sprints}
                loading={loading}
                error={error}
                onEditSprint={handleEditSprint}
                onDeleteSprint={handleDelete}
                onAddSprint={handleAddSprint}
                projectSlug={project?.slug || ''}
                searchValue={searchValue}
                statusFilter={statusFilter}
                onSprintUpdated={refetch}
            />
            <SprintModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                mode={modalMode}
                sprint={selectedSprint || undefined}
                milestones={milestones}
                defaultMilestoneSlug={milestoneSlug}
                onSave={handleSaveSprint}
            />
        </div>
    );
};
