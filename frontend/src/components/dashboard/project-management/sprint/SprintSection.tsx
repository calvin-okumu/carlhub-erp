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

export default function SprintSection() {
    const { project } = useProject();
    const { sprints, loading, error, addSprint, editSprint, removeSprint } = useSprints(project?.slug ?? '');
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
                setMilestones(data.results);
            } catch (err) {
                console.error('Failed to fetch milestones:', err);
            }
        };

        fetchMilestones();
    }, [project?.slug]);

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
            <section className="rounded-2xl border border-slate-200/70 bg-white/90 p-6 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="min-w-[240px] flex-1 space-y-1">
                        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Project Sprints</p>
                        <h2 className="text-lg font-semibold text-slate-900">Sprint Delivery Hub</h2>
                        <p className="text-sm text-slate-500">Monitor cadence, track progress, and open Kanban boards per sprint.</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <Button onClick={handleAddSprint}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Sprint
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
                                placeholder="Search sprint names..."
                            />
                        </div>
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className="px-3 py-2.5 border border-slate-200/70 rounded-full bg-white text-sm text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-900/20 focus:border-slate-300"
                        >
                            <option value="all">All Statuses</option>
                            <option value="planned">Planned</option>
                            <option value="active">Active</option>
                            <option value="completed">Completed</option>
                            <option value="canceled">Canceled</option>
                        </select>
                        <div className="rounded-xl border border-slate-200/70 bg-white px-3 py-2 text-xs text-slate-500">
                            Showing <span className="font-semibold text-slate-900">{filteredCount}</span> of {summary.total} sprints
                        </div>
                        <div className="text-xs text-slate-500">Updated in real time as sprints change.</div>
                    </div>
                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                        <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Sprints</p>
                            <div className="mt-3 flex items-baseline justify-between">
                                <span className="text-2xl font-semibold text-slate-900">{summary.total}</span>
                                <span className="text-xs font-medium text-slate-500">All</span>
                            </div>
                            <p className="mt-3 text-xs text-slate-500">{summary.totalTasks} tasks tracked</p>
                        </div>
                        <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Active</p>
                            <div className="mt-3 flex items-baseline justify-between">
                                <span className="text-2xl font-semibold text-slate-900">{summary.active}</span>
                                <span className="text-xs font-medium text-emerald-600">In flight</span>
                            </div>
                            <p className="mt-3 text-xs text-slate-500">{summary.planned} planned next</p>
                        </div>
                        <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Completed</p>
                            <div className="mt-3 flex items-baseline justify-between">
                                <span className="text-2xl font-semibold text-slate-900">{summary.completed}</span>
                                <span className="text-xs font-medium text-slate-500">Done</span>
                            </div>
                            <p className="mt-3 text-xs text-slate-500">Average {summary.averageProgress}% progress</p>
                        </div>
                        <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">In Planning</p>
                            <div className="mt-3 flex items-baseline justify-between">
                                <span className="text-2xl font-semibold text-slate-900">{summary.planned}</span>
                                <span className="text-xs font-medium text-amber-600">Queued</span>
                            </div>
                            <p className="mt-3 text-xs text-slate-500">Keep backlog ready</p>
                        </div>
                    </div>
                </div>
            </section>
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
            />
            <SprintModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                mode={modalMode}
                sprint={selectedSprint || undefined}
                milestones={milestones}
                onSave={handleSaveSprint}
            />
        </div>
    );
};
