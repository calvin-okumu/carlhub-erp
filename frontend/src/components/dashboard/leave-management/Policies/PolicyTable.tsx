"use client";

"use client";

import { Edit, Trash2 } from 'lucide-react';
import { LeavePolicy } from '@/api/types';
import { formatLeaveType, formatDaysAllowed, formatMaxAtOnce, formatAdvanceNotice } from '@/utils/leave';

interface PolicyTableProps {
    policies: LeavePolicy[];
    onEdit: (policy: LeavePolicy) => void;
    onDelete: (slug: string) => void;
    canManage: boolean;
}

export default function PolicyTable({ policies, onEdit, onDelete, canManage }: PolicyTableProps) {
    const handleDelete = (slug: string, leaveType: string) => {
        if (window.confirm(`Are you sure you want to delete the ${leaveType} policy? This action cannot be undone.`)) {
            onDelete(slug);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            {/* Desktop Table */}
            <div className="hidden md:block overflow-x-auto">
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
                                        {formatDaysAllowed(policy.annual_entitlement)}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        {formatMaxAtOnce(policy.max_consecutive_days)}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        {formatAdvanceNotice(policy.notice_period_days)}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        {formatDaysAllowed(policy.annual_entitlement)}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        {formatMaxAtOnce(policy.max_consecutive_days)}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        {formatAdvanceNotice(policy.notice_period_days)}
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
                                                onClick={() => handleDelete(policy.slug, formatLeaveType(policy.leave_type))}
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

            {/* Mobile View */}
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
                                    <div className="text-gray-900">{formatDaysAllowed(policy.annual_entitlement)}</div>
                                </div>
                                <div>
                                    <span className="font-medium">Max at Once:</span>
                                    <div className="text-gray-900">{formatMaxAtOnce(policy.max_consecutive_days)}</div>
                                </div>
                                <div className="col-span-2">
                                    <span className="font-medium">Advance Notice:</span>
                                    <div className="text-gray-900">{formatAdvanceNotice(policy.notice_period_days)}</div>
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
                                        onClick={() => handleDelete(policy.slug, formatLeaveType(policy.leave_type))}
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
}