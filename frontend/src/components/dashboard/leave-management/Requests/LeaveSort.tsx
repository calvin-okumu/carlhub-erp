import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import { ArrowUpDown, Filter } from 'lucide-react';

export type LeaveType =
    | 'all'
    | 'annual_leave'
    | 'sick_leave'
    | 'personal_leave'
    | 'maternity_leave'
    | 'emergency_leave'
    | 'unpaid_leave';

export type SortOption =
    | 'applied_date_desc'
    | 'applied_date_asc'
    | 'start_date_desc'
    | 'start_date_asc'
    | 'status';

interface LeaveSortProps {
    onSortChange: (sortBy: LeaveType) => void;
    onSortOptionChange?: (sortOption: SortOption) => void;
    currentSort?: LeaveType;
    currentSortOption?: SortOption;
}

const LEAVE_TYPE_OPTIONS = [
    { value: 'all', label: 'All Leave Types' },
    { value: 'annual_leave', label: 'Annual Leave' },
    { value: 'sick_leave', label: 'Sick Leave' },
    { value: 'personal_leave', label: 'Personal Leave' },
    { value: 'maternity_leave', label: 'Maternity/Paternity Leave' },
    { value: 'emergency_leave', label: 'Emergency Leave' },
    { value: 'unpaid_leave', label: 'Unpaid Leave' },
] as const;

const SORT_OPTIONS = [
    { value: 'applied_date_desc', label: 'Most Recent First' },
    { value: 'applied_date_asc', label: 'Oldest First' },
    { value: 'start_date_desc', label: 'Start Date (Newest)' },
    { value: 'start_date_asc', label: 'Start Date (Oldest)' },
    { value: 'status', label: 'Status' },
] as const;

export const LeaveSort = ({
    onSortChange,
    onSortOptionChange,
    currentSort = 'all',
    currentSortOption = 'applied_date_desc'
}: LeaveSortProps) => {
    return (
        <div className="flex flex-wrap items-center gap-4 p-4 bg-white/60 backdrop-blur border rounded-xl shadow-sm mb-6">
            {/* Filter */}
            <div className="flex items-center gap-2 text-sm text-gray-700 font-medium">
                <Filter size={16} />
                <span>Filter:</span>
            </div>

            <Select
                value={currentSort}
                onChange={(e) => onSortChange(e.target.value as LeaveType)}
                className="bg-white border rounded-lg shadow-sm w-48"
            >
                {LEAVE_TYPE_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </Select>

            {/* Sort */}
            <div className="flex items-center gap-2 text-sm text-gray-700 font-medium">
                <ArrowUpDown size={16} />
                <span>Sort:</span>
            </div>

            <Select
                value={currentSortOption}
                onChange={(e) => onSortOptionChange?.(e.target.value as SortOption)}
                className="bg-white border rounded-lg shadow-sm w-48"
            >
                {SORT_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </Select>

            <Button
                variant="outline"
                size="sm"
                onClick={() => onSortChange('all')}
                className="text-xs bg-white border shadow-sm ml-auto"
            >
                <ArrowUpDown size={14} className="mr-1" />
                Clear Filters
            </Button>
        </div>
    );
};
