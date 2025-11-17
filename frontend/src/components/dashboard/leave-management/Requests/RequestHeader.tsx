import { Plus } from 'lucide-react';
import { useEffect, useState } from 'react';
import type { LeaveRequest } from '../../../../api/types';
import SearchInput from '../../../shared/SearchInput';
import Button from '../../../ui/Button';
import LeaveRequestModal from './LeaveRequestModal';

interface RequestHeaderProps {
    onSearchChange: (value: string) => void;
    onRequestSuccess?: () => void;
    searchPlaceholder?: string;
    onCreateRequest?: (openModal: () => void) => void;
    editingRequest?: LeaveRequest | null;
    onEditClose?: () => void;
}

export const RequestHeader = ({
    onSearchChange,
    onRequestSuccess,
    searchPlaceholder = "Search leave requests...",
    onCreateRequest,
    editingRequest,
    onEditClose
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

    return (
        <>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between p-4 bg-white/60 backdrop-blur border rounded-xl shadow-sm mb-6">
                <div className="flex-1 max-w-md">
                    <SearchInput
                        value={searchValue}
                        onChange={handleSearchChange}
                        placeholder={searchPlaceholder}
                    />
                </div>

                <Button
                    onClick={() => setIsModalOpen(true)}
                    variant="gradient"
                    size="md"
                    className="flex items-center gap-2 whitespace-nowrap shadow-sm"
                >
                    <Plus size={16} />
                    Request Leave
                </Button>
            </div>

            <LeaveRequestModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSuccess={() => {
                    onRequestSuccess?.();
                    setIsModalOpen(false);
                }}
            />

            {editingRequest && (
                <LeaveRequestModal
                    isOpen={!!editingRequest}
                    onClose={onEditClose}
                    onSuccess={() => {
                        onRequestSuccess?.();
                        onEditClose?.();
                    }}
                    editingRequest={editingRequest}
                />
            )}
        </>
    );
};
