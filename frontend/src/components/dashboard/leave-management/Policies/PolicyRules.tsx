"use client";

import { useState } from 'react';
import { Plus, AlertCircle, CheckCircle2 } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { useLeavePolicies } from '@/hooks/useLeavePolicies';
import { useUserRole } from '@/hooks/useUserRole';
import PolicyModal, { PolicyFormData } from './PolicyModal';
import PolicyCard from './PolicyCard';

const DropdownCard = ({ title, children }: { title: string; children: React.ReactNode }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <Card className="mt-6">
            <div
                className="flex items-center justify-between cursor-pointer p-4 hover:bg-gray-50 transition-colors"
                onClick={() => setIsOpen(!isOpen)}
            >
                <h2 className="text-xl font-bold text-gray-900">{title}</h2>
                <div className={`transform transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}>
                    <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </div>
            </div>

            <div className={`overflow-hidden transition-all duration-300 ${isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}>
                <div className="px-4 pb-4">{children}</div>
            </div>
        </Card>
    );
};

export const PolicyRules = () => {
    const { policies, isLoading, error, createPolicy, updatePolicy, deletePolicy } = useLeavePolicies();
    const { role } = useUserRole();

    const [showModal, setShowModal] = useState(false);
    const [editingPolicy, setEditingPolicy] = useState<any>(null); // TODO: Fix type
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
        try {
            await deletePolicy(slug);
            setSuccessMessage('Policy deleted successfully!');
            setTimeout(() => setSuccessMessage(null), 3000);
        } catch (err) {
            console.error('Failed to delete policy:', err);
        }
    };

    const handleEdit = (policy: any) => { // TODO: Fix type
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

            {/* Policies List */}
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
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {policies.map((policy) => (
                        <PolicyCard
                            key={policy.slug}
                            policy={policy}
                            onEdit={handleEdit}
                            onDelete={handleDelete}
                            canManage={canManagePolicies}
                        />
                    ))}
                </div>
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