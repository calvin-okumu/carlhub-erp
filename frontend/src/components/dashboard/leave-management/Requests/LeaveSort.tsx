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
interface LeaveSortProps {
    onSortChange: (sortBy: LeaveType) => void;
    currentSort?: LeaveType;
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
export const LeaveSort = ({ onSortChange, currentSort = 'all' }: LeaveSortProps) => {
    const handleSortChange = (value: string) => {
        onSortChange(value as LeaveType);
    };
    return (
        <div className=" flex items-center gap-3 mb-4">
            <div className="flex items-center gap-2 text-sm text-gray-600">
                <Filter size={16} />
                <span>Filter by:</span>
            </div>

            <Select
                value={currentSort}
                onChange={(e) => handleSortChange(e.target.value)}
                className="bg-white shadow-md w-48"
            >
                {LEAVE_TYPE_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </Select>
            <Button
                variant="outline"
                size="sm"
                onClick={() => onSortChange('all')}
                className="text-xs bg-white shadow-md"
            >
                <ArrowUpDown size={14} className="mr-1" />
                Clear Filter
            </Button>
        </div>
    );
};
