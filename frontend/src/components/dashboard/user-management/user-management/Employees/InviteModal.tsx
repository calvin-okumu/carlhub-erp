import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface Group {
    id: number;
    name: string;
}

interface InviteModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSendInvite: (email: string, groups: number[]) => void;
    groups?: Group[];
}

export default function InviteModal({ isOpen, onClose, onSendInvite, groups = [] }: InviteModalProps) {
    const [email, setEmail] = useState('');
    const [selectedGroups, setSelectedGroups] = useState<number[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleGroupToggle = (groupId: number) => {
        setSelectedGroups(prev =>
            prev.includes(groupId)
                ? prev.filter(id => id !== groupId)
                : [...prev, groupId]
        );
    };

    const handleSendInvite = async () => {
        if (!email.trim()) {
            alert('Please enter an email address');
            return;
        }

        setIsLoading(true);
        try {
            await onSendInvite(email.trim(), selectedGroups);
            setEmail('');
            setSelectedGroups([]);
            onClose();
        } catch (error) {
            console.error('Error sending invite:', error);
            alert('Failed to send invitation');
        } finally {
            setIsLoading(false);
        }
    };

    const handleCancel = () => {
        setEmail('');
        setSelectedGroups([]);
        onClose();
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Invite Member">
            <div className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email Address
                    </label>
                    <Input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter email address"
                        className="w-full"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                        Assign to Groups
                    </label>
                    <div className="flex flex-wrap gap-2">
                        {groups.map((group) => (
                            <button
                                key={group.id}
                                onClick={() => handleGroupToggle(group.id)}
                                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${selectedGroups.includes(group.id)
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                {group.name}
                            </button>
                        ))}
                        {groups.length === 0 && (
                            <p className="text-sm text-gray-500">No groups available</p>
                        )}
                    </div>
                </div>

                <div className="flex justify-end space-x-3 pt-4 border-t">
                    <Button
                        onClick={handleCancel}
                        className="bg-gray-500 text-white hover:bg-gray-600"
                        disabled={isLoading}
                        variant='secondary'
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={handleSendInvite}
                        className="bg-blue-600 text-white hover:bg-blue-700"
                        disabled={isLoading}
                    >
                        {isLoading ? 'Sending...' : 'Send Invitation'}
                    </Button>
                </div>
            </div>
        </Modal>
    );
}
