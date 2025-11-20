"use client";

import { useState } from 'react';
import { Plus, AlertCircle, CheckCircle2, Edit, Trash2 } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { useLeavePolicies } from '@/hooks/useLeavePolicies';
import { useUserRole } from '@/hooks/useUserRole';
import PolicyModal, { PolicyFormData } from './PolicyModal';
import { LeavePolicy } from '@/api/types';

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

const PolicyTable = ({
    policies,
    onEdit,
    onDelete,
    canManage
}: {
    policies: LeavePolicy[];
    onEdit: (policy: LeavePolicy) => void;
    onDelete: (slug: string) => void;
    canManage: boolean;
}) => {
    const formatLeaveType = (type: string) => {
        const typeMap: Record<string, string> = {
            'annual': 'Annual Leave',
            'sick': 'Sick Leave',
            'casual': 'Casual Leave',
            'maternity': 'Maternity Leave',
            'paternity': 'Paternity Leave',
            'unpaid': 'Unpaid Leave'
        };
        return typeMap[type] || type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Leave Type
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Days Allowed
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Max at Once
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Advance Notice
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            {canManage && (
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            )}
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {policies.map((policy) => (
                            <tr key={policy.slug} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm font-medium text-gray-900">
                                        {formatLeaveType(policy.leave_type)}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        {policy.annual_entitlement} days/year
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        {policy.max_consecutive_days > 0
                                            ? `${policy.max_consecutive_days} days`
                                            : 'No limit'
                                        }
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        {policy.notice_period_days > 0
                                            ? `${policy.notice_period_days} days`
                                            : 'Same day'
                                        }
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                        policy.is_active
                                            ? 'bg-green-100 text-green-800'
                                            : 'bg-red-100 text-red-800'
                                    }`}>
                                        {policy.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </td>
                                {canManage && (
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <div className="flex space-x-2">
                                            <button
                                                onClick={() => onEdit(policy)}
                                                className="text-blue-600 hover:text-blue-900 transition-colors"
                                                title="Edit Policy"
                                            >
                                                <Edit size={16} />
                                            </button>
                                            <button
                                                onClick={() => onDelete(policy.slug)}
                                                className="text-red-600 hover:text-red-900 transition-colors"
                                                title="Delete Policy"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </td>
                                )}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Mobile view for small screens */}
            <div className="md:hidden">
                <div className="divide-y divide-gray-200">
                    {policies.map((policy) => (
                        <div key={policy.slug} className="p-4 hover:bg-gray-50">
                            <div className="flex justify-between items-start mb-3">
                                <h3 className="font-medium text-gray-900">
                                    {formatLeaveType(policy.leave_type)}
                                </h3>
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                    policy.is_active
                                        ? 'bg-green-100 text-green-800'
                                        : 'bg-red-100 text-red-800'
                                }`}>
                                    {policy.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>

                            <div className="grid grid-cols-2 gap-3 text-sm text-gray-600 mb-3">
                                <div>
                                    <span className="font-medium">Days Allowed:</span>
                                    <div className="text-gray-900">{policy.annual_entitlement} days/year</div>
                                </div>
                                <div>
                                    <span className="font-medium">Max at Once:</span>
                                    <div className="text-gray-900">
                                        {policy.max_consecutive_days > 0
                                            ? `${policy.max_consecutive_days} days`
                                            : 'No limit'
                                        }
                                    </div>
                                </div>
                                <div className="col-span-2">
                                    <span className="font-medium">Advance Notice:</span>
                                    <div className="text-gray-900">
                                        {policy.notice_period_days > 0
                                            ? `${policy.notice_period_days} days`
                                            : 'Same day'
                                        }
                                    </div>
                                </div>
                            </div>

                            {canManage && (
                                <div className="flex gap-3 pt-2 border-t border-gray-200">
                                    <button
                                        onClick={() => onEdit(policy)}
                                        className="flex items-center gap-1 text-blue-600 hover:text-blue-900 text-sm font-medium"
                                    >
                                        <Edit size={14} />
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => onDelete(policy.slug)}
                                        className="flex items-center gap-1 text-red-600 hover:text-red-900 text-sm font-medium"
                                    >
                                        <Trash2 size={14} />
                                        Delete
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

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