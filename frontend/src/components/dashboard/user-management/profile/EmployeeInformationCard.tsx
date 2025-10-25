import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { useProfile } from '@/hooks/useProfile';
import { IdCard, Hash, Calendar } from 'lucide-react';
import Loader from '@/components/shared/Loader';

export default function EmployeeInformationCard() {
    const { profile, loading, error, updateProfile } = useProfile();
    const [isEditing, setIsEditing] = useState(false);
    const [idNumber, setIdNumber] = useState('');
    const [employeeNumber, setEmployeeNumber] = useState('');
    const [taxNumber, setTaxNumber] = useState('');
    const [birthday, setBirthday] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [errorMessage, setErrorMessage] = useState('');

    useEffect(() => {
        if (profile) {
            setIdNumber(profile.employee_id || '');
            setEmployeeNumber(profile.employee_number || '');
            setTaxNumber(profile.tax_number || '');
            setBirthday(profile.hire_date || '');
        }
    }, [profile]);

    const handleSave = async () => {
        try {
            await updateProfile({
                employee_id: idNumber,
                employee_number: employeeNumber,
                tax_number: taxNumber,
                hire_date: birthday,
            });
            setIsEditing(false);
            setSuccessMessage('Employee information updated successfully');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (err) {
            setErrorMessage('Unable to update employee information. Please try again.');
            setTimeout(() => setErrorMessage(''), 5000);
        }
    };

    const handleCancel = () => {
        if (profile) {
            setIdNumber(profile.employee_id || '');
            setEmployeeNumber(profile.employee_number || '');
            setTaxNumber(profile.tax_number || '');
            setBirthday(profile.hire_date || '');
        }
        setIsEditing(false);
    };

    if (loading) {
        return (
            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Employee Information</h2>
                <Loader />
            </Card>
        );
    }

    if (error || !profile) {
        return (
            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Employee Information</h2>
                <div className="text-sm text-red-500">{error || "Unable to load employee information"}</div>
            </Card>
        );
    }

    return (
        <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Employee Information</h2>
                {!isEditing && (
                    <Button onClick={() => setIsEditing(true)} variant="outline" size="sm">
                        Edit
                    </Button>
                )}
            </div>

            <div className="space-y-4">
                {/* ID Number */}
                <div className="flex items-center space-x-3">
                    <IdCard className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="ID Number"
                            value={idNumber}
                            onChange={(e) => setIdNumber(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{idNumber || 'Not specified'}</span>
                    )}
                </div>

                {/* Employee Number */}
                <div className="flex items-center space-x-3">
                    <Hash className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Employee Number"
                            value={employeeNumber}
                            onChange={(e) => setEmployeeNumber(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{employeeNumber || 'Not specified'}</span>
                    )}
                </div>

                {/* Tax Number */}
                <div className="flex items-center space-x-3">
                    <Hash className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Tax Number"
                            value={taxNumber}
                            onChange={(e) => setTaxNumber(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{taxNumber || 'Not specified'}</span>
                    )}
                </div>

                {/* Hire Date */}
                <div className="flex items-center space-x-3">
                    <Calendar className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="date"
                            value={birthday}
                            onChange={(e) => setBirthday(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{birthday ? new Date(birthday).toLocaleDateString() : 'Not specified'}</span>
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
            {errorMessage && (
                <div className="mt-4 p-2 bg-red-100 text-red-800 rounded">
                    {errorMessage}
                </div>
            )}
        </Card>
    );
}
