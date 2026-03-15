/**
 * InviteModal
 * -----------
 * Invite a new member to the tenant.
 *
 * Key changes from the original:
 * - Role selector is driven by the access matrix (invitableRoles) rather than
 *   a hardcoded group-ID map.
 * - The 'Manager' legacy value is gone; the full ROLE_CHOICES list is used.
 * - The inviting user can only offer roles up to their own invite ceiling.
 */

import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { API_BASE } from '@/api';
import { authFetch } from '@/api/client';
import { useAuth } from '@/hooks/useAuth';
import type { Role } from '@/utils/permissions';

interface InviteModalProps {
    isOpen: boolean;
    onClose: () => void;
    /** Kept for backwards compat — no longer used for role mapping */
    groups?: unknown[];
    onInviteSent?: () => void;
}

export default function InviteModal({ isOpen, onClose, onInviteSent }: InviteModalProps) {
    const [email, setEmail] = useState('');
    const [selectedRole, setSelectedRole] = useState<Role>('Employee');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const { invitableRoles } = useAuth();
    const availableRoles = invitableRoles();

    const handleSendInvite = async () => {
        setError('');
        if (!email.trim()) {
            setError('Please enter an email address');
            return;
        }

        const token = localStorage.getItem('access_token');
        if (!token) {
            setError('You must be logged in to send invitations');
            return;
        }

        setIsLoading(true);
        try {
            const response = await authFetch(`${API_BASE}/invite-member/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email.trim(), role: selectedRole }),
            }, { token });

            const data = await response.json();

            if (response.ok) {
                setEmail('');
                setSelectedRole('Employee');
                onClose();
                onInviteSent?.();
            } else {
                setError(data.error || data.message || 'Failed to send invitation');
            }
        } catch {
            setError('Network error. Please check your connection and try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleCancel = () => {
        setEmail('');
        setSelectedRole('Employee');
        setError('');
        onClose();
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Invite Member">
            <div className="space-y-6">
                {/* Email field */}
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

                {/* Role selector */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                        Role
                    </label>
                    {availableRoles.length === 0 ? (
                        <p className="text-sm text-gray-500">
                            You do not have permission to invite members.
                        </p>
                    ) : (
                        <div className="flex flex-wrap gap-2">
                            {availableRoles.map((role) => (
                                <button
                                    key={role}
                                    type="button"
                                    onClick={() => setSelectedRole(role)}
                                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                                        selectedRole === role
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                                >
                                    {role}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Error message */}
                {error && (
                    <p className="text-sm text-red-600">{error}</p>
                )}

                <div className="flex justify-end space-x-3 pt-4 border-t">
                    <Button
                        onClick={handleCancel}
                        variant="secondary"
                        disabled={isLoading}
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={handleSendInvite}
                        disabled={isLoading || availableRoles.length === 0}
                    >
                        {isLoading ? 'Sending...' : 'Send Invitation'}
                    </Button>
                </div>
            </div>
        </Modal>
    );
}
