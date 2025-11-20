import { useState } from 'react';
import { Plus, AlertCircle, CheckCircle2 } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import DropdownCard from '@/components/ui/DropdownCard';
import { useLeavePolicies } from '@/hooks/useLeavePolicies';
import { useUserRole } from '@/hooks/useUserRole';
import PolicyModal, { PolicyFormData } from './PolicyModal';
import PolicyTable from './PolicyTable';
import { LeavePolicy } from '@/api/types';

export const PolicyRules = () => {
    const { policies, isLoading, error, createPolicy, updatePolicy, deletePolicy } = useLeavePolicies();
    const { role } = useUserRole();

    const [showModal, setShowModal] = useState(false);
    const [editingPolicy, setEditingPolicy] = useState<LeavePolicy | null>(null);
    const [modalLoading, setModalLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    // Check if user can manage policies (HR or tenant owner)
    const canManagePolicies = role === 'hr' || role === 'Tenant Owner' || role === 'owner';

    const handleCreate = async (data: PolicyFormData) => {
        setModalLoading(true);
        try {
            await createPolicy(data);
            setShowModal(false);
            setSuccessMessage('Policy created successfully!');
            setTimeout(() => setSuccessMessage(null), 3000);
        } catch (err) {
            console.error('Failed to create policy:', err);
            throw err; // Re-throw to let modal handle error display
        } finally {
            setModalLoading(false);
        }
    };

    const handleUpdate = async (data: PolicyFormData) => {
        if (!editingPolicy) return;
        setModalLoading(true);
        try {
            await updatePolicy(editingPolicy.slug, data);
            setEditingPolicy(null);
            setSuccessMessage('Policy updated successfully!');
            setTimeout(() => setSuccessMessage(null), 3000);
        } catch (err) {
            console.error('Failed to update policy:', err);
            throw err; // Re-throw to let modal handle error display
        } finally {
            setModalLoading(false);
        }
    };

    const handleDelete = async (slug: string) => {
        if (!confirm('Are you sure you want to delete this policy? This action cannot be undone.')) {
            return;
        }

        try {
            await deletePolicy(slug);
            setSuccessMessage('Policy deleted successfully!');
            setTimeout(() => setSuccessMessage(null), 3000);
        } catch (err) {
            console.error('Failed to delete policy:', err);
        }
    };

    const handleEdit = (policy: LeavePolicy) => {
        setEditingPolicy(policy);
    };

    const handleModalClose = () => {
        setShowModal(false);
        setEditingPolicy(null);
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-2 text-gray-600">Loading policies...</span>
            </div>
        );
    }

    if (error) {
        return (
            <Card className="p-6">
                <div className="flex items-center gap-3 text-red-600">
                    <AlertCircle size={20} />
                    <span>Failed to load leave policies: {error}</span>
                </div>
            </Card>
        );
    }

    return (
        <div className="space-y-6">
            {successMessage && (
                <Card className="p-4 bg-green-50 border-green-200">
                    <div className="flex items-center gap-3 text-green-800">
                        <CheckCircle2 size={20} />
                        <span>{successMessage}</span>
                    </div>
                </Card>
            )}

            {/* Header with Create Button */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Leave Policies</h2>
                {canManagePolicies && (
                    <Button
                        variant="gradient"
                        onClick={() => setShowModal(true)}
                    >
                        <Plus size={16} className="mr-2" />
                        Create Policy
                    </Button>
                )}
            </div>

            {/* Policy Modal */}
            <PolicyModal
                isOpen={showModal || !!editingPolicy}
                onClose={handleModalClose}
                policy={editingPolicy}
                onSave={editingPolicy ? handleUpdate : handleCreate}
                isLoading={modalLoading}
            />

            {/* Policies Table */}
            {policies.length === 0 ? (
                <Card className="p-8 text-center">
                    <p className="text-gray-500">No leave policies found.</p>
                    {canManagePolicies && (
                        <p className="text-sm text-gray-400 mt-2">
                            Click &quot;Create Policy&quot; to add your first leave policy.
                        </p>
                    )}
                </Card>
            ) : (
                <PolicyTable
                    policies={policies}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                    canManage={canManagePolicies}
                />
            )}

            {/* Static General Rules (shown for all users) */}
            <DropdownCard title="General Leave Rules">
                <ul className="list-disc pl-6 space-y-1 text-gray-700">
                    <li>All leave must be applied for through the system.</li>
                    <li>Leave must be approved by your manager before it is valid.</li>
                    <li>Leave cannot be taken if you have a pending disciplinary case.</li>
                    <li>You cannot apply for leave retroactively.</li>
                    <li>Public holidays do not count as leave days.</li>
                </ul>
            </DropdownCard>

            <DropdownCard title="Approval Workflow">
                <ul className="list-disc pl-6 space-y-1 text-gray-700">
                    <li>Employee submits leave request.</li>
                    <li>Direct manager receives and reviews the request.</li>
                    <li>HR is notified of all approved leave.</li>
                    <li>System automatically updates leave balance upon approval.</li>
                </ul>
            </DropdownCard>
        </div>
    );
};
