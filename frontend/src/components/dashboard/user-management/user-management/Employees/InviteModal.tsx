import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { API_BASE } from '@/api';
import { getAccessToken } from '@/utils/auth';

interface Group {
    id: number;
    name: string;
}

interface InviteModalProps {
    isOpen: boolean;
    onClose: () => void;
    groups?: Group[];
    onInviteSent?: () => void;
}

export default function InviteModal({ isOpen, onClose, groups = [], onInviteSent }: InviteModalProps) {
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

    // Map selected groups to backend role
    const mapGroupsToRole = (selectedGroups: number[]): string => {
        // Group ID to role mapping based on the groups array
        const groupRoleMap: { [key: number]: string } = {
            1: 'Tenant Owner', // Admin group
            2: 'Manager',      // Manager group
            3: 'Employee',     // Employee group
        };

        // If multiple groups selected, use highest priority role
        const rolePriority = ['Tenant Owner', 'Manager', 'Employee'];

        for (const role of rolePriority) {
            if (selectedGroups.some(groupId => groupRoleMap[groupId] === role)) {
                return role;
            }
        }

        return 'Employee'; // Default fallback
    };

    const handleSendInvite = async () => {
        if (!email.trim()) {
            alert('Please enter an email address');
            return;
        }

        if (selectedGroups.length === 0) {
            alert('Please select at least one group');
            return;
        }

        const token = getAccessToken();
        if (!token) {
            alert('You must be logged in to send invitations');
            return;
        }

        const role = mapGroupsToRole(selectedGroups);

        setIsLoading(true);
        try {
            const response = await fetch(`${API_BASE}/invite-member/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`,
                },
                body: JSON.stringify({
                    email: email.trim(),
                    role: role
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Success
                setEmail('');
                setSelectedGroups([]);
                onClose();
                alert('Invitation sent successfully!');
                onInviteSent?.(); // Call the callback to refresh the invites list
            } else {
                // Handle backend error responses
                const errorMessage = data.error || data.message || 'Failed to send invitation';
                alert(`Error: ${errorMessage}`);
            }
        } catch (error) {
            console.error('Error sending invite:', error);
            alert('Network error. Please check your connection and try again.');
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
