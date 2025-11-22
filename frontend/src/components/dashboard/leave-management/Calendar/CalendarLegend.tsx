import React, { useState } from 'react';
import { Calendar, Filter, X } from 'lucide-react';

interface CalendarLegendProps {
    onFilterChange?: (filters: CalendarFilters) => void;
}

interface CalendarFilters {
    leaveTypes: string[];
    statuses: string[];
    dateRange: {
        start: string;
        end: string;
    };
}

const LEAVE_TYPES = [
    { key: 'annual_leave', label: 'Annual Leave', icon: '🏖️', color: 'bg-blue-500' },
    { key: 'sick_leave', label: 'Sick Leave', icon: '🏥', color: 'bg-red-500' },
    { key: 'personal_leave', label: 'Personal Leave', icon: '👤', color: 'bg-purple-500' },
    { key: 'maternity_leave', label: 'Maternity Leave', icon: '🤰', color: 'bg-pink-500' },
    { key: 'paternity_leave', label: 'Paternity Leave', icon: '👨‍👧‍👦', color: 'bg-indigo-500' },
    { key: 'emergency_leave', label: 'Emergency Leave', icon: '🚨', color: 'bg-orange-500' },
    { key: 'unpaid_leave', label: 'Unpaid Leave', icon: '💳', color: 'bg-gray-500' },
];

const STATUSES = [
    { key: 'approved', label: 'Approved', color: 'bg-green-500' },
    { key: 'pending', label: 'Pending', color: 'bg-yellow-500' },
    { key: 'taken', label: 'Taken', color: 'bg-blue-500' },
    { key: 'rejected', label: 'Rejected', color: 'bg-red-500' },
];

export const CalendarLegend: React.FC<CalendarLegendProps> = ({ onFilterChange }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [filters, setFilters] = useState<CalendarFilters>({
        leaveTypes: [],
        statuses: [],
        dateRange: { start: '', end: '' }
    });

    const toggleLeaveType = (type: string) => {
        const newTypes = filters.leaveTypes.includes(type)
            ? filters.leaveTypes.filter(t => t !== type)
            : [...filters.leaveTypes, type];
        
        const newFilters = { ...filters, leaveTypes: newTypes };
        setFilters(newFilters);
        onFilterChange?.(newFilters);
    };

    const toggleStatus = (status: string) => {
        const newStatuses = filters.statuses.includes(status)
            ? filters.statuses.filter(s => s !== status)
            : [...filters.statuses, status];
        
        const newFilters = { ...filters, statuses: newStatuses };
        setFilters(newFilters);
        onFilterChange?.(newFilters);
    };

    const clearFilters = () => {
        const newFilters = {
            leaveTypes: [],
            statuses: [],
            dateRange: { start: '', end: '' }
        };
        setFilters(newFilters);
        onFilterChange?.(newFilters);
    };

    const hasActiveFilters = filters.leaveTypes.length > 0 || filters.statuses.length > 0;

    return (
        <div className="relative">
            {/* Legend Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`
                    flex items-center gap-2 px-4 py-2 rounded-lg border transition-all duration-200
                    ${isOpen 
                        ? 'bg-blue-600 text-white border-blue-600 shadow-lg' 
                        : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50 hover:border-gray-300'
                    }
                `}
            >
                <Calendar className="w-4 h-4" />
                <span className="font-medium">Legend</span>
                {hasActiveFilters && (
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
                )}
            </button>

            {/* Legend Panel */}
            {isOpen && (
                <div className="absolute top-full left-0 mt-2 w-96 bg-white rounded-xl border border-gray-200 shadow-2xl z-50 max-h-96 overflow-y-auto">
                    {/* Header */}
                    <div className="flex items-center justify-between p-4 border-b border-gray-100 bg-gray-50">
                        <div className="flex items-center gap-2">
                            <Filter className="w-4 h-4 text-gray-600" />
                            <h3 className="font-semibold text-gray-900">Calendar Legend & Filters</h3>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="p-1 hover:bg-gray-200 rounded-lg transition-colors"
                        >
                            <X className="w-4 h-4 text-gray-500" />
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-4 space-y-6">
                        {/* Leave Types */}
                        <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-3">Leave Types</h4>
                            <div className="space-y-2">
                                {LEAVE_TYPES.map((type) => (
                                    <label
                                        key={type.key}
                                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                                    >
                                        <input
                                            type="checkbox"
                                            checked={filters.leaveTypes.includes(type.key)}
                                            onChange={() => toggleLeaveType(type.key)}
                                            className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                                        />
                                        <div className="flex items-center gap-2 flex-1">
                                            <span className="text-lg">{type.icon}</span>
                                            <span className="text-sm font-medium text-gray-700">{type.label}</span>
                                        </div>
                                        <div className={`w-3 h-3 rounded-full ${type.color}`}></div>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Statuses */}
                        <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-3">Status</h4>
                            <div className="space-y-2">
                                {STATUSES.map((status) => (
                                    <label
                                        key={status.key}
                                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                                    >
                                        <input
                                            type="checkbox"
                                            checked={filters.statuses.includes(status.key)}
                                            onChange={() => toggleStatus(status.key)}
                                            className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                                        />
                                        <span className="text-sm font-medium text-gray-700 flex-1">{status.label}</span>
                                        <div className={`w-3 h-3 rounded-full ${status.color}`}></div>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Actions */}
                        {hasActiveFilters && (
                            <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                                <span className="text-sm text-gray-600">
                                    {filters.leaveTypes.length + filters.statuses.length} filter{filters.leaveTypes.length + filters.statuses.length === 1 ? '' : 's'} active
                                </span>
                                <button
                                    onClick={clearFilters}
                                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                                >
                                    Clear All
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};