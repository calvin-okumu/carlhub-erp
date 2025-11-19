import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Eye, EyeOff, Check, X } from 'lucide-react';
import { changePassword } from '@/api/auth';
import { getAccessToken } from '@/utils/auth';

interface PasswordForm {
    current: string;
    new: string;
    confirm: string;
}

export default function PasswordChangeCard() {
    const [passwordForm, setPasswordForm] = useState<PasswordForm>({
        current: '',
        new: '',
        confirm: '',
    });
    const [showCurrent, setShowCurrent] = useState(false);
    const [showNew, setShowNew] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);

    const handleChangePassword = async () => {
        const { current, new: newPass, confirm } = passwordForm;

        if (!current || !newPass || !confirm) {
            alert('All password fields are required.');
            return;
        }
        if (newPass !== confirm) {
            alert('Passwords do not match.');
            return;
        }

        try {
            const token = getAccessToken();
            if (!token) {
                throw new Error("No access token found. Please log in.");
            }
            await changePassword(token, current, newPass);
            alert('Password updated successfully');
            setPasswordForm({ current: '', new: '', confirm: '' });
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Failed to change password');
        }
    };

    const validatePassword = (password: string) => {
        return {
            minLength: password.length >= 8,
            hasLowercase: /[a-z]/.test(password),
            hasNumber: /\d/.test(password),
            hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(password),
        };
    };

    const newPasswordValidation = validatePassword(passwordForm.new);

    return (
        <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Change Password</h3>

            <div className="space-y-4">
                {/* Current Password */}
                <div className="relative">
                    <Input
                        type={showCurrent ? 'text' : 'password'}
                        placeholder="Current Password"
                        value={passwordForm.current}
                        onChange={(e) =>
                            setPasswordForm((prev) => ({ ...prev, current: e.target.value }))
                        }
                    />
                    <button
                        type="button"
                        onClick={() => setShowCurrent(!showCurrent)}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2"
                    >
                        {showCurrent ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                </div>

                {/* New Password */}
                <div className="relative">
                    <Input
                        type={showNew ? 'text' : 'password'}
                        placeholder="New Password"
                        value={passwordForm.new}
                        onChange={(e) =>
                            setPasswordForm((prev) => ({ ...prev, new: e.target.value }))
                        }
                    />
                    <button
                        type="button"
                        onClick={() => setShowNew(!showNew)}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2"
                    >
                        {showNew ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                </div>

                {/* Password Specifications */}
                {passwordForm.new && (
                    <div className="text-sm space-y-1">
                        <div className={`flex items-center ${newPasswordValidation.minLength ? 'text-green-600' : 'text-red-600'}`}>
                            {newPasswordValidation.minLength ? <Check className="h-3 w-3 mr-1" /> : <X className="h-3 w-3 mr-1" />}
                            Minimum 8 characters
                        </div>
                        <div className={`flex items-center ${newPasswordValidation.hasLowercase ? 'text-green-600' : 'text-red-600'}`}>
                            {newPasswordValidation.hasLowercase ? <Check className="h-3 w-3 mr-1" /> : <X className="h-3 w-3 mr-1" />}
                            At least one lowercase letter
                        </div>
                        <div className={`flex items-center ${newPasswordValidation.hasNumber ? 'text-green-600' : 'text-red-600'}`}>
                            {newPasswordValidation.hasNumber ? <Check className="h-3 w-3 mr-1" /> : <X className="h-3 w-3 mr-1" />}
                            At least one number
                        </div>
                        <div className={`flex items-center ${newPasswordValidation.hasSpecial ? 'text-green-600' : 'text-red-600'}`}>
                            {newPasswordValidation.hasSpecial ? <Check className="h-3 w-3 mr-1" /> : <X className="h-3 w-3 mr-1" />}
                            At least one special character
                        </div>
                    </div>
                )}

                {/* Confirm Password */}
                <div className="relative">
                    <Input
                        type={showConfirm ? 'text' : 'password'}
                        placeholder="Confirm New Password"
                        value={passwordForm.confirm}
                        onChange={(e) =>
                            setPasswordForm((prev) => ({ ...prev, confirm: e.target.value }))
                        }
                    />
                    <button
                        type="button"
                        onClick={() => setShowConfirm(!showConfirm)}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2"
                    >
                        {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                </div>
            </div>

            <div className="flex space-x-2 mt-4">
                <Button onClick={handleChangePassword} className="flex-1">
                    Save Changes
                </Button>
                <Button variant="secondary" className="flex-1">
                    Cancel
                </Button>
            </div>
        </Card>
    );
}
