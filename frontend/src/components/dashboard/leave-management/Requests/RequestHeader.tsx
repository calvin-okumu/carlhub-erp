import { Plus } from 'lucide-react';
import { useEffect, useState } from 'react';
import SearchInput from '../../../shared/SearchInput';
import Button from '../../../ui/Button';
import LeaveRequestModal from './LeaveRequestModal';
interface RequestHeaderProps {
    onSearchChange: (value: string) => void;
    onRequestSuccess?: () => void;
    searchPlaceholder?: string;
    onCreateRequest?: (openModal: () => void) => void;
}
export const RequestHeader = ({
    onSearchChange,
    onRequestSuccess,
    searchPlaceholder = "Search leave requests...",
    onCreateRequest
}: RequestHeaderProps) => {
    const [searchValue, setSearchValue] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        if (onCreateRequest) {
            onCreateRequest(() => setIsModalOpen(true));
        }
    }, [onCreateRequest]);
    const handleSearchChange = (value: string) => {
        setSearchValue(value);
        onSearchChange(value);
    };
    const handleNewRequest = () => {
        setIsModalOpen(true);
    };
    const handleModalClose = () => {
        setIsModalOpen(false);
    };
    const handleRequestSuccess = () => {
        onRequestSuccess?.();
        setIsModalOpen(false);
    };
    return (
        <>
            <div className="flex items-center justify-between gap-4 mb-6">
                <div className="flex-1 max-w-md">
                    <SearchInput
                        value={searchValue}
                        onChange={handleSearchChange}
                        placeholder={searchPlaceholder}
                    />
                </div>
                <Button
                    onClick={handleNewRequest}
                    variant="gradient"
                    size="md"
                    className="flex items-center gap-2 whitespace-nowrap"
                >
                    <Plus size={16} />
                    New Leave Request
                </Button>
            </div>
            <LeaveRequestModal
                isOpen={isModalOpen}
                onClose={handleModalClose}
                onSuccess={handleRequestSuccess}
            />
        </>
    );
};
