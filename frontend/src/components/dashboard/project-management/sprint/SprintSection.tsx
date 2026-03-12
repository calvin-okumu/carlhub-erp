"use client";

import { getMilestones } from '@/api/project_mgmt';
import type { Milestone, Sprint } from '@/api/types';
import SearchInput from '@/components/shared/SearchInput';
import Button from '@/components/ui/Button';
import { useProject } from '@/context/ProjectContext';
import { useSprints } from '@/hooks/useSprints';
import { Plus } from 'lucide-react';
import { useEffect, useState } from 'react';
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
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
                <div className="flex flex-1 flex-wrap items-center gap-3">
                    <div className="min-w-[220px] flex-1">
                        <SearchInput
                            value={searchValue}
                            onChange={setSearchValue}
                            placeholder="Search sprints..."
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
                </div>
                <Button onClick={handleAddSprint}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Sprint
                </Button>
            </div>
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
