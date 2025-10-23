"use client";

import React, { useState, useEffect } from 'react';
import SearchInput from '@/components/shared/SearchInput';
import Button from '@/components/ui/Button';
import MilestoneTable from './MilestoneTable';
import MilestoneModal from './MilestoneModal';
import { useMilestones } from '@/hooks/useMilestones';
import { getUserTenants } from '@/api/crm';
import { useProject } from '@/context/ProjectContext';
import type { Milestone, UserTenant } from '@/api/types';
import { Plus } from 'lucide-react';

 interface MilestoneSectionProps {
     projectId: number;
     tenant?: number;
 }

 export default function MilestoneSection({ projectId, tenant }: MilestoneSectionProps) {
     const { project } = useProject();
     const tenantId = tenant || parseInt(localStorage.getItem('tenant') || '1');
     const { milestones, loading, error, addMilestone, editMilestone, removeMilestone } = useMilestones(projectId, tenantId);
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedMilestone, setSelectedMilestone] = useState<Milestone | null>(null);
    const [searchValue, setSearchValue] = useState('');
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
        project: number;
        tenant: number;
    }) => {
        try {
            if (modalMode === 'add') {
                await addMilestone(data);
            } else if (selectedMilestone) {
                await editMilestone(selectedMilestone.id, data);
            }
            setModalOpen(false);
        } catch (error) {
            console.error('Error saving milestone:', error);
            // TODO: Show error message
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <SearchInput
                    value={searchValue}
                    onChange={setSearchValue}
                    placeholder="Search milestones..."
                />
                <Button onClick={handleAddMilestone} variant="primary" className="flex items-center">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Milestone
                </Button>
            </div>
            <MilestoneTable
                milestones={milestones}
                loading={loading}
                error={error}
                onEditMilestone={handleEditMilestone}
                onDeleteMilestone={removeMilestone}
                onAddMilestone={handleAddMilestone}
                searchValue={searchValue}
            />
            <MilestoneModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                mode={modalMode}
                milestone={selectedMilestone || undefined}
                projectId={projectId}
                 tenant={tenantId}
                assignees={users}
                projectStart={project?.start_date}
                projectEnd={project?.end_date}
                onSave={handleSaveMilestone}
            />
        </div>
    );
};