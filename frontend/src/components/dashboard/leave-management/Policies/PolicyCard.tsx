"use client";

import { Edit, Trash2, CheckCircle, XCircle } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { LeavePolicy } from '@/api/types';

interface PolicyCardProps {
    policy: LeavePolicy;
    onEdit: (policy: LeavePolicy) => void;
    onDelete: (slug: string) => void;
    canManage: boolean;
}

export default function PolicyCard({ policy, onEdit, onDelete, canManage }: PolicyCardProps) {
    const formatLeaveType = (type: string) => {
        return type.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    };

    const handleDelete = () => {
        if (window.confirm(`Are you sure you want to delete the ${formatLeaveType(policy.leave_type)} policy? This action cannot be undone.`)) {
            onDelete(policy.slug);
        }
    };

    return (
        <Card className="hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                        {formatLeaveType(policy.leave_type)}
                    </h3>
                    <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                        policy.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                    }`}>
                        {policy.is_active ? (
                            <>
                                <CheckCircle size={12} />
                                Active
                            </>
                        ) : (
                            <>
                                <XCircle size={12} />
                                Inactive
                            </>
                        )}
                    </div>
                </div>

                {canManage && (
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onEdit(policy)}
                            className="p-2"
                        >
                            <Edit size={16} />
                        </Button>
                        <Button
                            variant="danger"
                            size="sm"
                            onClick={handleDelete}
                            className="p-2"
                        >
                            <Trash2 size={16} />
                        </Button>
                    </div>
                )}
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="space-y-2">
                    <div className="flex justify-between">
                        <span className="text-gray-600">Annual Entitlement:</span>
                        <span className="font-medium">{policy.annual_entitlement} days</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Max Consecutive:</span>
                        <span className="font-medium">{policy.max_consecutive_days} days</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Notice Period:</span>
                        <span className="font-medium">{policy.notice_period_days} days</span>
                    </div>
                </div>

                <div className="space-y-2">
                    <div className="flex justify-between">
                        <span className="text-gray-600">Carry Over:</span>
                        <span className="font-medium">
                            {policy.carry_over_allowed ? 'Yes' : 'No'}
                        </span>
                    </div>
                    {policy.carry_over_allowed && policy.max_carry_over && (
                        <div className="flex justify-between">
                            <span className="text-gray-600">Max Carry Over:</span>
                            <span className="font-medium">{policy.max_carry_over} days</span>
                        </div>
                    )}
                    {policy.auto_approve_max_days && (
                        <div className="flex justify-between">
                            <span className="text-gray-600">Auto Approve:</span>
                            <span className="font-medium">≤{policy.auto_approve_max_days} days</span>
                        </div>
                    )}
                </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex justify-between text-xs text-gray-500">
                    <span>Created: {new Date(policy.created_at).toLocaleDateString()}</span>
                    <span>Updated: {new Date(policy.updated_at).toLocaleDateString()}</span>
                </div>
            </div>
        </Card>
    );
};