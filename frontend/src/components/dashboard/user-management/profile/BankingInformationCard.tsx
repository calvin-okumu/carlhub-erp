import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import { useProfile } from '@/hooks/useProfile';
import { Building2, CreditCard, Hash, DollarSign, Globe } from 'lucide-react';
import Loader from '@/components/shared/Loader';

export default function BankingInformationCard() {
    const { profile, loading, error, updateProfile } = useProfile();
    const [isEditing, setIsEditing] = useState(false);
    const [bankName, setBankName] = useState('');
    const [accountNumber, setAccountNumber] = useState('');
    const [branchCode, setBranchCode] = useState('');
    const [accountType, setAccountType] = useState('');
    const [routingNumber, setRoutingNumber] = useState('');
    const [swiftCode, setSwiftCode] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    useEffect(() => {
        if (profile) {
            setBankName(profile.bank_name || '');
            setAccountNumber(profile.account_number || '');
            setBranchCode(profile.branch_code || '');
            setAccountType(profile.account_type || '');
            setRoutingNumber(profile.routing_number || '');
            setSwiftCode(profile.swift_code || '');
        }
    }, [profile]);

    const handleSave = async () => {
        try {
            await updateProfile({
                bank_name: bankName,
                account_number: accountNumber,
                branch_code: branchCode,
                account_type: accountType,
                routing_number: routingNumber,
                swift_code: swiftCode,
            });
            setIsEditing(false);
            setSuccessMessage('Banking information updated successfully');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Failed to update banking information');
        }
    };

    const handleCancel = () => {
        if (profile) {
            setBankName(profile.bank_name || '');
            setAccountNumber(profile.account_number || '');
            setBranchCode(profile.branch_code || '');
            setAccountType(profile.account_type || '');
            setRoutingNumber(profile.routing_number || '');
            setSwiftCode(profile.swift_code || '');
        }
        setIsEditing(false);
    };

    if (loading) {
        return (
            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Banking Information</h2>
                <Loader />
            </Card>
        );
    }

    if (error || !profile) {
        return (
            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Banking Information</h2>
                <div className="text-sm text-red-500">{error || "Unable to load banking information"}</div>
            </Card>
        );
    }

    return (
        <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Banking Information</h2>
                {!isEditing && (
                    <Button onClick={() => setIsEditing(true)} variant="outline" size="sm">
                        Edit
                    </Button>
                )}
            </div>

            <div className="space-y-4">
                {/* Bank Name */}
                <div className="flex items-center space-x-3">
                    <Building2 className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Bank Name"
                            value={bankName}
                            onChange={(e) => setBankName(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{bankName || 'Not specified'}</span>
                    )}
                </div>

                {/* Account Number */}
                <div className="flex items-center space-x-3">
                    <CreditCard className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Account Number"
                            value={accountNumber}
                            onChange={(e) => setAccountNumber(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{accountNumber || 'Not specified'}</span>
                    )}
                </div>

                {/* Branch Code */}
                <div className="flex items-center space-x-3">
                    <Hash className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Branch Code"
                            value={branchCode}
                            onChange={(e) => setBranchCode(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{branchCode || 'Not specified'}</span>
                    )}
                </div>

                {/* Account Type */}
                <div className="flex items-center space-x-3">
                    <DollarSign className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Select
                            value={accountType}
                            onChange={(e) => setAccountType(e.target.value)}
                            className="flex-1"
                        >
                            <option value="checking">Checking</option>
                            <option value="savings">Savings</option>
                        </Select>
                    ) : (
                        <span className="flex-1">{accountType || 'Not specified'}</span>
                    )}
                </div>

                {/* Routing Number */}
                <div className="flex items-center space-x-3">
                    <Hash className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Routing Number"
                            value={routingNumber}
                            onChange={(e) => setRoutingNumber(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{routingNumber || 'Not specified'}</span>
                    )}
                </div>

                {/* SWIFT Code */}
                <div className="flex items-center space-x-3">
                    <Globe className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="SWIFT Code"
                            value={swiftCode}
                            onChange={(e) => setSwiftCode(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{swiftCode || 'Not specified'}</span>
                    )}
                </div>
            </div>

            {isEditing && (
                <div className="flex space-x-2 mt-4">
                    <Button onClick={handleSave}>Save Changes</Button>
                    <Button variant="outline" onClick={handleCancel}>Cancel</Button>
                </div>
            )}
            {successMessage && (
                <div className="mt-4 p-2 bg-green-100 text-green-800 rounded">
                    {successMessage}
                </div>
            )}
        </Card>
    );
}