import React from 'react';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export default function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const getStatusClasses = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'completed':
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'pending':
      case 'planning':
      case 'pending_department_manager':
      case 'pending_hr_manager':
      case 'pending_general_manager':
        return 'bg-yellow-100 text-yellow-800';
      case 'inactive':
      case 'cancelled':
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'taken':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusDisplay = (status: string): string => {
    const displays = {
      pending_department_manager: 'Pending Dept Manager',
      pending_hr_manager: 'Pending HR Manager',
      pending_general_manager: 'Pending GM',
      approved: 'Approved',
      rejected: 'Rejected',
      cancelled: 'Cancelled',
      taken: 'Taken',
    };
    return displays[status as keyof typeof displays] || status.replace('_', ' ');
  };

  return (
    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusClasses(status)} ${className}`}>
      {getStatusDisplay(status)}
    </span>
  );
}