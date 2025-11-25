"use client";

import type { Sprint } from '@/api/types';
import SearchInput from '@/components/shared/SearchInput';
import Button from '@/components/ui/Button';
import { useProject } from '@/context/ProjectContext';
import { useSprintsContext } from '@/context/SprintsContext';
import { useMilestonesContext } from '@/context/MilestonesContext';
import { useSprints } from '@/hooks/useSprints';
import { Plus } from 'lucide-react';
import { useState } from 'react';
import SprintModal from './SprintModal';
import SprintTable from './SprintTable';

export default function SprintSection() {
    const { project } = useProject();
    const { sprints, loading, error, updateSprintOptimistically, removeSprintOptimistically, refetch } = useSprintsContext();
    const { milestones } = useMilestonesContext();
    const { addSprint } = useSprints(project?.id || 0);
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedSprint, setSelectedSprint] = useState<Sprint | null>(null);
    const [searchValue, setSearchValue] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('all');

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
            removeSprintOptimistically(slug);
        }
    };

    const handleSaveSprint = async (data: {
        name: string;
        status: string;
        start_date?: string;
        end_date?: string;
        milestone: string;
    }) => {
        if (!project?.id) {
            alert('Project not loaded yet. Please wait and try again.');
            return;
        }

        try {
            if (modalMode === 'add') {
                // Use hook's addSprint function for proper state management
                await addSprint(data);
            } else if (selectedSprint) {
                updateSprintOptimistically(selectedSprint.slug, data);
            }
            setModalOpen(false);
        } catch (error) {
            console.error('Error saving sprint:', error);
            // TODO: Show error message to user
            alert(`Error saving sprint: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    };



    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div className="flex items-center space-x-4">
                    <SearchInput
                        value={searchValue}
                        onChange={setSearchValue}
                        placeholder="Search sprints..."
                    />
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        <option value="all">All Statuses</option>
                        <option value="planned">Planned</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                    </select>
                </div>
                <Button onClick={handleAddSprint} >
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
