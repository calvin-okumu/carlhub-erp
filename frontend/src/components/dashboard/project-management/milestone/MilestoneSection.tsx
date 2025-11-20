"use client";

import { getUserTenants } from '@/api/crm';
import { createMilestone } from '@/api/project_mgmt';
import type { Milestone, UserTenant } from '@/api/types';
import SearchInput from '@/components/shared/SearchInput';
import Button from '@/components/ui/Button';
import { useMilestonesContext } from '@/context/MilestonesContext';
import { useProject } from '@/context/ProjectContext';
import { getAccessToken } from '@/utils/auth';
import { Plus } from 'lucide-react';
import { useEffect, useState } from 'react';
import MilestoneModal from './MilestoneModal';
import MilestoneTable from './MilestoneTable';

interface MilestoneSectionProps {
    tenant: number;
}

export default function MilestoneSection({ tenant }: MilestoneSectionProps) {
    const { project } = useProject();
    const { milestones, loading, error, updateMilestoneOptimistically, removeMilestoneOptimistically, refetch } = useMilestonesContext();
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedMilestone, setSelectedMilestone] = useState<Milestone | null>(null);
    const [searchValue, setSearchValue] = useState('');
    const [users, setUsers] = useState<UserTenant[]>([]);

    useEffect(() => {
        const fetchUsers = async () => {
            const token = getAccessToken();
            if (!token) return;

            try {
                const data = await getUserTenants();
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
        tenant: number;
    }) => {
        try {
            const token = getAccessToken();
            if (!token || !project?.id) {
                throw new Error('Authentication or project data missing');
            }

            if (modalMode === 'add') {
                // Call API to create milestone
                await createMilestone(token, project.id, data);
                
                // Refetch milestones to get updated list
                refetch();
            } else if (selectedMilestone) {
                updateMilestoneOptimistically(selectedMilestone.slug, data);
            }
            setModalOpen(false);
        } catch (error) {
            console.error('Error saving milestone:', error);
            // TODO: Show error message to user
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
                <Button onClick={handleAddMilestone} >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Milestone
                </Button>
            </div>
            <MilestoneTable
                milestones={milestones}
                loading={loading}
                error={error}
                onEditMilestone={handleEditMilestone}
                onDeleteMilestone={removeMilestoneOptimistically}
                onAddMilestone={handleAddMilestone}
                searchValue={searchValue}
            />
            <MilestoneModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                mode={modalMode}
                milestone={selectedMilestone || undefined}
                projectSlug={project?.slug || ''}
                tenant={tenant}
                assignees={users}
                projectStart={project?.start_date}
                projectEnd={project?.end_date}
                onSave={handleSaveMilestone}
            />
        </div>
    );
};
