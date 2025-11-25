"use client";

import { CheckCircle, Clock, XCircle, AlertCircle, User } from 'lucide-react';
import type { WorkflowStatus as WorkflowStatusType, WorkflowStep } from '@/api/types';

interface WorkflowStatusProps {
    workflowStatus: WorkflowStatusType;
    className?: string;
}

export default function WorkflowStatus({ workflowStatus, className = '' }: WorkflowStatusProps) {
    const getStepIcon = (status: string) => {
        switch (status) {
            case 'approved':
                return <CheckCircle className="w-5 h-5 text-green-500" />;
            case 'rejected':
                return <XCircle className="w-5 h-5 text-red-500" />;
            case 'pending':
                return <Clock className="w-5 h-5 text-yellow-500" />;
            case 'skipped':
                return <AlertCircle className="w-5 h-5 text-gray-400" />;
            default:
                return <Clock className="w-5 h-5 text-gray-400" />;
        }
    };

    const getStepBorderColor = (status: string, isActive: boolean) => {
        if (status === 'approved') return 'border-green-500';
        if (status === 'rejected') return 'border-red-500';
        if (status === 'pending' && isActive) return 'border-yellow-500';
        return 'border-gray-300';
    };

    const getStepBgColor = (status: string, isActive: boolean) => {
        if (status === 'approved') return 'bg-green-50';
        if (status === 'rejected') return 'bg-red-50';
        if (status === 'pending' && isActive) return 'bg-yellow-50';
        return 'bg-white';
    };

    return (
        <div className={`space-y-4 ${className}`}>
            {/* Current Status Summary */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                    <h3 className="font-semibold text-gray-900">Current Status</h3>
                    <p className="text-sm text-gray-600">{workflowStatus.current_status}</p>
                </div>
                {workflowStatus.next_approver && (
                    <div className="text-right">
                        <p className="text-sm text-gray-500">Next Approver</p>
                        <p className="font-medium text-gray-900">{workflowStatus.next_approver}</p>
                    </div>
                )}
            </div>

            {/* Workflow Steps */}
            <div className="space-y-3">
                <h4 className="font-medium text-gray-900">Approval Workflow</h4>
                <div className="relative">
                    {/* Connection Line */}
                    <div className="absolute left-6 top-8 bottom-8 w-0.5 bg-gray-300"></div>
                    
                    {workflowStatus.steps.map((step: WorkflowStep, index: number) => {
                        const isActive = step.status === 'pending' && workflowStatus.is_pending;
                        return (
                            <div key={step.level} className="relative flex items-start space-x-4 pb-6">
                                {/* Step Icon */}
                                <div className={`relative z-10 flex items-center justify-center w-12 h-12 rounded-full border-2 ${getStepBorderColor(step.status, isActive)} ${getStepBgColor(step.status, isActive)}`}>
                                    {getStepIcon(step.status)}
                                </div>
                                
                                {/* Step Content */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h5 className="font-medium text-gray-900">
                                                {step.level_display}
                                            </h5>
                                            <p className="text-sm text-gray-500">
                                                Step {step.order}
                                            </p>
                                        </div>
                                        {step.approved_date && (
                                            <p className="text-sm text-gray-500">
                                                {new Date(step.approved_date).toLocaleDateString()}
                                            </p>
                                        )}
                                    </div>
                                    
                                    {step.approver && (
                                        <div className="flex items-center mt-1 text-sm text-gray-600">
                                            <User className="w-4 h-4 mr-1" />
                                            {step.approver}
                                        </div>
                                    )}
                                    
                                    {step.notes && (
                                        <p className="mt-2 text-sm text-gray-600 bg-gray-50 p-2 rounded">
                                            {step.notes}
                                        </p>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Status Summary */}
            <div className="flex items-center space-x-6 text-sm">
                <div className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                    <span className="text-gray-600">Approved</span>
                </div>
                <div className="flex items-center">
                    <Clock className="w-4 h-4 text-yellow-500 mr-1" />
                    <span className="text-gray-600">Pending</span>
                </div>
                <div className="flex items-center">
                    <XCircle className="w-4 h-4 text-red-500 mr-1" />
                    <span className="text-gray-600">Rejected</span>
                </div>
                <div className="flex items-center">
                    <AlertCircle className="w-4 h-4 text-gray-400 mr-1" />
                    <span className="text-gray-600">Skipped</span>
                </div>
            </div>
        </div>
    );
}