"use client";

import React, { useState, useEffect } from 'react';
import SearchInput from '@/components/shared/SearchInput';
import Button from '@/components/ui/Button';
import SprintTable from './SprintTable';
import SprintModal from './SprintModal';
import { useSprints } from '@/hooks/useSprints';
import { getMilestones } from '@/api/project_mgmt';
import type { Sprint, Milestone } from '@/api/types';
import { Plus } from 'lucide-react';

interface SprintSectionProps {
    projectId: number;
}

export default function SprintSection({ projectId }: SprintSectionProps) {
    const { sprints, loading, error, addSprint, editSprint, removeSprint } = useSprints(projectId);
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
                 const data = await getMilestones(token, { projectId });
                 setMilestones(data);
             } catch (err) {
                 console.error('Failed to fetch milestones:', err);
             }
         };

         fetchMilestones();
     }, [projectId]);

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

    const handleDelete = async (id: number) => {
        if (confirm("Are you sure you want to delete this sprint?")) {
            await removeSprint(id);
        }
    };

    const handleSaveSprint = async (data: {
        name: string;
        status: string;
        start_date?: string;
        end_date?: string;
        milestone: number;
    }) => {
        try {
            if (modalMode === 'add') {
                await addSprint(data);
            } else if (selectedSprint) {
                await editSprint(selectedSprint.id, data);
            }
            setModalOpen(false);
        } catch (error) {
            console.error('Error saving sprint:', error);
            // TODO: Show error message
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
                 <Button onClick={handleAddSprint} variant="primary" className="flex items-center">
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
                  projectId={projectId}
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