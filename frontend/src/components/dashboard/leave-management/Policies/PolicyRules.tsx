"use client";

import Card from "@/components/ui/Card";
import { ChevronDown, Plus, Edit, Trash2, AlertCircle, CheckCircle2 } from "lucide-react";
import { useState } from "react";
import { useLeavePolicies } from "@/hooks/useLeavePolicies";
import { useUserRole } from "@/hooks/useUserRole";
import { LeavePolicy } from "@/api/types";

const DropdownCard = ({ title, children }: { title: string; children: React.ReactNode }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <Card className="mt-6">
            <div
                className="flex items-center justify-between cursor-pointer p-4 hover:bg-gray-50 transition-colors"
                onClick={() => setIsOpen(!isOpen)}
            >
                <h2 className="text-xl font-bold text-gray-900">{title}</h2>
                <ChevronDown
                    className={`w-5 h-5 text-gray-500 transition-transform ${isOpen ? "rotate-180" : ""
                        }`}
                />
            </div>

            <div
                className={`overflow-hidden transition-all duration-300 ${isOpen ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
                    }`}
            >
                <div className="px-4 pb-4">{children}</div>
            </div>
        </Card>
    );
};

const PolicyCard = ({
    policy,
    onEdit,
    onDelete,
    canManage
}: {
    policy: LeavePolicy;
    onEdit: (policy: LeavePolicy) => void;
    onDelete: (slug: string) => void;
    canManage: boolean;
}) => {
    return (
        <Card className="p-4">
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 capitalize">
                            {policy.leave_type.replace('_', ' ')}
                        </h3>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                            policy.is_active
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                        }`}>
                            {policy.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                        <div>
                            <span className="font-medium">Annual Entitlement:</span> {policy.annual_entitlement} days
                        </div>
                        <div>
                            <span className="font-medium">Max Consecutive:</span> {policy.max_consecutive_days} days
                        </div>
                        <div>
                            <span className="font-medium">Notice Period:</span> {policy.notice_period_days} days
                        </div>
                        <div>
                            <span className="font-medium">Carry Over:</span> {policy.carry_over_allowed ? 'Yes' : 'No'}
                            {policy.carry_over_allowed && policy.max_carry_over && ` (max ${policy.max_carry_over})`}
                        </div>
                        {policy.auto_approve_max_days && (
                            <div className="col-span-2">
                                <span className="font-medium">Auto Approve:</span> ≤{policy.auto_approve_max_days} days
                            </div>
                        )}
                    </div>
                </div>

                {canManage && (
                    <div className="flex gap-2 ml-4">
                        <button
                            onClick={() => onEdit(policy)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Edit Policy"
                        >
                            <Edit size={16} />
                        </button>
                        <button
                            onClick={() => onDelete(policy.slug)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete Policy"
                        >
                            <Trash2 size={16} />
                        </button>
                    </div>
                )}
            </div>
        </Card>
    );
};

const PolicyForm = ({
    policy,
    onSave,
    onCancel,
    isLoading
}: {
    policy?: LeavePolicy;
    onSave: (data: {
        leave_type: string;
        annual_entitlement: number;
        max_consecutive_days: number;
        notice_period_days: number;
        carry_over_allowed: boolean;
        max_carry_over?: number;
        auto_approve_max_days?: number;
        is_active: boolean;
    } | Partial<LeavePolicy>) => Promise<void>;
    onCancel: () => void;
    isLoading: boolean;
}) => {
    const [formData, setFormData] = useState({
        leave_type: policy?.leave_type || '',
        annual_entitlement: policy?.annual_entitlement || 0,
        max_consecutive_days: policy?.max_consecutive_days || 0,
        notice_period_days: policy?.notice_period_days || 0,
        carry_over_allowed: policy?.carry_over_allowed || false,
        max_carry_over: policy?.max_carry_over || undefined,
        auto_approve_max_days: policy?.auto_approve_max_days || undefined,
        is_active: policy?.is_active ?? true,
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await onSave(formData);
    };

    return (
        <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">
                {policy ? 'Edit Leave Policy' : 'Create Leave Policy'}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Leave Type *
                        </label>
                        <select
                            value={formData.leave_type}
                            onChange={(e) => setFormData(prev => ({ ...prev, leave_type: e.target.value }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            required
                        >
                            <option value="">Select type</option>
                            <option value="annual">Annual Leave</option>
                            <option value="sick">Sick Leave</option>
                            <option value="casual">Casual Leave</option>
                            <option value="maternity">Maternity Leave</option>
                            <option value="paternity">Paternity Leave</option>
                            <option value="unpaid">Unpaid Leave</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Annual Entitlement (days) *
                        </label>
                        <input
                            type="number"
                            value={formData.annual_entitlement}
                            onChange={(e) => setFormData(prev => ({ ...prev, annual_entitlement: parseInt(e.target.value) || 0 }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            min="0"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Max Consecutive Days *
                        </label>
                        <input
                            type="number"
                            value={formData.max_consecutive_days}
                            onChange={(e) => setFormData(prev => ({ ...prev, max_consecutive_days: parseInt(e.target.value) || 0 }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            min="0"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Notice Period (days) *
                        </label>
                        <input
                            type="number"
                            value={formData.notice_period_days}
                            onChange={(e) => setFormData(prev => ({ ...prev, notice_period_days: parseInt(e.target.value) || 0 }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            min="0"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Carry Over Allowed
                        </label>
                        <input
                            type="checkbox"
                            checked={formData.carry_over_allowed}
                            onChange={(e) => setFormData(prev => ({ ...prev, carry_over_allowed: e.target.checked }))}
                            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                    </div>

                    {formData.carry_over_allowed && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Max Carry Over (days)
                            </label>
                            <input
                                type="number"
                                value={formData.max_carry_over || ''}
                                onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    max_carry_over: e.target.value ? parseInt(e.target.value) : undefined
                                }))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                min="0"
                            />
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Auto Approve ≤ (days)
                        </label>
                        <input
                            type="number"
                            value={formData.auto_approve_max_days || ''}
                            onChange={(e) => setFormData(prev => ({
                                ...prev,
                                auto_approve_max_days: e.target.value ? parseInt(e.target.value) : undefined
                            }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            min="0"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Active
                        </label>
                        <input
                            type="checkbox"
                            checked={formData.is_active}
                            onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                    </div>
                </div>

                <div className="flex gap-3 pt-4">
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? 'Saving...' : (policy ? 'Update Policy' : 'Create Policy')}
                    </button>
                    <button
                        type="button"
                        onClick={onCancel}
                        className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </Card>
    );
};

export const PolicyRules = () => {
    const { policies, isLoading, error, createPolicy, updatePolicy, deletePolicy } = useLeavePolicies();
    const { role, canApproveLeave } = useUserRole();

    const [showForm, setShowForm] = useState(false);
    const [editingPolicy, setEditingPolicy] = useState<LeavePolicy | undefined>();
    const [formLoading, setFormLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    // Check if user can manage policies (HR or tenant owner)
    const canManagePolicies = role === 'hr' || role === 'Tenant Owner' || role === 'owner';

    const handleCreate = async (data: {
      leave_type: string;
      annual_entitlement: number;
      max_consecutive_days: number;
      notice_period_days: number;
      carry_over_allowed: boolean;
      max_carry_over?: number;
      auto_approve_max_days?: number;
      is_active: boolean;
    }) => {
        setFormLoading(true);
        try {
            await createPolicy(data);
            setShowForm(false);
            setSuccessMessage('Policy created successfully!');
            setTimeout(() => setSuccessMessage(null), 3000);
        } catch (err) {
            console.error('Failed to create policy:', err);
        } finally {
            setFormLoading(false);
        }
    };

    const handleUpdate = async (data: Partial<LeavePolicy>) => {
        if (!editingPolicy) return;
        setFormLoading(true);
        try {
            await updatePolicy(editingPolicy.slug, data);
            setEditingPolicy(undefined);
            setSuccessMessage('Policy updated successfully!');
            setTimeout(() => setSuccessMessage(null), 3000);
        } catch (err) {
            console.error('Failed to update policy:', err);
        } finally {
            setFormLoading(false);
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
                    <button
                        onClick={() => setShowForm(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <Plus size={16} />
                        Create Policy
                    </button>
                )}
            </div>

            {/* Create/Edit Form */}
            {(showForm || editingPolicy) && (
                <PolicyForm
                    policy={editingPolicy}
                    onSave={editingPolicy ? handleUpdate : handleCreate}
                    onCancel={() => {
                        setShowForm(false);
                        setEditingPolicy(undefined);
                    }}
                    isLoading={formLoading}
                />
            )}

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
                <div className="grid gap-4">
                    {policies.map((policy) => (
                        <PolicyCard
                            key={policy.slug}
                            policy={policy}
                            onEdit={setEditingPolicy}
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
