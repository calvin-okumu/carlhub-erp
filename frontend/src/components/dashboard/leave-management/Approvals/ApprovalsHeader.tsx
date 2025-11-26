import SearchInput from '@/components/shared/SearchInput';
import Button from '@/components/ui/Button';
import { CheckSquare, Filter, Search } from 'lucide-react';

interface ApprovalsHeaderProps {
    searchValue: string;
    onSearchChange: (value: string) => void;
    onFiltersClick: () => void;
}

export const ApprovalsHeader = ({
    searchValue,
    onSearchChange,
    onFiltersClick,
}: ApprovalsHeaderProps) => {
    return (
        <header className="bg-gradient-to-r from-white to-blue-50/30 border border-blue-100 rounded-xl shadow-sm mb-6 p-6">
            <div className="flex flex-col lg:flex-row gap-6 lg:items-center lg:justify-between">
                {/* Title and Search Section */}
                <div className="flex-1 space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-100 rounded-lg">
                            <CheckSquare className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">Leave Approvals</h1>
                            <p className="text-sm text-gray-600">Review and manage leave requests</p>
                        </div>
                    </div>

                    <div className="relative max-w-lg">
                        <SearchInput
                            value={searchValue}
                            onChange={onSearchChange}
                            placeholder="Search by employee, dates, or leave type..."
                        />
                        <Search className="absolute left-4 top-3 w-4 h-4 text-gray-400" />
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-3">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={onFiltersClick}
                        className="flex items-center gap-2 bg-white/80 backdrop-blur border-blue-200 hover:bg-blue-50 hover:border-blue-300 transition-all duration-200"
                    >
                        <Filter className="h-4 w-4" />
                        <span className="hidden sm:inline">Filters</span>
                    </Button>
                </div>
            </div>
        </header>
    );
};
