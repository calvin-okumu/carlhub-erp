import SearchInput from '@/components/shared/SearchInput';
import Button from '@/components/ui/Button';
import { Filter } from 'lucide-react';

interface ApprovalsHeaderProps {
    searchValue: string;
    onSearchChange: (value: string) => void;
    onFiltersClick: () => void;
    onBulkActionsClick: () => void;
}

export const ApprovalsHeader = ({
    searchValue,
    onSearchChange,
    onFiltersClick,
    onBulkActionsClick
}: ApprovalsHeaderProps) => {
    return (
        <header className="bg-white/60 backdrop-blur border rounded-xl shadow-sm mb-6 p-6">
            <div className="flex flex-col sm:flex-row gap-4 sm:items-center sm:justify-between">
                <div className="flex-1 max-w-lg">
                    <SearchInput
                        value={searchValue}
                        onChange={onSearchChange}
                        placeholder="Search by employee, dates, or leave type..."
                    />
                </div>

                <div className="flex items-center gap-3">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={onFiltersClick}
                        className="flex items-center gap-2"
                    >
                        <Filter className="h-4 w-4" />
                        <span className="hidden sm:inline">Filters</span>
                    </Button>

                    <Button
                        variant="secondary"
                        size="sm"
                        onClick={onBulkActionsClick}
                        className="flex items-center gap-2"
                    >
                        Bulk Actions
                    </Button>
                </div>
            </div>
        </header>
    );
};
